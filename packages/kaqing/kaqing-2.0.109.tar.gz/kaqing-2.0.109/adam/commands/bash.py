from adam.commands.command import Command
from adam.utils_k8s.cassandra_clusters import CassandraClusters
from adam.utils_k8s.cassandra_nodes import CassandraNodes
from adam.pod_exec_result import PodExecResult
from adam.repl_state import BashSession, ReplState, RequiredState
from adam.utils_repl.automata_completer import AutomataCompleter
from adam.utils_repl.state_machine import StateMachine

class Bash(Command):
    COMMAND = 'bash'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(Bash, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return Bash.COMMAND

    def required(self):
        return RequiredState.CLUSTER_OR_POD

    def run(self, cmd: str, s0: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, s0)

        state, args = self.apply_state(args, s0, args_to_check=2)
        if not self.validate_state(state):
            return state

        if state.in_repl:
            if s0.sts != state.sts or s0.pod != state.pod:
                r = self.exec_with_dir(state, args)
            else:
                r = self.exec_with_dir(s0, args)

            if not r:
                state.exit_bash()

                return 'inconsistent pwd'

            return r
        else:
            command = ' '.join(args)

            if state.pod:
                CassandraNodes.exec(state.pod, state.namespace, command, show_out=True)
            elif state.sts:
                CassandraClusters.exec(state.sts, state.namespace, command, action='bash', show_out=True)

            return state

    def exec_with_dir(self, state: ReplState, args: list[str]) -> list[PodExecResult]:
        session_just_created = False
        if not args:
            session_just_created = True
            session = BashSession(state.device)
            state.enter_bash(session)

        if state.bash_session:
            if args != ['pwd']:
                if args:
                    args.append('&&')
                args.extend(['pwd', '>', f'/tmp/.qing-{state.bash_session.session_id}'])

            if not session_just_created:
                if pwd := state.bash_session.pwd(state):
                    args = ['cd', pwd, '&&'] + args

        command = ' '.join(args)

        rs = []

        if state.pod:
            rs = [CassandraNodes.exec(state.pod, state.namespace, command,
                                      show_out=not session_just_created, shell='bash')]
        elif state.sts:
            rs = CassandraClusters.exec(state.sts, state.namespace, command, action='bash',
                                        show_out=not session_just_created, shell='bash')

        return rs

    def completion(self, state: ReplState):
        if state.pod or state.sts:
            return {Bash.COMMAND: AutomataCompleter(BashStateMachine())}

        return {}

    def help(self, _: ReplState):
        return f'{Bash.COMMAND} [bash-commands]\t run bash on the Cassandra nodes'

BASH_SPEC = [
    # <command> ::= <simple_command> | <pipeline> | <conditional_command>
    # <simple_command> ::= <word> <argument>* <redirection>*
    # <pipeline> ::= <command> '|' <command>
    # <conditional_command> ::= <command> '&&' <command> | <command> '||' <command>
    # <word> ::= <letter> <letter_or_digit>*
    # <argument> ::= <word>
    # <redirection> ::= '>' <filename> | '<' <filename>
    # <filename> ::= <word>
    # <letter> ::= 'a' | 'b' | ... | 'z' | 'A' | 'B' | ... | 'Z'
    # <digit> ::= '0' | '1' | ... | '9'
    # <letter_or_digit> ::= <letter> | <digit>

    '                                > word           > word',
    'word                            > word           > word                                ^ |,>,2>,<,&,&&,||',
    '-                               > pipe           > word_pipe',
    '-                               > _rdr0_         > word_rdr0',
    '-                               > _rdr1_         > word_rdr1',
    '-                               > _rdr2_         > word_rdr2',
    '-                               > &              > word_bg                             ^ |,>,2>,<,&,&&,||',
    '-                               > &&|_or_        > word',
    'word_a                          > word           > word',
    'word_pipe                       > word           > word',
    'word_rdr0                       > word           > word_rdr0_f',
    'word_rdr1                       > word           > word_rdr1_f',
    'word_rdr2                       > word           > word_rdr2_f',
    'word_rdr1_f                     > pipe           > word_pipe                           ^ |,2>,<,&,&&,||',
    '-                               > _rdr2_         > word_rdr2',
    '-                               > _rdr0_         > word_rdr0',
    'word_rdr2_f                     > pipe           > word_pipe                           ^ |,<,&,&&,||',
    '-                               > _rdr0_         > word_rdr0',
    '-                               > &              > word_bg                             ^ |,>,2>,<,&,&&,||',
    '-                               > &&|_or_        > word',
    'word_rdr0_f                     > pipe           > word_pipe                           ^ |,&,&&,||',
    '-                               > &              > word_bg                             ^ |,>,2>,<,&,&&,||',
    '-                               > &&|_or_        > word',
    'word_bg                         > &&|_or_        >                                     ^ &&,||',
]

BASH_KEYWORDS = [
    '&',
    '&&',
    '|',
    '||',
    '>',
    '2>',
    '>>',
    '<'
]
class BashStateMachine(StateMachine[str]):
    def spec(self) -> str:
        return BASH_SPEC

    def keywords(self) -> list[str]:
        return BASH_KEYWORDS