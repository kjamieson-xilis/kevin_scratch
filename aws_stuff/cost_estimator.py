import boto3
from botocore.config import Config
from collections import defaultdict


from rich.console import Console
from rich.table import Table
import datetime
import json

import pprint
PP = pprint.PrettyPrinter(indent=2)

my_config = Config(region_name='us-east-1')

ec2 = boto3.client('ec2', config=my_config)

pricing_client = boto3.client('pricing', region_name='us-east-1')

def get_products(region, instance_type):
    paginator = pricing_client.get_paginator('get_products')

    response_iterator = paginator.paginate(
        ServiceCode="AmazonEC2",
        Filters=[
            {
                'Type': 'TERM_MATCH',
                'Field': 'location',
                'Value': region
            },
            {
                'Type': 'TERM_MATCH',
                'Field': 'instanceType',
                'Value': instance_type
            },
            {
                'Type': 'TERM_MATCH',
                'Field': 'tenancy',
                'Value': 'shared'
            },
            {
                'Type': 'TERM_MATCH',
                'Field': 'preInstalledSw',
                'Value': 'NA'
            },
            {
                'Type': 'TERM_MATCH',
                'Field': 'operatingSystem',
                'Value': 'Linux'
            },
            {
                'Type': 'TERM_MATCH',
                'Field': 'capacitystatus',
                'Value': 'Used'
            }
        ],
        PaginationConfig={
            'PageSize': 100
        }
    )

    products = []
    for response in response_iterator:
        for priceItem in response["PriceList"]:
            priceItemJson = json.loads(priceItem)
            products.append(priceItemJson)

    return products

def get_ec2_price(region, instance_type):
    products = get_products(region, instance_type)
    for x in products[0]['terms']['OnDemand'].values():
        return list(x.get('priceDimensions').values())[0]['pricePerUnit']['USD']



#print(get_ec2_price('US East (N. Virginia)', 'm5.xlarge'))
#PP.pprint([x.get('product').get('attributes').get('capacitystatus') for x in products])
#exit()

def main():
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

    raw_rows = []

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
            raw_rows.append(desired_row)



    priced_rows = []
    for instance in raw_rows:
        if 'running' in instance[7]:
            hourly_price = get_ec2_price('US East (N. Virginia)', instance[4])
            new_row = instance
            new_row.append(hourly_price)
            priced_rows.append(new_row)

    hours_in_april = 720
    costed_rows = []
    for x in priced_rows:
        filt_row = [x[0], x[1], x[4], float(x[8])]
        filt_row.append(filt_row[3] * 720)
        costed_rows.append(filt_row)
    with open('costs.json', 'w') as f:
        json.dump(costed_rows, f)
    #['bill_gpu_dev', 'dsci', 'ami-09e67e426f25ce0d7', 'i-077de8533ee779dd9', 'g4dn.xlarge', '2021-12-08 02:32:48+00:00', '172.30.9.111', '[bold green]running[/bold green]', '0.5260000000']
    #console.print(table)


def monthly_by_dept(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    dept_dict = defaultdict(float)
    for x in data:
        dept_dict[x[1]] += x[4]
        if x[1] == 'tx':
            print(x)
    PP.pprint(dept_dict)
    print(sum([x for x in dept_dict.values()]))

if __name__ == '__main__':
    #main()
    monthly_by_dept('costs.json')
