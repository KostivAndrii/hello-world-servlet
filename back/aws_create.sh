#!/bin/bash
#set -x

aws_key_name="aws-test-oregon"
ssh_key="aws-test-oregon.pem"

if [[ -f "$ssh_key" ]]; then
    rm -rf $ssh_key
fi

aws ec2 create-key-pair --key-name $aws_key_name --query 'KeyMaterial' --output text 2>&1 | tee $ssh_key
echo "Setting permissions for ssh key $ssh_key"
chmod 400 $ssh_key

aws cloudformation create-stack --stack-name PROD --template-body file://./ec2.yaml --parameters ParameterKey=KeyName,ParameterValue=$aws_key_name

echo "Creating instance ..."

StackStatus=""
temp_cnt=300

#while [[( "$StackStatus" != "CREATE_COMPLETE" ) && ( $temp_cnt -ne 0 )]];
while [[( "$StackStatus" != CREATE_COMPLETE ) && ( $temp_cnt -ne 0 )]];
do
    printf "\rYou have %2d second(s) remaining to hit Ctrl+C to cancel that operation!" ${temp_cnt}
    StackStatus=$(aws cloudformation describe-stacks --query "Stacks[*].StackStatus" --output=text --stack-name PROD)
    echo "Still waiting. Current status "$StackStatus
    sleep 5
    temp_cnt=$((temp_cnt - 5))
done

ec2_IP=$(aws ec2 describe-instances --query "Reservations[*].Instances[*].PublicIpAddress" --output=text --filter Name=tag:VM,Values=Tomcat)
echo "IP " $ec2_IP

##export ANSIBLE_HOST_KEY_CHECKING=False
##ansible-playbook --key-file aws-test-oregon.pem -i ./inventory/ec2.py -u ec2-user --limit "tag_VM_Tomcat" tomcat.yml
#set +x
