import base64
import errno
import math
import os
import subprocess
from typing import Optional

from hera.image import ImagePullPolicy
from hera.task import Task
from hera.workflow import Workflow
from hera.workflow_service import WorkflowService
from hera.resources import Resources
from hera.toleration import GPUToleration

from kubernetes import client, config


#token_string = subprocess.check_output("argo auth token", stderr=subprocess.STDOUT, shell=True)
#my_token = token_string.decode('UTF-8').replace('Bearer ', '').strip('\n')


# This can be used when you have your own custom image
# Image_pull_policy is set to Never because on localhost when you test
# you don't need to pull the image
def get_sa_token(service_account: str, namespace: str = "default", config_file: Optional[str] = None):
    """Get ServiceAccount token using kubernetes config.
     Parameters
    ----------
    service_account: str
        The service account to authenticate from.
    namespace: str = 'default'
        The K8S namespace the workflow service submits workflows to. This defaults to the `default` namespace.
    config_file: Optional[str] = None
        The path to k8s configuration file.
     Raises
    ------
    FileNotFoundError
        When the config_file can not be found.
    """
    if config_file is not None and not os.path.isfile(config_file):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), config_file)

    config.load_kube_config(config_file=config_file)
    v1 = client.CoreV1Api()
    secret_name = v1.read_namespaced_service_account(service_account, namespace).secrets[0].name
    sec = v1.read_namespaced_secret(secret_name, namespace).data
    return base64.b64decode(sec["token"]).decode()

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]



token = get_sa_token('argo', namespace='argo')

ws = WorkflowService(host='argo.dsci.xilis.tools', verify_ssl=False, token=token)
w = Workflow('generic-gpu-test', ws, namespace="argo", service_account_name="argo-dsci")

#task_resource_request = Resources(min_mem="25Gi")

def do_nvidia_smi():
    import os
    print(f'This is a task that uses GPUs! CUDA info:\n{os.popen("nvidia-smi").read()}')

t = Task(
    f'pipeline-kevin-nvidia-smi-test',
    do_nvidia_smi,
    image='horovod/horovod:0.22.1',
    image_pull_policy=ImagePullPolicy.Always,
    node_selectors={'node.kubernetes.io/instance-type': 'p3.2xlarge'},
    resources=Resources(gpus=1),
    tolerations=[GPUToleration]
)

w.add_task(t)
w.create()


