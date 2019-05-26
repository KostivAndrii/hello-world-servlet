#!/usr/bin/env python
import sys
import json
import yaml

program_name = sys.argv[0]
envir = sys.argv[1]
#count = len(sys.argv[1:])

print('the script has the name %s' % program_name)
#print("the script is called with %i arguments" % count) 
print("the script will convert params-%s.yaml and tags-%s.yaml into params.json and tags.json" % (sys.argv[1], sys.argv[1]))
print('we will prepare params.json and tags.json for ENVIRONMENT %s' % envir)


inputfile = 'params-'+sys.argv[1]+'.yaml'
print('inputfile is %s' % inputfile )
stream = open(inputfile, 'r')
datamap = yaml.safe_load(stream)
print('json_obj =', datamap)
output=open('params.json', 'w')
json.dump(datamap, output)
output.flush()
output.close()
stream.close()


inputfile = 'tags-'+sys.argv[1]+'.yaml'
print('inputfile is %s' % inputfile )
stream = open(inputfile, 'r')
datamap = yaml.safe_load(stream)
print('json_obj =', datamap)
output=open('tags.json', 'w')
json.dump(datamap, output)
output.flush()
output.close()
stream.close()
