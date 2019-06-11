#!/bin/bash

ssh -o "StrictHostKeyChecking no" -f -N -L 12345:10.200.11.18:22 ec2-user@35.180.113.227
ssh -o "StrictHostKeyChecking no" -f -N -L 12345:10.200.11.222:22 ec2-user@35.180.25.127
ssh -o "StrictHostKeyChecking no" -f -N -L 12345:10.200.11.43:22 ec2-user@35.180.202.191
ssh -o "StrictHostKeyChecking no" -f -N -L 12345:10.200.11.43:22 ec2-user@35.180.202.191
ssh -o "StrictHostKeyChecking no" -f -N -L 12345:10.200.11.217:22 ec2-user@35.180.88.110
ssh -o "StrictHostKeyChecking no" -f -N -L 12345:10.200.11.208:22 ec2-user@35.180.85.186
ssh -o "StrictHostKeyChecking no" -f -N -L 12345:10.200.11.249:22 ec2-user@52.47.128.228
