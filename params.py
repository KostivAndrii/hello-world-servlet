#!/usr/bin/env python3
import sys
#import os
import json
import yaml

allowed_env = ['DEV','QA','TEST']

def process_yaml(inputfile, outputfile):
  try:
      stream = open(inputfile, 'r')
  except FileNotFoundError:
#      path = os.getcwd()
#      print("can''t open source file %s\%s " % (path, inputfile))
      print("can''t open source file %s" % inputfile)
      sys.exit(1)
#   try:
#       output=open(outputfile, 'w')
#   except FileNotFoundError:
#       print("can''t open destiantion file %s " % inputfile)
#       sys.exit(2)
  datamap = yaml.safe_load(stream)
  print('json_obj =', datamap)

  Parameters = []
  for paramm in datamap[0]["Parameters"]:
      value = datamap[0]["Parameters"][paramm]
      Key = {"ParameterKey": paramm, "ParameterValue": value}
      Parameters.append(Key)
  print('Parameters =', Parameters)
  try:
      output=open(outputfile, 'w')
  except FileNotFoundError:
      print("can''t open destiantion file %s " % inputfile)
      sys.exit(2)
  json.dump(Parameters, output)
  output.flush()
  output.close()

  Tags = []
  for paramm in datamap[1]["Tags"]:
      value = datamap[1]["Tags"][paramm]
      Key = {"Key": paramm, "Value": value}
      Tags.append(Key)
  print('Tags =', Tags)
  try:
      output=open('tags.json', 'w')
  except FileNotFoundError:
      print("can''t open destiantion file %s " % inputfile)
      sys.exit(2)
  json.dump(Tags, output)
  output.flush()
  output.close()



days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

for i,m in enumerate(days, start=3):
    print(i,m)

def main():
    if len(sys.argv[1:]) < 1 :
        sys.exit('should be described ENVIRONMENT')
    envir = sys.argv[1]
    if envir not in allowed_env:
        print('wrong env - we process only', allowed_env)
        sys.exit()

    # print('the script has the name %s' % program_name)
    print("the script will convert params-%s.yaml and tags-%s.yaml into params.json and tags.json" % (sys.argv[1], sys.argv[1]))
    print('we will prepare params.json and tags.json for ENVIRONMENT %s' % envir)

    print('')
    print("Lets process params.yaml")

    inputfile = 'params-'+sys.argv[1]+'.yaml'
    process_yaml(inputfile, 'params.json')

    print('')
    print("Lets process tags.yaml")

    inputfile = 'tags-'+sys.argv[1]+'.yaml'
    #process_yaml(inputfile, 'tags.json')


if __name__ == "__main__":
    # execute only if run as a script
    main()