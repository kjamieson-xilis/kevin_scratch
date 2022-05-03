import base64
import errno
import math
import os
import subprocess
from typing import Optional

from hera.artifact import InputArtifact, OutputArtifact
from hera.input import InputFrom
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

def writer():
    import json

    with open('/file', 'w+') as f:
        for i in range(10):
            f.write(f'{json.dumps(i)}\n')


def fanout():
    import json
    import sys

    indices = []
    with open('/file', 'r') as f:
        for line in f.readlines():
            indices.append({'i': line})
    json.dump(indices, sys.stdout)


def consumer(i: int):
    print(i)

token = get_sa_token('argo', namespace='argo')

ws = WorkflowService(host='argo.dsci.xilis.tools', verify_ssl=False, token=token)
w = Workflow('hera-artifact-test', ws, namespace="argo", service_account_name="argo-dsci")
w_t = Task('writer', writer, output_artifacts=[OutputArtifact(name='test', path='/file')])
f_t = Task(
    'fanout',
    fanout,
    input_artifacts=[InputArtifact(from_task='writer', artifact_name='test', name='test', path='/file')],
)
c_t = Task('consumer', consumer, input_from=InputFrom(name='fanout', parameters=['i']))
w_t >> f_t >> c_t
w.add_tasks(w_t, f_t, c_t)
w.create()
