#!/usr/bin/env python3
import sys
import os
import json
import yaml
import argparse
# import boto.cloudformation
import boto3
import uuid

# allowed_env = ['DEV','QA','TEST']
allowed_action = ['CREATE', 'UPDATE', 'TEST', 'BOTO']

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

def create_bucket_name(bucket_prefix):
    # The generated bucket name must be between 3 and 63 chars long
    return ''.join([bucket_prefix, str(uuid.uuid4())])

def create_temp_file(size, file_name, file_content):
    random_file_name = ''.join([str(uuid.uuid4().hex[:6]), file_name])
    with open(random_file_name, 'w') as f:
        f.write(str(file_content) * size)
    return random_file_name

def create_bucket(bucket_prefix, s3_connection):
    session = boto3.session.Session()
    current_region = session.region_name
    bucket_name = create_bucket_name(bucket_prefix)
    bucket_response = s3_connection.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration={
        'LocationConstraint': current_region})
    print(bucket_name, current_region)
    return bucket_name, bucket_response

def get_obj_url(s3_client, s3_bucket, s3_key):
    bucket_location = s3_client.get_bucket_location(Bucket=s3_bucket)
    return "https://{1}.s3.{0}.amazonaws.com/{2}".format(bucket_location['LocationConstraint'], s3_bucket, s3_key)

def _stack_exists(cf_client, stack_name):
    stacks = cf_client.list_stacks()['StackSummaries']
    for stack in stacks:
        if stack['StackStatus'] == 'DELETE_COMPLETE':
            continue
        if stack_name == stack['StackName']:
            return True
    return False

def main():
    parser = argparse.ArgumentParser(description='Programm to work with AWS')
    parser.add_argument("-s","--stack", help="STACK name", type=str)
    parser.add_argument('-a','--action', help='what to do CREATE/UPDATE/BOTO')
    parser.add_argument('-i','--input', help='file with parameters and tags')
    parser.add_argument('-cf','--cloud-formation', help='file with parameters and tags')
    parser.add_argument('-cfk','--cloud-formation-key', help='file with parameters and tags')
    parser.add_argument('-s3','--s3', help='file with parameters and tags')

    args = parser.parse_args()
    if args.action not in allowed_action:
        print('wrong env - we process only', allowed_action)
        sys.exit()

    print("script will convert %s into parameters.json and tags.json for ENVIRONMENT ... and %s STACK %s" \
        % (args.input, args.action, args.stack) )

    cfg = read_cfg(args.input)
    print('cfg = ', cfg)

    parameters = cfg["parameters"]
    tags = cfg["tags"]
    print('parameters = ', parameters)
    print('tags = ', tags)

    #https://realpython.com/python-boto3-aws-s3/
    s3 = boto3.resource('s3')
    cf_client = boto3.client('cloudformation')

    # delete previous version args.s3, args.cloud_formation_key
    obj = s3.Object(args.s3, args.cloud_formation_key)
    obj.delete()

    # upload args.cloud_formation args.s3 args.cloud_formation_key
    try:
        data=open(args.cloud_formation, 'rb')
    except FileNotFoundError:
        print("can''t open destiantion file %s " % args.cloud_formation)
        sys.exit(2)
    s3.Bucket(args.s3).put_object(Key=args.cloud_formation_key, Body=data)

    # get s3_file_URL
    object_url = get_obj_url(s3.meta.client, args.s3, args.cloud_formation_key)

    # validate templatee
    response = cf_client.validate_template(TemplateURL=object_url)
    print('ec2.yaml validate = ', response)

    jParameters = write_json("parameters.json",parameters,"ParameterKey", "ParameterValue")
    jTags = write_json("tags.json",tags,"Key", "Value")
    # process_yaml(inputfile, 'params.json')

    cmd = "aws cloudformation validate-template --template-body file://ec2.yaml"
    # stdout = run(cmd)
    print('stdout = ', run(cmd))

    if args.action == "CREATE":
        cmd = "aws cloudformation create-stack --stack-name " + args.stack + \
              " --template-body file://ec2.yaml --parameters file://parameters.json --tags file://tags.json"
        stdout = run(cmd)
        print('stdout = ', stdout)
    if args.action == "UPDATE":
        cmd = "aws cloudformation update-stack --stack-name " + args.stack + \
              " --template-body file://ec2.yaml --parameters file://parameters.json --tags file://tags.json"
        stdout = run(cmd)
        print('stdout = ', stdout)
    if args.action == "BOTO":
        if _stack_exists(cf_client, args.stack):
            print('Updating {}'.format(args.stack))
            response = cf_client.update_stack(StackName=args.stack, TemplateURL=object_url, Parameters=jParameters, Tags=jTags)
            waiter = cf_client.get_waiter('stack_update_complete')
        else:
            print('Creating {}'.format(args.stack))
            response = cf_client.create_stack(StackName=args.stack, TemplateURL=object_url, Parameters=jParameters, Tags=jTags)
            waiter = cf_client.get_waiter('stack_create_complete')
        waiter.wait(StackName=args.stack)
        # response = cf_client.create_stack(StackName=args.stack, TemplateURL=object_url, Parameters=jParameters, Tags=jTags)
        print('ec2.yaml create = ', response)
        # cf_param = [ {paramm, parameters[paramm]} for paramm in parameters ]
        # cf_tags = { paramm: tags[paramm] for paramm in tags }
        # response = cf_client.create_stack(StackName=args.stack, TemplateURL=object_url, Parameters=cf_param, Tags=cf_tags)
        # print('stdout = ', stdout)
    ec2 = boto3.resource('ec2')
    m_client = ec2.meta.client
    # m_client = boto3.client('ec2')

    # inst_info = m_client.describe_instances(InstanceIds = [instance.id])
    custom_filter = [{'Name':'tag:VM', 'Values': ['NATGW']},{'Name': 'instance-state-name', 'Values': ['running']}]
    response_n = m_client.describe_instances(Filters=custom_filter)
    custom_filter = [{'Name':'tag:VM', 'Values': ['BackEnd']},{'Name': 'instance-state-name', 'Values': ['running']}]
    response_b = m_client.describe_instances(Filters=custom_filter)

    PublicIpAddress = response_n['Reservations'][0]['Instances'][0]['PublicIpAddress']
    PrivateIpAddress = response_b['Reservations'][0]['Instances'][0]['PrivateIpAddress']

    print('NATGW PublicIpAddress = ', PublicIpAddress)
    print('BackEnd PrivateIpAddress = ', PrivateIpAddress)

    ssh_tunnel1 = 'ssh -i id_rsa -o "StrictHostKeyChecking no" ec2-user@' + PublicIpAddress + ' '
    ssh_tunnel = 'ssh -i id_rsa -o "StrictHostKeyChecking no" -f -N -L 12345:' + \
        PrivateIpAddress + ':22 ec2-user@' + PublicIpAddress
    print('ssh_tunnel = ', ssh_tunnel)
    print('ssh -i id_rsa -o "StrictHostKeyChecking no" -p12345 ec2-user@localhost')
    print('stdout = ', run(ssh_tunnel))



    instances = ec2.instances.filter(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])

    for instance in instances:
        inst_status = m_client.describe_instance_status(InstanceIds = [instance.id])
        print("Id1: %s Id2: %s InstanceStatus: %s SystemStatus %s " % (instance.id, \
            inst_status['InstanceStatuses'][0]['InstanceId'], \
            inst_status['InstanceStatuses'][0]['InstanceStatus']['Status'],\
            inst_status['InstanceStatuses'][0]['SystemStatus']['Status']))
        if inst_status['InstanceStatuses'][0]['SystemStatus']['Status'] == 'initializing':
            waiter = m_client.get_waiter('system_status_ok')
            waiter.wait(InstanceIds=[instance.id])
        if inst_status['InstanceStatuses'][0]['InstanceStatus']['Status'] == 'initializing':
            waiter = m_client.get_waiter('instance_status_ok')
            waiter.wait(InstanceIds=[instance.id])


if __name__ == "__main__":
    # execute only if run as a script
    main()