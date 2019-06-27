from __future__ import division, print_function, unicode_literals

import json
import re

import boto3


def main(stack):
    cf = boto3.client('cloudformation')
    r = cf.describe_stacks(StackName=stack)

    stack, = r['Stacks']
    outputs = stack['Outputs']

    out = {}
    for o in outputs:
        key = _to_env(o['OutputKey'])
        out[key] = o['OutputValue']
    print(json.dumps(out, indent=2))


def _to_env(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).upper()


if __name__ == '__main__':
    import sys
    main(sys.argv[1])
