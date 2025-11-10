from adam.commands.command import Command
from adam.commands.postgres.postgres_utils import pg_database_names
from adam.commands.postgres.postgres_context import PostgresContext
from adam.utils_k8s.app_pods import AppPods
from adam.utils_k8s.cassandra_clusters import CassandraClusters
from adam.utils_k8s.kube_context import KubeContext
from adam.utils_k8s.statefulsets import StatefulSets
from adam.repl_state import ReplState
from adam.utils import log2
from adam.apps import Apps

class Cd(Command):
    COMMAND = 'cd'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(Cd, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return Cd.COMMAND

    def required(self):
        return ReplState.NON_L

    def run(self, cmd: str, state: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        if not self.validate_state(state):
            return state

        if len(args) < 2:
            return state

        arg = args[1]
        for dir in arg.split('/'):
            if state.device == ReplState.P:
                if dir == '':
                    state.pg_path = None
                else:
                    context: PostgresContext = PostgresContext.apply(state.namespace, state.pg_path, arg=dir)
                    # patch up state.namespace from pg cd
                    if not state.namespace and context.namespace:
                        state.namespace = context.namespace
                    state.pg_path = context.path()
            elif state.device == ReplState.A:
                if dir == '':
                    state.app_env = None
                    state.app_app = None
                    state.app_pod = None
                elif dir == '..':
                    if state.app_pod:
                        state.app_pod = None
                    elif state.app_app:
                        state.app_app = None
                    else:
                        state.app_env = None
                else:
                    if state.app_app:
                        state.app_pod = dir
                    elif not state.app_env:
                        tks = dir.split('@')
                        if len(tks) > 1:
                            state.namespace = tks[1]

                        state.app_env = dir.split('@')[0]
                    else:
                        state.app_app = dir
            elif state.device == ReplState.L:
                pass
            else:
                if dir == '':
                    state.sts = None
                    state.pod = None
                elif dir == '..':
                    if state.pod:
                        state.pod = None
                    else:
                        state.sts = None
                else:
                    if not state.sts:
                        ss_and_ns = dir.split('@')
                        state.sts = ss_and_ns[0]
                        if len(ss_and_ns) > 1:
                            state.namespace = ss_and_ns[1]
                    elif not state.pod:
                        p, _ = KubeContext.is_pod_name(dir)
                        if p:
                            state.pod = p
                        else:
                            names = CassandraClusters.pod_names_by_host_id(state.sts, state.namespace);
                            if dir in names:
                                state.pod = names[dir]
                            else:
                                log2('Not a valid pod name or host id.')

        return state

    def completion(self, state: ReplState):
        if state.device == ReplState.P:
            pg: PostgresContext = PostgresContext.apply(state.namespace, state.pg_path) if state.pg_path else None
            if pg and pg.db:
                return {Cd.COMMAND: {'..': None}}
            elif pg and pg.host:
                return {Cd.COMMAND: {'..': None} | {p: None for p in pg_database_names(state.namespace, pg.path())}}
            else:
                return {Cd.COMMAND: {p: None for p in PostgresContext.hosts(state.namespace)}}
        elif state.device == ReplState.A:
            if state.app_app:
                return {Cd.COMMAND: {'..': None} | {pod: None for pod in AppPods.pod_names(state.namespace, state.app_env, state.app_app)}}
            elif state.app_env:
                return {Cd.COMMAND: {'..': None} | {app[0].split('-')[1]: None for app in Apps.apps(state.app_env)}}
            else:
                return {Cd.COMMAND: {'..': None} | {env[0]: None for env in Apps.envs()}}
        elif state.device == ReplState.C:
            if state.pod:
                return {Cd.COMMAND: {'..': None}}
            elif state.sts:
                return {Cd.COMMAND: {'..': None} | {p: None for p in StatefulSets.pod_names(state.sts, state.namespace)}}
            else:
                return {Cd.COMMAND: {p: None for p in StatefulSets.list_sts_names()}}

        return {}

    def help(self, _: ReplState):
        return f'{Cd.COMMAND} <path> | .. \t move around'