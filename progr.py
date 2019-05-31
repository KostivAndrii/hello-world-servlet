#!/usr/bin/env python
import sys
import json
import yaml


def process_yaml(inputfile, outputfile):
  try:
      stream = open(inputfile, 'r')
  except FileNotFoundError:
      print("can''t open source file %s " % inputfile)
      sys.exit("can''t open source file")
  try:
      output=open(outputfile, 'w')
  except FileNotFoundError:
      print("can''t open destiantion file %s " % inputfile)
      sys.exit("can''t open destiantion file")
  datamap = yaml.safe_load(stream)
  print('json_obj =', datamap)
  A = datamap[0]['env']
  print('ENV', A)

  json.dump(datamap, output)
  output.flush()
  output.close()
  stream.close()


program_name = sys.argv[0]
envir = sys.argv[1]
#count = len(ys.argv[1:]

print('the script has the name %s' % program_name)
#print("the script is called with %i arguments" % count)
print("the script will convert params-%s.yaml and tags-%s.yaml into params.json and tags.json" % (sys.argv[1], sys.argv[1]))
print('we will prepare params.json and tags.json for ENVIRONMENT %s' % envir)


inputfile = 'params-'+sys.argv[1]+'.yaml'
# inputfile = 'params-'+'DEV'+'.yaml'

process_yaml(inputfile, 'params.json')
# print('inputfile is %s' % inputfile )
# stream = open(inputfile, 'r')
# datamap = yaml.safe_load(stream)
# print('json_obj =', datamap)
# output=open('params.json', 'w')
# json.dump(datamap, output)
# output.flush()
# output.close()
# stream.close()

inputfile = 'tags-'+sys.argv[1]+'.yaml'
process_yaml(inputfile, 'tags.json')

# print('inputfile is %s' % inputfile )
# stream = open('inputfile', 'r')
# datamap = yaml.safe_load(stream)
# print('json_obj =', datamap)
# output=open('tags.json', 'w')
# json.dump(datamap, output)
# output.flush()
# output.close()
# stream.close()
# print ("the script has the name %s" % (sys.argv[0])
# arguments = len(sys.argv) - 1  
# print ("the script is called with %i arguments" % (arguments)) 
# print ("the script will convert params-%s.yaml tags-%s.yaml into params.yaml tags.yaml" % (sys.argv[1])

program_name = sys.argv[0]
arguments = sys.argv[1:]
count = len(arguments)


stream = open('param.yaml', 'r')
datamap = yaml.safe_load(stream)
print('json_obj =', datamap)
output=open('param.json', 'w')
json.dump(datamap, output)
output.flush()
output.close()
stream.close()

# https://stackoverflow.com/questions/51914505/python-yaml-to-json-to-yaml
# https://github.com/awslabs/aws-cfn-template-flip
yaml.dump(sample, ff, default_flow_style=False)
type(ff)

ydump = yaml.dump(sample, default_flow_style=False)
print 'ydump=',ydump

import os
os.getcwd()
os.chdir("/home/akostiv/source/hello-world-servlet/")
