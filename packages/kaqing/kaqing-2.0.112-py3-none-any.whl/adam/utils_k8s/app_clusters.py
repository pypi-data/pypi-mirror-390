from concurrent.futures import ThreadPoolExecutor
import sys
from typing import TypeVar

from adam.utils_k8s.app_pods import AppPods
from adam.pod_exec_result import PodExecResult
from adam.utils import log2
from adam.utils_k8s.pods import Pods
from .kube_context import KubeContext

T = TypeVar('T')

# utility collection on app clusters; methods are all static
class AppClusters:
    def exec(pods: list[str], namespace: str, command: str, action: str = 'action',
             max_workers=0, show_out=True, on_any = False, shell = '/bin/sh', background = False) -> list[PodExecResult]:
        def body(executor: ThreadPoolExecutor, pod: str, namespace: str, show_out: bool):
            if executor:
                return executor.submit(AppPods.exec, pod, namespace, command, False, False, shell, background)

            return AppPods.exec(pod, namespace, command, show_out=show_out, background=background)

        def post(result, show_out: bool):
            if KubeContext.show_out(show_out):
                print(result.command)
                if result.stdout:
                    print(result.stdout)
                if result.stderr:
                    log2(result.stderr, file=sys.stderr)

            return result

        return Pods.on_pods(pods, namespace, body, post=post, action=action, max_workers=max_workers, show_out=show_out, on_any=on_any, background=background)