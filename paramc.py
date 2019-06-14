#!/usr/bin/env python3
import sys
import os
import json
import yaml
import argparse
import boto3
import jinja2
import http.client

from botocore.client import ClientError


allowed_action = ['CREATE', 'UPDATE', 'VERIFY', 'BOTO']

def read_cfg(inputfile):
    try:
        stream = open(inputfile, 'r')
    except FileNotFoundError:
        print("can''t open source file %s" % inputfile)
        sys.exit(1)
    datamap = yaml.safe_load(stream)
    stream.close()
    # print('json_obj =', datamap)
    return datamap

def write_json(outputfile, data, KeyName, ValueName):
    try:
        output=open(outputfile, 'w')
    except FileNotFoundError:
        print("can''t open destiantion file %s " % outputfile)
        sys.exit(2)
    OutputParam = [ {KeyName: paramm, ValueName: data[paramm]} for paramm in data ]
    json.dump(OutputParam, output)
    output.flush()
    output.close()
    # print('OutputParam =', OutputParam)
    return OutputParam

def run(cmd):
    return os.popen(cmd).read()

def stack_exists(cf_client, stack_name):
    stacks = cf_client.list_stacks()['StackSummaries']
    for stack in stacks:
        if stack['StackStatus'] == 'DELETE_COMPLETE':
            continue
        if stack_name == stack['StackName']:
            return True
    return False

class s3_bucket:
    "class for workng with s3 bucket"
    def __init__(self, backet_name):
        # del first_bucket_name first_
        self.__s3 = boto3.resource('s3')
        self.backet_name = backet_name
        try:
            self.__s3.meta.client.head_bucket(Bucket=backet_name)
        except ClientError:
            self.__create_bucket(self.backet_name)
        return

    def __create_bucket(self, bucket_name):
        # del s3_connection
        s3_client =  self.__s3.meta.client
        session = boto3.session.Session()
        current_region = session.region_name
        # bucket_name = create_bucket_name(bucket_prefix)
        s3_client.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={
            'LocationConstraint': current_region})
        print('create_bucket: ',bucket_name, current_region)
        return

    def upload_obj(self, bucket, file, key):
        try:
            cf_file=open(file, 'rb')
        except FileNotFoundError:
            print("can''t open destiantion file %s " % cf_file)
            sys.exit(2)
        self.__s3.Bucket(bucket).put_object(Key=key, Body=cf_file)

    def get_obj_url(self, s3_bucket, s3_key):
        bucket_location = self.__s3.meta.client.get_bucket_location(Bucket=s3_bucket)
        return "https://{1}.s3.{0}.amazonaws.com/{2}".format(bucket_location['LocationConstraint'], s3_bucket, s3_key)

    def del_obj(self, obj_key):
        obj = self.__s3.Object(self.backet_name, obj_key)
        return obj.delete()


def main():
    parser = argparse.ArgumentParser(description='Programm to work with AWS')
    parser.add_argument("-s","--stack", help="STACK name", type=str)
    parser.add_argument('-a','--action', help='what to do CREATE/UPDATE/BOTO')
    parser.add_argument('-i','--input', help='file with parameters and tags')
    parser.add_argument('-cf','--cloud-formation', help='file with parameters and tags')
    parser.add_argument('-cfk','--cloud-formation-key', help='file with parameters and tags')
    parser.add_argument('-s3','--s3', help='file with parameters and tags')
    args = parser.parse_args()

    sys.stdout.flush()

    if args.action not in allowed_action:
        print('wrong action - we process only', allowed_action)
        sys.exit()

    print("script will convert %s into parameters.json and tags.json for ENVIRONMENT ... and %s STACK %s" \
        % (args.input, args.action, args.stack) )

    cfg = read_cfg(args.input)
    print('cfg = ', cfg)

    parameters = cfg["parameters"]
    tags = cfg["tags"]
    tags['STACK'] = args.stack
    print('parameters = ', parameters)
    print('tags = ', tags)

    jParameters = write_json("parameters.json",parameters,"ParameterKey", "ParameterValue")
    jTags = write_json("tags.json",tags,"Key", "Value")

    s3 = s3_bucket(args.s3)
    s3.del_obj(args.cloud_formation_key)
    s3.upload_obj(args.s3, args.cloud_formation, args.cloud_formation_key)
    object_url = s3.get_obj_url(args.s3, args.cloud_formation_key)

    cf_client = boto3.client('cloudformation')
    # validate templatee
    print('ec2.yaml validate = ', cf_client.validate_template(TemplateURL=object_url))
    print('stdout = ', run("aws cloudformation validate-template --template-body file://ec2.yaml"))

    if args.action == "CREATE":
        cmd = "aws cloudformation create-stack --stack-name " + args.stack + \
              " --template-body file://ec2.yaml --parameters file://parameters.json --tags file://tags.json"
        # stdout =
        print('Creating STACK = ', run(cmd))
    if args.action == "UPDATE":
        cmd = "aws cloudformation update-stack --stack-name " + args.stack + \
              " --template-body file://ec2.yaml --parameters file://parameters.json --tags file://tags.json"
        # stdout = run(cmd)
        print('stdout = ', run(cmd))
    if args.action == "BOTO":
        if stack_exists(cf_client, args.stack):
            print('Updating {}'.format(args.stack))
            response = cf_client.update_stack(StackName=args.stack, TemplateURL=object_url, Parameters=jParameters, Tags=jTags)
            waiter = cf_client.get_waiter('stack_update_complete')
        else:
            print('Creating {}'.format(args.stack))
            response = cf_client.create_stack(StackName=args.stack, TemplateURL=object_url, Parameters=jParameters, Tags=jTags)
            waiter = cf_client.get_waiter('stack_create_complete')
        waiter.wait(StackName=args.stack)
        print('ec2.yaml create = ', response)
    if args.action == "VERIFY":
        pass

    ec2 = boto3.resource('ec2')
    ec2_client = ec2.meta.client
    # ec2_client = boto3.client('ec2')

    # waiting for finishing instances initialization tags['STACK'] = args.stack
    instances = ec2.instances.filter(
        Filters=[{'Name':'tag:STACK', 'Values': [args.stack]},{'Name': 'instance-state-name', 'Values': ['running']}])

    for instance in instances:
        inst_status = ec2_client.describe_instance_status(InstanceIds = [instance.id])
        print("Id1: %s Id2: %s InstanceStatus: %s SystemStatus %s " % (instance.id, \
            inst_status['InstanceStatuses'][0]['InstanceId'], \
            inst_status['InstanceStatuses'][0]['InstanceStatus']['Status'],\
            inst_status['InstanceStatuses'][0]['SystemStatus']['Status']))
        if inst_status['InstanceStatuses'][0]['SystemStatus']['Status'] == 'initializing':
            waiter = ec2_client.get_waiter('system_status_ok')
            waiter.wait(InstanceIds=[instance.id])
        if inst_status['InstanceStatuses'][0]['InstanceStatus']['Status'] == 'initializing':
            waiter = ec2_client.get_waiter('instance_status_ok')
            waiter.wait(InstanceIds=[instance.id])

    # preparion scripts for tunelling
    # inst_info = ec2_client.describe_instances(InstanceIds = [instance.id])
    custom_filter = [{'Name':'tag:VM', 'Values': ['NATGW']},{'Name': 'instance-state-name', 'Values': ['running']}]
    response_n = ec2_client.describe_instances(Filters=custom_filter)
    PublicIpAddress = response_n['Reservations'][0]['Instances'][0]['PublicIpAddress']

    custom_filter = [{'Name':'tag:VM', 'Values': ['BackEnd']},{'Name': 'instance-state-name', 'Values': ['running']}]
    response_b = ec2_client.describe_instances(Filters=custom_filter)
    PrivateIpAddress = response_b['Reservations'][0]['Instances'][0]['PrivateIpAddress']

    ssh_tunnel = 'ssh -o "StrictHostKeyChecking no" -f -N -L 12345:' + \
        PrivateIpAddress + ':22 ec2-user@' + PublicIpAddress
    # ssh_tunnel1 = 'ssh -i id_rsa -o "StrictHostKeyChecking no" -p12345 ec2-user@' + PublicIpAddress + ' '
    print(ssh_tunnel)
    # print('stdout = ', run(ssh_tunnel))
        # print('stdout = ', run(ssh_tunnel1))
    # print('run ssh_tunell', run(ssh_tunnel))

    custom_filter = [{'Name':'tag:VM', 'Values': ['Tomcat']},{'Name': 'instance-state-name', 'Values': ['running']}]
    response_е = ec2_client.describe_instances(Filters=custom_filter)
    TomcatIpAddress = response_е['Reservations'][0]['Instances'][0]['PublicIpAddress']

    conn       = http.client.HTTPConnection(TomcatIpAddress, 8080)
    conn.request("GET", "/")
    response = conn.getresponse()
    print(response.status)
    conn.close()
    print(response.status, response.reason)
    data = response.read()
    print(data)
    # https://www.journaldev.com/19213/python-http-client-request-get-post

    template_filename = "config.j2"
    rendered_filename = "config"
    render_vars = {
        "PublicIP": PublicIpAddress,
        "PrivatIP": PrivateIpAddress
    }

    script_path = os.path.dirname(os.path.abspath(__file__))
    template_file_path = os.path.join(script_path, template_filename)
    rendered_file_path = os.path.join(script_path, rendered_filename)

    environment = jinja2.Environment(loader=jinja2.FileSystemLoader(script_path))
    output_text = environment.get_template(template_filename).render(render_vars)

    print(output_text)

    with open(rendered_file_path, "w") as result_file:
        result_file.write(output_text)

    # try:
    #     tun_sh=open('tunnel.sh', 'a')
    # except FileNotFoundError:
    #     print("can''t open destiantion file %s " % tun_sh)
    #     sys.exit(2)
    # tun_sh.write("%s\r\n" % ssh_tunnel)
    # tun_sh.flush()
    # tun_sh.close()


    # try:
    #     tun_sh=open('tunnel.sh', 'a')
    # except FileNotFoundError:
    #     print("can''t open destiantion file %s " % tun_sh)
    #     sys.exit(2)
    # tun_sh.write("%s\r\n" % ssh_tunnel)
    # tun_sh.flush()
    # tun_sh.close()

    # print('ssh_tunnel = ', ssh_tunnel)
    # print('ssh -i id_rsa -o "StrictHostKeyChecking no" -p12345 ec2-user@localhost')
    # print('stdout = ', run(ssh_tunnel))
# ---------------- working
# 1. scp -o "StrictHostKeyChecking no" -i id_rsa ./id_rsa ec2-user@35.180.85.186:./.ssh/id_rsa
# 2. ssh -o "StrictHostKeyChecking no" -i id_rsa ec2-user@35.180.85.186 "chmod 600 ~/.ssh/id_rsa"
# ### jump server ###
# /.ssh/config
# Host 35.180.85.186
#     HostName 35.180.85.186
#     Port 22
#     User ec2-user
#     IdentityFile ~/.ssh/id_rsa
#     ForwardAgent yes

# Host 10.200.11.208
#     HostName 10.200.11.208
#     ProxyJump 35.180.85.186
#     Port 22
#     User ec2-user
#     ForwardAgent yes
#     IdentityFile ~/.ssh/id_rsa

# 4. ansible hosts
# [bastion]
# 35.180.85.186
# [backend]
# 10.200.11.208
# [all:vars]
# ansible_ssh_user=ec2-user
# ansible_ssh_common_args='-F config'

# ansible -i hosts backend -m ping
# ssh -F config 10.200.11.208

# ./config
# ### jump server ###
# Host bastion
#     HostName 35.180.159.10
#     Port 22
#     User ec2-user
#     StrictHostKeyChecking no
#     ForwardAgent yes

# Host db
#     HostName 10.200.11.103
#     ProxyJump bastion
#     Port 22
#     User ec2-user
#     StrictHostKeyChecking no
#     ForwardAgent yes

# # inventory
# [gate]
# bastion
# [backend]
# db
# [all:vars]
# ansible_ssh_user=ec2-user
# ansible_ssh_common_args='-F config'

# Jenkinsfile-create
# Jenkinsfile-deploy
# Jenkinsfile-destroy


if __name__ == "__main__":
    # execute only if run as a script
    main()