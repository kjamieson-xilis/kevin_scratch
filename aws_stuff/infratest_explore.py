import boto3

from pprint import PrettyPrinter
PP = PrettyPrinter(indent=2)

def vpc():
    session = boto3.Session(profile_name='infratest')
    client = session.client('ec2')
    #PP.pprint(client.describe_vpcs())
    ec2_resource = session.resource('ec2')
    my_vpc = ec2_resource.Vpc('vpc-014d901307b480427')
    response = my_vpc.describe_attribute(Attribute='enableDnsHostnames')
    PP.pprint(response)

def client_vpn():
    session = boto3.Session(profile_name='infratest')
    client = session.client('ec2')
    PP.pprint(client.describe_client_vpn_endpoints())

def main():
    session = boto3.Session(profile_name='infratest')
    client = session.client('ec2')
    vpcs = client.describe_vpcs()
    for x in vpcs.get('Vpcs'):
        print(x.get('CidrBlock'), x.get('VpcId'))

if __name__ == '__main__':
    main()
