from adam.commands.command import Command
from adam.commands.cql.cql_utils import cassandra_table_names, run_cql
from adam.commands.postgres.postgres_context import PostgresContext
from adam.config import Config
from adam.repl_state import ReplState, RequiredState
from adam.utils import lines_to_tabular, log, log2
from adam.utils_audits import Audits

class PreviewTable(Command):
    COMMAND = 'preview'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(PreviewTable, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return PreviewTable.COMMAND

    def required(self):
        return [RequiredState.CLUSTER_OR_POD, RequiredState.PG_DATABASE, ReplState.L]

    def run(self, cmd: str, state: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        state, args = self.apply_state(args, state)
        if not self.validate_state(state):
            return state

        if not args:
            def show_tables():
                if state.device == ReplState.P:
                    pg = PostgresContext.apply(state.namespace, state.pg_path)
                    lines = [db["name"] for db in pg.tables() if db["schema"] == PostgresContext.default_schema()]
                    log(lines_to_tabular(lines, separator=','))
                elif state.device == ReplState.L:
                    log(lines_to_tabular(Audits.audit_table_names(), separator=','))
                else:
                    log(lines_to_tabular(cassandra_table_names(state), separator=','))

            if state.in_repl:
                log2('Table is required.')
                log2()
                log2('Tables:')
                show_tables()
            else:
                log2('* Table is missing.')
                show_tables()

                Command.display_help()

            return 'command-missing'

        table = args[0]

        rows = Config().get('preview.rows', 10)
        if state.device == ReplState.P:
            PostgresContext.apply(state.namespace, state.pg_path).run_sql(f'select * from {table} limit {rows}')
        elif state.device == ReplState.L:
            Audits.run_audit_query(f'select * from {table} limit {rows}')
        else:
            run_cql(state, f'select * from {table} limit {rows}', show_out=True, use_single_quotes=True, on_any=True)

        return state

    def completion(self, _: ReplState):
        return {}

    def help(self, _: ReplState):
        return f'{PreviewTable.COMMAND} TABLE\t preview table'