import boto3
from botocore.config import Config
import datetime

import pprint
PP = pprint.PrettyPrinter(indent=2)

my_config = Config(region_name='us-east-1')

session = boto3.Session()
ec2 = session.resource('ec2')

dsci_vpc = {'Name': 'vpc-id','Values': ['vpc-02d1be40e204286ad']}

for eni in ec2.network_interfaces.filter(Filters=[dsci_vpc]):
        attachment_info = 'No attachment'
        if eni.attachment:
            if 'InstanceId' in eni.attachment:
                attachment_info = eni.attachment['InstanceId']
            else:
                attachment_info = eni.attachment['InstanceOwnerId']

        row = (
            eni.private_ip_address,
            eni.subnet_id,
            eni.subnet.cidr_block,
            attachment_info,
            eni.private_ip_addresses
        )
        PP.pprint(row)
