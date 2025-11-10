from typing import Callable
from prompt_toolkit.completion import WordCompleter

from adam.commands.command import Command
from adam.utils_k8s.app_clusters import AppClusters
from adam.utils_k8s.app_pods import AppPods
from adam.utils_k8s.cassandra_clusters import CassandraClusters
from adam.utils_k8s.cassandra_nodes import CassandraNodes
from adam.pod_exec_result import PodExecResult
from adam.repl_state import BashSession, ReplState, RequiredState
from adam.utils_k8s.statefulsets import StatefulSets
from adam.utils_repl.automata_completer import AutomataCompleter
from adam.utils_repl.state_machine import State, StateMachine
from build.lib.adam.utils_k8s.cassandra_nodes import CassandraNodes

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
        return [RequiredState.CLUSTER_OR_POD, RequiredState.APP_APP]

    def run(self, cmd: str, s0: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, s0)

        state, args = self.apply_state(args, s0, args_to_check=2)
        if not self.validate_state(state):
            return state

        if state.device == ReplState.A:
            if state.in_repl:
                if s0.app_env != state.app_env or s0.app_app != state.app_app or s0.app_pod != state.app_pod:
                    r = self.exec_with_dir(state, args)
                else:
                    r = self.exec_with_dir(s0, args)

                if not r:
                    state.exit_bash()

                    return 'inconsistent pwd'

                return r
            else:
                command = ' '.join(args)

                if state.app_pod:
                    AppPods.exec(state.app_pod, state.namespace, command, show_out=True)
                elif state.app_app:
                    AppClusters.exec(AppPods.pod_names(state.namespace, state.app_env, state.app_app), state.namespace, command, action='bash', show_out=True)

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

        if state.device == ReplState.A:
            if state.app_pod:
                rs = [AppPods.exec(state.app_pod, state.namespace, command,
                                        show_out=not session_just_created, shell='bash')]
            elif state.app_app:
                rs = AppClusters.exec(AppPods.pod_names(state.namespace, state.app_env, state.app_app), state.namespace, command, action='bash',
                                            show_out=not session_just_created, shell='bash')
        else:
            if state.pod:
                rs = [CassandraNodes.exec(state.pod, state.namespace, command,
                                        show_out=not session_just_created, shell='bash')]
            elif state.sts:
                rs = CassandraClusters.exec(state.sts, state.namespace, command, action='bash',
                                            show_out=not session_just_created, shell='bash')

        return rs

    def completion(self, state: ReplState):
        if state.device == ReplState.A and state.app_app:
            def pod_names():
                return [p for p in AppPods.pod_names(state.namespace, state.app_env, state.app_app)]

            return { Bash.COMMAND: BashCompleter(lambda: []) } | \
                   {f'@{p}': {Bash.COMMAND: BashCompleter(lambda: [])} for p in pod_names()}
        elif state.sts:
            def pod_names():
                return [p for p in StatefulSets.pod_names(state.sts, state.namespace)]

            return { Bash.COMMAND: BashCompleter(lambda: []) } | \
                   {f'@{p}': {Bash.COMMAND: BashCompleter(lambda: [])} for p in pod_names()}

        return {}

    def help(self, _: ReplState):
        return f'{Bash.COMMAND} [pod-name] [bash-commands] [&]\t run bash on the Cassandra nodes'

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

    '                                > word           > cmd                                ^ hosts',
    'cmd                             > word           > cmd                                ^ |,>,2>,<,&,&&,||',
    '-                               > pipe           > cmd_pipe',
    '-                               > _rdr0_         > cmd_rdr0',
    '-                               > _rdr1_         > cmd_rdr1',
    '-                               > _rdr2_         > cmd_rdr2',
    '-                               > &              > cmd_bg                             ^ |,>,2>,<,&,&&,||',
    '-                               > &&|_or_        > nocmd',
    'cmd_a                           > word           > cmd',
    'cmd_pipe                        > word           > cmd',
    'cmd_rdr0                        > word           > cmd_rdr0_f',
    'cmd_rdr1                        > word           > cmd_rdr1_f',
    'cmd_rdr2                        > word           > cmd_rdr2_f',
    'cmd_rdr1_f                      > pipe           > cmd_pipe                           ^ |,2>,<,&,&&,||',
    '-                               > _rdr2_         > cmd_rdr2',
    '-                               > _rdr0_         > cmd_rdr0',
    'cmd_rdr2_f                      > pipe           > cmd_pipe                           ^ |,<,&,&&,||',
    '-                               > _rdr0_         > cmd_rdr0',
    '-                               > &              > cmd_bg                             ^ |,>,2>,<,&,&&,||',
    '-                               > &&|_or_        > nocmd',
    'cmd_rdr0_f                      > pipe           > cmd_pipe                           ^ |,&,&&,||',
    '-                               > &              > cmd_bg                             ^ |,>,2>,<,&,&&,||',
    '-                               > &&|_or_        > cmd',
    'cmd_bg                          > &&|_or_        > nocmd                              ^ &&,||',
    'nocmd                           > word           > cmd',
]

BASH_KEYWORDS = [
    '&',
    '&&',
    '|',
    '||',
    '>',
    '2>',
    '>>',
    '<',
    'hosts'
]

class BashStateMachine(StateMachine[str]):
    def spec(self) -> str:
        return BASH_SPEC

    def keywords(self) -> list[str]:
        return BASH_KEYWORDS

class BashCompleter(AutomataCompleter[str]):
    def __init__(self,
                 hosts: Callable[[], list[str]],
                 debug = False):
        super().__init__(BashStateMachine(debug=debug), '', debug=debug)

        self.hosts = hosts
        self.debug = debug

    def suggestions_completer(self, state: State, suggestions: str) -> list[str]:
        if not suggestions:
            return None

        terms = []
        for suggestion in suggestions.split(','):
            terms.extend(self._terms(state, suggestion))

        return WordCompleter(terms)

    def _terms(self, _: State, word: str) -> list[str]:
        terms = []

        if word == 'hosts':
            terms.extend(self.hosts())
        else:
            terms.append(word)

        return terms