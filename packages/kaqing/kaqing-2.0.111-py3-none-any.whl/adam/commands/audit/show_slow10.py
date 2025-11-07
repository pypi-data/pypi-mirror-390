from adam.commands.audit.utils_show_top10 import extract_limit_and_duration
from adam.commands.command import Command
from adam.repl_state import ReplState
from adam.utils import log2
from adam.utils_audits import Audits

class ShowSlow10(Command):
    COMMAND = 'show slow'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(ShowSlow10, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return ShowSlow10.COMMAND

    def required(self):
        return ReplState.L

    def run(self, cmd: str, state: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        state, args = self.apply_state(args, state)
        if not self.validate_state(state):
            return state

        limit, date_condition = extract_limit_and_duration(args)

        query = '\n    '.join([
            "SELECT * FROM audit",
            f"WHERE drive <> 'z' and ({date_condition})",
            f"ORDER BY CAST(duration AS REAL) DESC LIMIT {limit};"])
        log2(query)
        log2()
        Audits.run_audit_query(query)

        return state

    def completion(self, _: ReplState):
        return {}

    def help(self, _: ReplState):
        return f'{ShowSlow10.COMMAND} [limit]\t show slow <limit> audit lines'