import json
import yaml

sample = {
  "Environment": "STAGE",
  "KeyName": "aws-test-oregon",
  "NATGWInstanceTypeParameter": "t2.micro",
  "VPCBlock": "10.0.0.0/16",
  "PublicSubnetCIDR": "10.0.10.0/24",
  "PrivateSubnetCIDR": "10.0.11.0/24"
}

json_obj = json.dumps(sample)
print('json_obj =', json_obj)

ff = open('params.yaml', 'wb')

stream = open('parammm.yaml', 'r')
datamap = yaml.safe_load(stream)
print('json_obj =', datamap)
output=open('parammm.json', 'w')
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

