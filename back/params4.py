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
    "-e=TEST",
    "-s=AWS-NATGW",
    "-a=BOTO",
    "-i=my_cfg.yaml",
    "-cf=ec2.yaml",
    "-cfk=ec2.yaml",
    "-s3=cf-yaml-s3-bucket"

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

    # s3_client = boto3.client('s3')
    # s3_client = s3.meta.client
    # bucket_location = boto3.client('s3').get_bucket_location(Bucket=args.s3)

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


    # cmd = "aws cloudformation validate-template --template-url " + object_url
    # print('ec2.yaml validate1 = ', run(cmd))
    # bucket_location = s3.meta.client.get_bucket_location(Bucket=args.s3)
    # object_url = "https://s3-{0}.amazonaws.com/{1}/{2}".format(bucket_location['LocationConstraint'], args.s3, args.cloud_formation_key)
    # cmd = "aws cloudformation validate-template --template-url https://cf-yaml-s3-bucket.s3.eu-west-3.amazonaws.com/ec2.yaml"
    # print('ec2.yaml validate2 = ', run(cmd))

    # s3 = boto3.resource('s3')
    # bucket = s3.Bucket(args.s3)
    # for obj in bucket.objects.all():
    #     print(obj.key)

    # #  create_bucket
    # first_bucket_name, first_response = create_bucket(bucket_prefix=args.s3, s3_connection=s3.meta.client)
    # # second_bucket_name, second_response = create_bucket(bucket_prefix='secondpythonbucket', s3_connection=s3_client)
    # # third_bucket_name, third_response = create_bucket(bucket_prefix='thirdpythonbucket', s3_connection=s3.meta.client)

    # first_file_name = create_temp_file(300, 'firstfile.txt', 'f')
    # # first_bucket = s3_resource.Bucket(name=first_bucket_name)
    # first_object = s3.Object(bucket_name=args.s3, key=args.cloud_formation_key)

    # # first_object_again = first_bucket.Object(first_file_name)
    # # first_bucket_again = first_object.Bucket()

    # # s3_resource.Object(first_bucket_name, first_file_name).upload_file(Filename=first_file_name)
    # # first_object.upload_file(first_file_name)
    # # s3_resource.Bucket(first_bucket_name).upload_file(Filename=first_file_name, Key=first_file_name)
    # # s3_resource.meta.client.upload_file(Filename=first_file_name, Bucket=first_bucket_name, Key=first_file_name)

    # # upload file
    # first_object.upload_file(args.cloud_formation)
    # s3.Object(args.s3, first_file_name).upload_file(Filename=args.cloud_formation)
    # s3.Object(args.s3, args.cloud_formation_key).upload_file(Filename=args.cloud_formation)
    # s3.Bucket(args.s3).upload_file(Filename=args.cloud_formation, Key=args.cloud_formation_key)
    # s3.meta.client.upload_file(Filename=args.cloud_formation, Bucket=args.s3, Key=args.cloud_formation_key)

    # # dict comprehensive
    # team1 = {"Jones": 24, "Jameson": 18, "Smith": 58, "Burns": 7}
    # team2 = {"White": 12, "Macke": 88, "Perce": 4}
    # newTeam = {k:v for team in (team1, team) for k,v in team.items()}

    # boto.cloudformation.connect_to_region("eu-west-3")
    # template_url = 'https://s3.eu-west-3.amazonaws.com/cf-templates-1ldvye973texh-eu-west-3/2019153GhZ-ec2-natgw-tomcattpk5so5vb7k'
    # template_url = 'https://s3-external-1.amazonaws.com/cf-templates-1ldvye973texh-us-east-1/20191539Ae-cf-natgw-tomcatuumsynh895'
    # nasted https://s3-external-1.amazonaws.com/cf-templates-1ldvye973texh-us-east-1/2019153q0R-tomcat-v.2.153en2wbmth2v
    # with open("ec2.yaml") as tmpfile:
    #     template_body = json.dumps(yaml.safe_load(tmpfile))
    # conn = boto.cloudformation.connection.CloudFormationConnection()
    # conn.create_stack('mystack', template_body=None, template_url=template_url, parameters=cf_param, notification_arns=[], disable_rollback=False, timeout_in_minutes=None, capabilities=None)

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

        # # template_url = 'https://s3-external-1.amazonaws.com/cf-templates-1ldvye973texh-us-east-1/20191539Ae-cf-natgw-tomcatuumsynh895'
        # # stdout = create_cf_boto(stack, template_url, parameters, tags)
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

    ssh_tunnel = 'ssh -i id_rsa -o "StrictHostKeyChecking no" -f -N -L 12345:' + \
        PrivateIpAddress + ':22 ec2-user@' + PublicIpAddress
    print('ssh_tunnel = ', ssh_tunnel)
    print('ssh -i id_rsa -o "StrictHostKeyChecking no" -p12345 ec2-user@localhost')
    print('stdout = ', run(ssh_tunnel))

    instances = ec2.instances.filter(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
    # print('instances = ', instances)
    # print('')
    # myinstances = [ instance.id for instance in instances ]
    # print('myinstances = ', myinstances)
    # print('')
    # inst_status = m_client.describe_instance_status(InstanceIds = myinstances)
    # print('inst_status_my = ', inst_status)
    # print('')
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

    # cf_client = boto3.client('cloudformation')
    # r = cf_client.describe_stacks(StackName = args.stack)
    # s, = r['Stacks']
    # outputs = s['Outputs']
    # print('Stacks = ', s)
    # # print('')
    # print('outputs = ', outputs)

#     inst_status = m_client.describe_instance_status()
#     print('inst_status_all = ', inst_status)
#     print('')


#     for instance in ec2.instances.all():
#         print(instance)

#     client.describe_instance_status()

#     for instance in instances:
#         print(instance.id, instance.instance_type)

#     client.describe_instance_status(InstanceIds=[     'i-07eb26270d31d946b'   ])
#     client.describe_instance_status()

#     response = client.describe_tags(Filters=[{'Key': 'VM', 'Value': 'Tomcat'}])
#     print(response)
#     custom_filter = [{'Name':'tag:VM', 'Values': ['Tomcat']}]
#     response = client.describe_instances(Filters=custom_filter)
#     response = client.describe_instances()
#     for instance in ec2.instances.all():
#         print(instance)

#     client.describe_instance_status(InstanceIds=[     'i-01fe2c4814225824a'   ])
#     client.describe_instance_status()

#     cf_client = boto3.client('cloudformation')
#     r = cf_client.describe_stacks(StackName="AWS-NATGW")
#     s, = r['Stacks']
#     outputs = s['Outputs']

#     out = {}
#     for o in outputs:
#         key = _to_env(o['OutputKey'])
#         out[key] = o['OutputValue']
#     print(json.dumps(out, indent=2))
# import boto3
# import re
# def _to_env(name):
#     s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
#     return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).upper()

# # open tunel from localhost:12345 to BackEnd ssh (10.200.11.96:22) though NATGW (ec2-user@35.180.227.97)
# $ ssh -i id_rsa -o "StrictHostKeyChecking no" -f -N -L 12345:10.200.11.96:22 ec2-user@35.180.227.97
# # making ssh connecting to BackEnd though local port localhost:12345
# $ ssh -i id_rsa -o "StrictHostKeyChecking no" -p12345 ec2-user@localhost

if __name__ == "__main__":
    # execute only if run as a script
    main()