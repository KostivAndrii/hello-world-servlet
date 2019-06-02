#!/usr/bin/env python3
import sys
import os
import json
import yaml
import boto3
import boto.cloudformation

conn = boto.cloudformation.connection.CloudFormationConnection()
conn.create_stack('mystack', template_body=None, template_url='https://cloudfront-live.s3.amazonaws.com/live-http-streaming-fms-4-5-1-using-cloudfront.txt', parameters=], notification_arns=[, disable_rollback=False, timeout_in_minutes=None, capabilities=None)


s3 = boto3.resource('s3')
print(s3)
ec2 = boto.ec2.connect_to_region('eu-west-3')

allowed_env = ['DEV','QA','TEST']

def read_cfg(inputfile):
    try:
        stream = open(inputfile, 'r')
    except FileNotFoundError:
        # path = os.getcwd()
        # print("can''t open source file %s\%s " % (path, inputfile))
        print("can''t open source file %s" % inputfile)
        sys.exit(1)
    # path = os.getcwd()
    datamap = yaml.safe_load(stream)
    stream.close()
    print('json_obj =', datamap)
    return datamap


def write_json(outputfile, data, KeyName, ValueName):
    try:
        output=open(outputfile, 'w')
    except FileNotFoundError:
        print("can''t open destiantion file %s " % inputfile)
        sys.exit(2)

    OutputParam = []
    for paramm in data:
        value = data[paramm]
        Key = {KeyName: paramm, ValueName: value}
        OutputParam.append(Key)
    print('OutputParam =', OutputParam)

    # path = os.getcwd()
    json.dump(OutputParam, output)
    output.flush()
    output.close()
    return OutputParam


def run(cmd):
    stdout = os.popen(cmd).read()
    return stdout

def main():
    args_count = len(sys.argv[1:])
    if args_count < 1 :
        sys.exit('should be described ENVIRONMENT')
    envir = sys.argv[1]
    if envir not in allowed_env:
        print('wrong env - we process only', allowed_env)
        sys.exit()
    if args_count > 1 :
        inputfile = sys.argv[2]
    else:
        inputfile = 'my_cfg.yaml'
    if args_count > 2 :
        stack = sys.argv[3]
    else:
        stack = 'AWS-NATGW'
    if args_count > 3 :
        action = sys.argv[4]
    else:
        action = 'CREATE'

    print("script will convert %s into parameters.json and tags.json for ENVIRONMENT %s and %s STACK %s" % (inputfile, envir, action, stack) )

    # inputfile = 'params-'+sys.argv[1]+'.yaml'
    cfg = read_cfg(inputfile)
    print('cfg = ', cfg)

    parameters = cfg[0]["parameters"]
    tags = cfg[1]["tags"]
    print('parameters = ', parameters)
    print('tags = ', tags)

    write_json("parameters.json",parameters,"ParameterKey", "ParameterValue")
    write_json("tags.json",tags,"Key", "Value")
    # process_yaml(inputfile, 'params.json')

    cmd = "aws cloudformation validate-template --template-body file://./ec2.yaml"
    stdout = run(cmd)
    print('stdout = ', stdout)

    if action == "CREATE":
        cmd = "aws cloudformation create-stack --stack-name "+stack+" --template-body file://ec2.yaml --parameters file://parameters.json --tags file://tags.json"
        stdout = run(cmd)
        print('stdout = ', stdout)
    if action == "UPDATE":
        cmd = "aws cloudformation update-stack --stack-name "+stack+" --template-body file://ec2.yaml --parameters file://parameters.json --tags file://tags.json"
        stdout = run(cmd)
        print('stdout = ', stdout)

    # print('')
    # print("Lets process tags.yaml")

    # inputfile = 'tags-'+sys.argv[1]+'.yaml'
    # process_yaml(inputfile, 'tags.json')


if __name__ == "__main__":
    # execute only if run as a script
    main()