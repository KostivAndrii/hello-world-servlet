#!/usr/bin/env python3
import sys
import os
import json
import yaml
import argparse
import boto.cloudformation
import boto3
import uuid

allowed_env = ['DEV','QA','TEST']
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
        print("can''t open destiantion file %s " % inputfile)
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


def main():
    parser = argparse.ArgumentParser(description='Programm to work with AWS')
    parser.add_argument("-e","--env", help="Environment name", type=str)
    parser.add_argument("-s","--stack", help="STACK name", type=str)
    parser.add_argument('-a','--action', help='what to do CREATE/UPDATE/BOTO')
    parser.add_argument('-i','--input', help='file with parameters and tags')
    # parser.add_argument('-cf','--cloud-formation', help='file with parameters and tags')
    # "-e=TEST",
    # "-s=AWS-NATGW",
    # "-a=CREATE",
    # "-i=my_cfg.yaml"

    args = parser.parse_args()
    if args.env not in allowed_env:
        print('wrong env - we process only', allowed_env)
        sys.exit()
    if args.action not in allowed_action:
        print('wrong env - we process only', allowed_action)
        sys.exit()
    # envir = args['env']
    # stack = args['stack']
    # inputfile = args['input']
    # action = args['action']
    
    print("script will convert %s into parameters.json and tags.json for ENVIRONMENT %s and %s STACK %s" \
        % (args.input, args.env, args.action, args.stack) )

    cfg = read_cfg(args.input)
    print('cfg = ', cfg)

    parameters = cfg["parameters"]
    tags = cfg["tags"]
    print('parameters = ', parameters)
    print('tags = ', tags)

    #https://realpython.com/python-boto3-aws-s3/
    s3_client = boto3.client('s3')
    s3_resource = boto3.resource('s3')

    first_bucket_name, first_response = create_bucket( bucket_prefix='firstpythonbucket', s3_connection=s3_resource.meta.client)
    second_bucket_name, second_response = create_bucket(bucket_prefix='secondpythonbucket', s3_connection=s3_resource)

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

    write_json("parameters.json",parameters,"ParameterKey", "ParameterValue")
    write_json("tags.json",tags,"Key", "Value")
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
    # if action == "BOTO":
    #     template_url = 'https://s3-external-1.amazonaws.com/cf-templates-1ldvye973texh-us-east-1/20191539Ae-cf-natgw-tomcatuumsynh895'
    #     stdout = create_cf_boto(stack, template_url, parameters, tags)
    #     print('stdout = ', stdout)


if __name__ == "__main__":
    # execute only if run as a script
    main()