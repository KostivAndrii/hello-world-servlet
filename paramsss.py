#!/usr/bin/env python3
import sys
#import os
import json
import yaml

allowed_env = ['DEV','QA']

def process_yaml(inputfile, outputfile):
  try:
      stream = open(inputfile, 'r')
  except FileNotFoundError:
#      path = os.getcwd()
#      print("can''t open source file %s\%s " % (path, inputfile))
      print("can''t open source file %s" % inputfile)
      sys.exit(1)
  try:
      output=open(outputfile, 'w')
  except FileNotFoundError:
#      path = os.getcwd()
#      print("can''t open destiantion file %s\%s " % (path, inputfile))
      print("can''t open destiantion file %s " % inputfile)
      sys.exit(2)
  datamap = yaml.safe_load(stream)
  print('json_obj =', datamap)
  A = datamap[0]
  print('ENV', A)
  json.dump(datamap, output)
  output.flush()
  output.close()
  stream.close()


# program_name = sys.argv[0]
if len(sys.argv[1:]) < 1 :
    sys.exit('should be described ENVIRONMENT') 
envir = sys.argv[1]
if envir not in allowed_env:
    print('wrong env - we process only', allowed_env)
    sys.exit()

#print('the script has the name %s' % sys.argv[0])
print("the script will convert params-%s.yaml and tags-%s.yaml into params.json and tags.json" % (sys.argv[1], sys.argv[1]))
print('we will prepare params.json and tags.json for ENVIRONMENT %s' % envir)
#print("working dir is %s " % os.getcwd())
print('')
print("Lets process params.yaml")

inputfile = 'params-'+sys.argv[1]+'.yaml'
process_yaml(inputfile, 'params.json')

print('')
print("Lets process tags.yaml")

inputfile = 'tags-'+sys.argv[1]+'.yaml'
process_yaml(inputfile, 'tags.json')

