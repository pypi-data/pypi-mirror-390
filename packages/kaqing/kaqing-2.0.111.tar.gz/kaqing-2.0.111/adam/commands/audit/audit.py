import click

from adam.commands.audit.audit_repair_tables import AuditRepairTables
from adam.commands.audit.audit_run import AuditRun
from adam.commands.audit.show_last10 import ShowLast10
from adam.commands.audit.show_slow10 import ShowSlow10
from adam.commands.audit.show_top10 import ShowTop10
from adam.commands.audit.utils_show_top10 import show_top10_completions_for_nesting
from adam.commands.command import Command
from adam.config import Config
from adam.repl_state import ReplState
from adam.sql.sql_completer import SqlCompleter
from adam.utils import log2
from adam.utils_audits import Audits

class Audit(Command):
    COMMAND = 'audit'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(Audit, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)
        self.schema_read = False

    def command(self):
        return Audit.COMMAND

    def required(self):
        return ReplState.L

    def run(self, cmd: str, state: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        state, args = self.apply_state(args, state)
        if not self.validate_state(state):
            return state

        r = None
        if len(args) > 0:
            r = super().intermediate_run(cmd, state, args, Audit.cmd_list(), display_help=False)

        if not r or isinstance(r, str) and r == 'command-missing':
            sql = 'select * from audit order by ts desc limit 10'
            if args:
                sql = ' '.join(args)
            else:
                log2(sql)

            Audits.run_audit_query(sql)

        return state

    def completion(self, state: ReplState):
        if state.device == ReplState.L:
            if not self.schema_read:
                Config().wait_log(f'Inspecting audit database schema...')
                self.schema_read = True
                # warm up the caches first time when l: drive is accessed
                Audits.audit_table_names()
                Audits.audit_column_names()
                Audits.audit_column_names(partition_cols_only=True)

            return super().completion(state) | show_top10_completions_for_nesting() | SqlCompleter(
                lambda: Audits.audit_table_names(),
                columns=lambda table: Audits.audit_column_names(),
                partition_columns=lambda table: Audits.audit_column_names(partition_cols_only=True),
                variant='athena'
            ).completions_for_nesting()

        return {}

    def cmd_list():
        return [AuditRepairTables(), AuditRun(), ShowLast10(), ShowSlow10(), ShowTop10()]

    def help(self, _: ReplState):
        return f'[{Audit.COMMAND}] [<sql-statements>]\t run SQL queries on Authena audit database'

class AuditCommandHelper(click.Command):
    def get_help(self, ctx: click.Context):
        Command.intermediate_help(super().get_help(ctx), Audit.COMMAND, Audit.cmd_list(), show_cluster_help=False)