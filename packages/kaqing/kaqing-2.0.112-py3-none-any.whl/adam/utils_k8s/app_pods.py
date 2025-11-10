from typing import List
from kubernetes import client

from adam.config import Config
from adam.utils_k8s.pods import Pods
from adam.pod_exec_result import PodExecResult
from adam.repl_session import ReplSession

# utility collection on app pods; methods are all static
class AppPods:
    def pod_names(namespace: str, env: str, app: str):
        return [pod.metadata.name for pod in AppPods.app_pods(namespace, env, app)]

    def app_pods(namespace: str, env: str, app: str) -> List[client.V1Pod]:
        v1 = client.CoreV1Api()

        env_key = Config().get('app.env', 'c3__env-0')
        app_key = Config().get('app.app', 'c3__app-0')
        label_selector = f'applicationGroup=c3,{env_key}=0{env}0,{app_key}=0{app}0'

        return v1.list_namespaced_pod(namespace, label_selector=label_selector).items

    def exec(pod_name: str, namespace: str, command: str, show_out = True, throw_err = False, shell = '/bin/sh', background = False) -> PodExecResult:
        r = Pods.exec(pod_name, "c3-server", namespace, command, show_out = show_out, throw_err = throw_err, shell = shell, background = background)

        if r and Config().get('repl.history.push-cat-remote-log-file', True):
            if r.log_file and ReplSession().prompt_session:
                ReplSession().prompt_session.history.append_string(f'@{r.pod} cat {r.log_file}')

        return r