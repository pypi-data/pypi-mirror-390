from adam.commands.cql.cql_utils import cassandra_table_names
from adam.config import Config
from adam.repl_state import ReplState
from adam.sql.sql_completer import SqlCompleter

def cql_completions(state: ReplState) -> dict[str, any]:
    ps = Config().get('cql.alter-tables.gc-grace-periods', '3600,86400,864000,7776000').split(',')
    return {
        'describe': {
            'keyspaces': None,
            'table': {t: None for t in cassandra_table_names(state)},
            'tables': None},
    } | SqlCompleter(lambda: cassandra_table_names(state), table_props=lambda: {
        'GC_GRACE_SECONDS': ps
    }, variant='cql').completions_for_nesting()