import boto3
from botocore.config import Config
from rich.console import Console
from rich.table import Table
import datetime

import pprint
PP = pprint.PrettyPrinter(indent=2)

my_config = Config(region_name='us-east-1')

ec2 = boto3.client('ec2', config=my_config)
instances = ec2.describe_instances().get('Reservations')
#desired_fields = ['ImageId', 'InstanceId', 'InstanceType', 'KeyName', 'LaunchTime', 'PrivateIpAddress', 'State', 'VpcId']
#desired_fields = ['InstanceId', 'InstanceType', 'State']
#desired_fields = ['InstanceId']
desired_fields = ['ImageId', 'InstanceId', 'InstanceType','LaunchTime','PrivateIpAddress', 'State']

# Get the image id descriptions
image_ids = []
for instance in instances:
    details = instance.get('Instances')
    for detail in details:
        image_ids.append(detail.get('ImageId'))


image_response = ec2.describe_images(ImageIds=list(set(image_ids)))
image_id_dict = {}
for entry in image_response.get('Images'):
    image_id_dict[entry.get('ImageId')] = entry.get('Name')



console = Console()
table = Table(show_header=True)
table.add_column('Name', no_wrap=True)
table.add_column('department')
for field in desired_fields:
    table.add_column(field)

for x in instances:
    details = x.get('Instances')
    for y in details:
        # get the tags
        tags = y.get('Tags')
        name_list = [x.get('Value') for x in tags if x.get('Key') == 'Name']
        name = None
        if name_list:
            name = name_list[0]
        department = [x.get('Value') for x in tags if x.get('Key') == 'department']
        department_name = None
        if department:
            department_name = department[0]
        # Lookup the ami name
        image_name = image_id_dict.get(y.get('ImageId'))

        desired_row = [name, department_name]

        for field in desired_fields:
            field_value = y.get(field)
            if isinstance(field_value, datetime.datetime):
                field_value = str(field_value)
            if field == 'State':
                field_value = field_value.get('Name')
                if field_value == 'running':
                    field_value = '[bold green]running[/bold green]'
                elif field_value == 'stopped':
                    field_value = '[bold red]stopped[/bold red]'

            #elif isinstance(field_value, dict):
            #    field_value = str(field_value)
            desired_row.append(field_value)
        #print(f"{desired_row},")
        table.add_row(*desired_row)


console.print(table)
