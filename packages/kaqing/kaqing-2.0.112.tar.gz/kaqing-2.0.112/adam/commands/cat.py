from adam.commands.bash import Bash
from adam.commands.command import Command
from adam.repl_state import ReplState, RequiredState
from adam.utils import log2
from adam.utils_k8s.app_pods import AppPods
from adam.utils_k8s.statefulsets import StatefulSets

class Cat(Command):
    COMMAND = 'cat'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(Cat, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return Cat.COMMAND

    def required(self):
        return [RequiredState.CLUSTER_OR_POD, RequiredState.APP_APP]

    def run(self, cmd: str, state: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        state, args = self.apply_state(args, state)

        if len(args) < 1:
            if state.in_repl:
                log2('File is required.')
                log2()
            else:
                log2('* File is missing.')
                Command.display_help()

            return 'command-missing'

        return Bash().run('bash ' + cmd, state)

    def completion(self, state: ReplState):
        if state.device == ReplState.A and state.app_app:
            return super().completion(state) | \
                {f'@{p}': {Cat.COMMAND: None} for p in AppPods.pod_names(state.namespace, state.app_env, state.app_app)}
        elif state.device == ReplState.C and state.sts:
            return super().completion(state) | \
                {f'@{p}': {Cat.COMMAND: None} for p in StatefulSets.pod_names(state.sts, state.namespace)}

        return {}

    def help(self, _: ReplState):
        return f'{Cat.COMMAND} file [&]\t run cat command on the Cassandra nodes'