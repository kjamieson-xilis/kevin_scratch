import boto3
from botocore.config import Config
from collections import namedtuple, defaultdict

import pprint
PP = pprint.PrettyPrinter(indent=2)

my_config = Config(region_name='us-east-1')

ec2 = boto3.client('ec2', config=my_config)


list_of_lists = [
['bill_gpu_dev', "dsci", 'i-077de8533ee779dd9'],
['labcollector-deployed', "ops", 'i-09cc83467569aece8'],
['dmoview', "unknown", 'i-0c1105c9a86d47b23'],
['NHR-training', "cleanup", 'i-0dcc9a7608f0959f4'],
['NHR-training2', "cleanup", 'i-0571ade63f0f1df1d'],
['jupyter', "cleanup", 'i-0c0415c7dbf51ef41'],
['vpn-test', "sw", 'i-0adf3ed4b1eeee640'],
['NHR-training-p3.8x', "cleanup", 'i-0672109a21d4d98e1'],
['fluorescent-analyzer', "unknown", 'i-0192c17925ffdd94e'],
['dmoview-production', "unknown", 'i-033333f098492f584'],
['XilisHub - FrontendStack', "ops", 'i-0b89bf2db635b01fb'],
['kevin_dev', "sw", 'i-0fc2fefd0fc9b8847'],
['ml_model_server', "dsci", 'i-00e6c0bafad503d7f'],
['XilisHub-BackendStack', "ops", 'i-08cfaa51141de7cd1'],
['XilisHub-BackendStack-GPU', "ops", 'i-028bd5be58d44f962'],
['ml_model_server', "dsci", 'i-00f28a1f4a328234b'],
['XilisHub-Modelserver', "ops", 'i-073fb5365b88dfd67'],
['wbq-train-instance', "dsci", 'i-0c6d8654564077686'],
['CdkStack/ec2_instance_newbackend.xilis.tools', "ops", 'i-0f1a456f8cb681a32'],
['CdkStack/ec2_instance_ami_template', "sw", 'i-05d8d4a36614ef786'],
['CdkStack/ec2_instance_modelserver2.xilis.tools', "ops", 'i-0e35dca9480073871'],
['CdkStack/ec2_instance_modelserver3.xilis.tools', "ops", 'i-03e5d777121d293d4'],
['CdkStack/ec2_instance_modelserver4.xilis.tools', "ops", 'i-09929dbc79bd71f70'],
['CdkStack/ec2_instance_modelserver7.xilis.tools', "ops", 'i-0985af6d6ad394dba'],
['CdkStack/ec2_instance_modelserver6.xilis.tools', "ops", 'i-0d0780558cb3a6e46'],
['CdkStack/ec2_instance_modelserver5.xilis.tools', "ops", 'i-0e9490d2a600b1728'],
['CdkStack/ec2_instance_modelserver12.xilis.tools', "ops", 'i-05fbbab214d89f528'],
['CdkStack/ec2_instance_modelserver18.xilis.tools', "ops", 'i-04537417216213104'],
['CdkStack/ec2_instance_modelserver14.xilis.tools', "ops", 'i-01555e9c50087f911'],
['CdkStack/ec2_instance_modelserver10.xilis.tools', "ops", 'i-0d4a68be5b0ec00b0'],
['CdkStack/ec2_instance_modelserver19.xilis.tools', "ops", 'i-06295358c5a74a046'],
['CdkStack/ec2_instance_modelserver13.xilis.tools', "ops", 'i-0d16865d76442b8e5'],
['CdkStack/ec2_instance_modelserver16.xilis.tools', "ops", 'i-017a609ebbab43ac0'],
['CdkStack/ec2_instance_modelserver9.xilis.tools', "ops", 'i-02aab5d36e4bef40d'],
['CdkStack/ec2_instance_modelserver15.xilis.tools', "ops", 'i-02cb93806b07ce770'],
['CdkStack/ec2_instance_modelserver11.xilis.tools', "ops", 'i-0f97c1aa1a57041e0'],
['CdkStack/ec2_instance_modelserver20.xilis.tools', "ops", 'i-01caafb342055df64'],
['CdkStack/ec2_instance_modelserver17.xilis.tools', "ops", 'i-08169cb3d65eaa6d2'],
['CdkStack/ec2_instance_modelserver8.xilis.tools', "ops", 'i-087d2469dfc0f58ee'],
['download_box', "dsci", 'i-0de5ec074d02d6993'],
['hub_dev-worker-group-1-eks_asg', "sw", 'i-056319a49405aa968'],
['kevin_dev2', "sw", 'i-06b1bb6ce7dad8b07'],
['sbakhtiari_dev', "dsci", 'i-014206d7d85f540a0'],
['labcollector_deployment_test', "sw", 'i-0c16711b19600649f'],
['karpenter.sh/provisioner-name/default', "dsci", 'i-0804f1b8a1a1a6860'],
['hub_tx-0-eks_asg', "tx", 'i-0f31ed047a44f83c4'],
['labcollector_corelabs', "core", 'i-09d1ea68d9477a680'],
['mssql_linux_test', "ops", 'i-0ad062402a48ef758'],
['karpenter.sh/provisioner-name/modelserver', "dsci", 'i-0e410b862b2582733'],
['establishment_monitoring', 'ops', 'i-02b147f0f5ed3856b'],
['karpenter.sh/provisioner-name/default', "dsci", 'i-03a35f8bd7cb2ba30'],
['rmoseley_dev_gpu', "dsci", 'i-025b8be5c4e1c3abf'],
['hub_dsci-0-eks_asg', "dsci", 'i-0c0f74b8ef3247250'],
['nbaro_dev_gpu2', "dsci", 'i-012ec47efdb3eb0d0'],
['sbakhtiari_dev_gpu', "dsci", 'i-093d4b3ade05c64cd'],
['nbaro_dev_gpu3', "dsci", 'i-07b2cbf5d01d5b9f7'],
['karpenter.sh/provisioner-name/default', "tx", 'i-0a77537ef98245224'],
['karpenter.sh/provisioner-name/default', "tx", 'i-017051778075a72e3'],
['karpenter.sh/provisioner-name/default', "tx", 'i-0bafe41dea1f22cfb'],
['karpenter.sh/provisioner-name/modelserver', "dsci", 'i-099fcd9edd52e2bcf'],
['bill_gpu_dev2', "dsci", 'i-080f0bc6459043903'],
['hub_dev-worker-group-1-eks_asg', "sw", 'i-04b244677a3f67241'],
['hub_dev-worker-group-2-eks_asg', "sw", 'i-0f4c883792e5421af'],
['rmoseley_dev', "dsci", 'i-06b6cb87ac667c518'],
['nbaro_dev', "dsci", 'i-024d8cf8cdf1d7702'],
['nbaro_dev_ubuntu', "dsci", 'i-0b02aa81fcb85f025'],
['nbaro_dev_thunor', "dsci", 'i-09f45b6d8b39c194f'],
['mwheeler_dev', "sw", 'i-0b89615d56b935295'],
['labcollector_dev', "ops", 'i-0a35acf735afa7ead'],
['nbaro_dev_gpu', "dsci", 'i-03abaf6141f256a0f'],
['detectron_highmem_dev', "dsci", 'i-0d028f1e7bed30dba']
        ]

for x in list_of_lists:
    if 'unknown' in x:
        print(x)

exit()
TagTuple = namedtuple("TagTuple", "name department instance_id")
instance_tuples = []
for x in list_of_lists:
    instance = TagTuple(*x)
    instance_tuples.append(instance)

dept_dict = defaultdict(list)

for x in instance_tuples:
    dept_dict[x.department].append(x)


for dept, tuple_list in dept_dict.items():
    resources = []
    construct_tag = [
            {
                "Key": "department",
                "Value": dept,
                }
            ]
    for t in tuple_list:
        resources.append(t.instance_id)
    response = ec2.create_tags(
            Resources=resources,
            Tags=construct_tag)
    print(response)
