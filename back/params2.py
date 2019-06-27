#!/usr/bin/env python3
import sys
import os
import json
import yaml
import argparse

# import boto3
import boto.cloudformation

# conn = boto.cloudformation.connection.CloudFormationConnection()
# conn.create_stack('mystack', template_body="ec2.yaml", template_url=None, parameters=], notification_arns=[, disable_rollback=False, timeout_in_minutes=None, capabilities=None)
# conn.create_stack('mystack', template_body="ec2.yaml", template_url=None, parameters=[('KeyPair', 'myKeyPair'), ('FMSAdminPassword', 'myPassword')], notification_arns=[], disable_rollback=False, timeout_in_minutes=None, capabilities=None)

# s3 = boto3.resource('s3')
# print(s3)
# ec2 = boto.ec2.connect_to_region('eu-west-3')

allowed_env = ['DEV','QA','TEST']
allowed_action = ['CREATE', 'UPDATE', 'TEST', 'BOTO']

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

    OutputParam = [ {KeyName: paramm, ValueName: data[paramm]} for paramm in data ]
    # OutputParam = []
    # for paramm in data:
    #     # value = data[paramm]
    #     Key = {KeyName: paramm, ValueName: data[paramm]}
    #     OutputParam.append(Key)
    # print('OutputParam2 =', OutputParam2)
    print('OutputParam =', OutputParam)

    # path = os.getcwd()
    json.dump(OutputParam, output)
    output.flush()
    output.close()
    return OutputParam


def run(cmd):
    stdout = os.popen(cmd).read()
    return stdout


def create_cf_boto(cf_stack, cf_template_url, parameters, tags):
    # cf_param = []
    # for paramm in parameters:
    #     Key = (paramm, parameters[paramm])
    #     cf_param.append(Key)
    cf_param = [ (paramm, parameters[paramm]) for paramm in parameters ]
    # cf_tags = {}
    # for paramm in tags:
    #     cf_tags[paramm] = tags[paramm]
    #     # cf_tags.append(Key)
    cf_tags = { paramm: tags[paramm] for paramm in tags }
    conn = boto.cloudformation.connection.CloudFormationConnection()
    stdout = conn.create_stack(cf_stack, template_body=None, template_url=cf_template_url, parameters=cf_param, notification_arns=[], disable_rollback=False, timeout_in_minutes=None, capabilities=None, tags=cf_tags)
    return stdout

def main():
    parser = argparse.ArgumentParser(description='Programm to work with AWS')
    parser.add_argument("-e","--env", help="Environment name", type=str)
    parser.add_argument("-s","--stack", help="STACK name", type=str)
    parser.add_argument('-a','--action', help='what to do CREATE/UPDATE/BOTO')
    parser.add_argument('-i','--input', help='file with parameters and tags')
    parser.add_argument('-cf','--cloud-formation', help='file with parameters and tags')
    # parser.add_argument('-e','--env', help='Environment', required=True)
    # parser.add_argument('-s','--stack', help='STACK name', required=True)
    # parser.add_argument('-a','--action', help='what to do CREATE/UPDATE/BOTO', required=True)
    # parser.add_argument('-i','--input', help='file with parameters and tags', required=False)
    args = parser.parse_args()
    # args = vars(parser.parse_args())
    if args.env not in allowed_env:
        print('wrong env - we process only', allowed_env)
        sys.exit()
    if args.action not in allowed_action:
        print('wrong env - we process only', allowed_action)
        sys.exit()
    # stack = args['stack']
    # inputfile = args['input']

    # args_count = len(sys.argv[1:])
    # if args_count < 1 :
    #     sys.exit('should be described ENVIRONMENT')
    # envir = sys.argv[1]
    # if envir not in allowed_env:
    #     print('wrong env - we process only', allowed_env)
    #     sys.exit()
    # if args_count > 1 :
    #     inputfile = sys.argv[2]
    # else:
    #     inputfile = 'my_cfg.yaml'
    # if args_count > 2 :
    #     stack = sys.argv[3]
    # else:
    #     stack = 'AWS-NATGW'
    # if args_count > 3 :
    #     action = sys.argv[4]
    # else:
    #     action = 'CREATE'

    # print("script will convert %s into parameters.json and tags.json for ENVIRONMENT %s and %s STACK %s" % (inputfile, envir, action, stack) )

    # inputfile = 'params-'+sys.argv[1]+'.yaml'
    cfg = read_cfg(args.input)
    print('cfg = ', cfg)

    parameters = cfg["parameters"]
    tags = cfg["tags"]
    print('parameters = ', parameters)
    print('tags = ', tags)

    # # dict comprehensive
    # team1 = {"Jones": 24, "Jameson": 18, "Smith": 58, "Burns": 7}
    # team2 = {"White": 12, "Macke": 88, "Perce": 4}
    # newTeam = {k:v for team in (team1, team) for k,v in team.items()}


    # cf_param = []
    # for paramm in parameters:
    #     Key = (paramm, parameters[paramm])
    #     cf_param.append(Key)

    # boto.cloudformation.connect_to_region("eu-west-3")
    # conn.
    # conn.
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

    cmd = "aws cloudformation validate-template --template-body file://./ec2.yaml"
    stdout = run(cmd)
    print('stdout = ', stdout)

    if args.action == "CREATE":
        cmd = "aws cloudformation create-stack --stack-name " + args.stack + \
              " --template-body file://ec2.yaml --parameters file://parameters.json --tags file://tags.json"
        stdout = run(cmd)
        print('stdout = ', stdout)
    if args.action == "UPDATE":
        cmd = "aws cloudformation update-stack --stack-name "+args.stack+" --template-body file://ec2.yaml --parameters file://parameters.json --tags file://tags.json"
        stdout = run(cmd)
        print('stdout = ', stdout)
    if args.action == "BOTO":
        template_url = 'https://s3-external-1.amazonaws.com/cf-templates-1ldvye973texh-us-east-1/20191539Ae-cf-natgw-tomcatuumsynh895'
        stdout = create_cf_boto(args.stack, template_url, parameters, tags)
        print('stdout = ', stdout)

    # print('')
    # print("Lets process tags.yaml")

    # inputfile = 'tags-'+sys.argv[1]+'.yaml'
    # process_yaml(inputfile, 'tags.json')


if __name__ == "__main__":
    # execute only if run as a script
    main()