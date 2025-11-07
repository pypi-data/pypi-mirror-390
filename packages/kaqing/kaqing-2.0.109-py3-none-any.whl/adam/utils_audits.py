from datetime import datetime
import functools
import getpass
import time
import boto3
import requests

from adam.config import Config
from adam.utils import lines_to_tabular, log, log2
from adam.utils_net import get_my_host

class AuditMeta:
   def __init__(self, partitions_last_checked: float, cluster_last_checked: float):
      self.partitions_last_checked = partitions_last_checked
      self.cluster_last_checked = cluster_last_checked

# no state utility class
class Audits:
   PARTITIONS_ADDED = 'partitions-added'
   ADD_CLUSTERS = 'add-clusters'

   def log(cmd: str, cluster = 'NA', drive: str = 'NA', duration: float = 0.0):
      payload = {
         'cluster': cluster if cluster else 'NA',
         'ts': time.time(),
         'host': get_my_host(),
         'user': getpass.getuser(),
         'line': cmd.replace('"', '""').replace('\n', ' '),
         'drive': drive,
         'duration': duration,
      }
      audit_endpoint = Config().get("audit.endpoint", "https://4psvtaxlcb.execute-api.us-west-2.amazonaws.com/prod/")
      try:
         response = requests.post(audit_endpoint, json=payload, timeout=Config().get("audit.timeout", 10))
         if response.status_code in [200, 201]:
               Config().debug(response.text)
         else:
               log2(f"Error: {response.status_code} {response.text}")
      except requests.exceptions.Timeout as e:
         log2(f"Timeout occurred: {e}")

   def get_meta() -> AuditMeta:
      checked_in = 0.0
      cluster_last_checked = 0.0

      state, _, rs = Audits.audit_query(f'select partitions_last_checked, clusters_last_checked from meta')
      if state == 'SUCCEEDED':
         if len(rs) > 1:
            try:
               row = rs[1]['Data']
               checked_in = float(row[0]['VarCharValue'])
               cluster_last_checked = float(row[1]['VarCharValue'])
            except:
               pass

      return AuditMeta(checked_in, cluster_last_checked)

   def put_meta(action: str, meta: AuditMeta, clusters: list[str] = None):
      payload = {
         'action': action,
         'partitions-last-checked': meta.partitions_last_checked,
         'clusters-last-checked': meta.cluster_last_checked
      }
      if clusters:
         payload['clusters'] = clusters

      audit_endpoint = Config().get("audit.endpoint", "https://4psvtaxlcb.execute-api.us-west-2.amazonaws.com/prod/")
      try:
         response = requests.post(audit_endpoint, json=payload, timeout=Config().get("audit.timeout", 10))
         if response.status_code in [200, 201]:
               Config().debug(response.text)
         else:
               log2(f"Error: {response.status_code} {response.text}")
      except requests.exceptions.Timeout as e:
         log2(f"Timeout occurred: {e}")

   def find_new_clusters(cluster_last_checked: float) -> list[str]:
      dt_object = datetime.fromtimestamp(cluster_last_checked)

      # select distinct c2.name from cluster as c1 right outer join
      #     (select distinct c as name from audit where y = '1969' and m = '12' and d >= '31' or y = '1969' and m > '12' or y > '1969') as c2
      #     on c1.name = c2.name where c1.name is null
      query = '\n    '.join([
         'select distinct c2.name from cluster as c1 right outer join',
         f'(select distinct c as name from audit where {Audits.date_from(dt_object)}) as c2',
         'on c1.name = c2.name where c1.name is null'])
      log2(query)
      state, _, rs = Audits.audit_query(query)
      if state == 'SUCCEEDED':
         if len(rs) > 1:
               try:
                  return [r['Data'][0]['VarCharValue'] for r in rs[1:]]
               except:
                  pass

      return []

   @functools.lru_cache()
   def audit_table_names():
      region_name = Config().get('audit.athena.region', 'us-west-2')
      database_name = Config().get('audit.athena.database', 'audit')
      catalog_name = Config().get('audit.athena.catalog', 'AwsDataCatalog')

      athena_client = boto3.client('athena', region_name=region_name)
      paginator = athena_client.get_paginator('list_table_metadata')

      table_names = []
      for page in paginator.paginate(CatalogName=catalog_name, DatabaseName=database_name):
         for table_metadata in page.get('TableMetadataList', []):
            table_names.append(table_metadata['Name'])

      return table_names

   @functools.lru_cache()
   def audit_column_names(tables: list[str] = [], database: str = None, partition_cols_only = False):
      if not database:
         database = Config().get('audit.athena.database', 'audit')

      if not tables:
         tables = Config().get('audit.athena.tables', 'audit').split(',')

      table_names = "'" + "','".join([table.strip() for table in tables]) + "'"

      query = f"select column_name from information_schema.columns where table_name in ({table_names}) and table_schema = '{database}'"
      if partition_cols_only:
         query = f"{query} and extra_info = 'partition key'"

      _, _, rs = Audits.audit_query(query)
      if rs:
         return [row['Data'][0].get('VarCharValue') for row in rs[1:]]

      return []

   def run_audit_query(sql: str, database: str = None):
      state, reason, rs = Audits.audit_query(sql, database)

      if state == 'SUCCEEDED':
         if rs:
            column_info = rs[0]['Data']
            columns = [col.get('VarCharValue') for col in column_info]
            lines = []
            for row in rs[1:]:
                  row_data = [col.get('VarCharValue') if col else '' for col in row['Data']]
                  lines.append('\t'.join(row_data))

            log(lines_to_tabular(lines, header='\t'.join(columns), separator='\t'))
      else:
         log2(f"Query failed or was cancelled. State: {state}")
         log2(f"Reason: {reason}")

   def audit_query(sql: str, database: str = None) -> tuple[str, str, list]:
      athena_client = boto3.client('athena')

      if not database:
         database = Config().get('audit.athena.database', 'audit')

      s3_output_location = Config().get('audit.athena.output', 's3://s3.ops--audit/ddl/results')

      response = athena_client.start_query_execution(
         QueryString=sql,
         QueryExecutionContext={
               'Database': database
         },
         ResultConfiguration={
               'OutputLocation': s3_output_location
         }
      )

      query_execution_id = response['QueryExecutionId']

      while True:
         query_status = athena_client.get_query_execution(QueryExecutionId=query_execution_id)
         state = query_status['QueryExecution']['Status']['State']
         if state in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
               break
         time.sleep(1)

      if state == 'SUCCEEDED':
         results_response = athena_client.get_query_results(QueryExecutionId=query_execution_id)
         if results_response['ResultSet']['Rows']:
            return (state, None, results_response['ResultSet']['Rows'])

         return (state, None, [])
      else:
         return (state, query_status['QueryExecution']['Status'].get('StateChangeReason'), [])

   def date_from(dt_object: datetime):
        y = dt_object.strftime("%Y")
        m = dt_object.strftime("%m")
        d = dt_object.strftime("%d")

        return f"y = '{y}' and m = '{m}' and d >= '{d}' or y = '{y}' and m > '{m}' or y > '{y}'"