#!/bin/bash

aws_image_id="ami-0dd7e7ed60da8fb83"
i_type="t2.micro"
aws_key_name="aws-test-oregon"
ssh_key="aws-test-oregon.pem"
sec_name=JenkinsSG
sec_desc="Jenkins SG"

release=$1
echo 'release ' $release

url_r='http://artifactory:8081/artifactory/libs-release-local/com/geekcap/vmturbo/hello-world-servlet-example/'
url_s='http://artifactory:8081/artifactory/libs-snapshot-local/com/geekcap/vmturbo/hello-world-servlet-example/'

IS_RELEASE=$(echo ${release} | sed -n 's/.*\(RELEASE\).*/\1/p')

if [[ "$IS_RELEASE" == "RELEASE" ]]; then
    folder=$(echo $release | sed -n 's/.*example-\(.*\).war/\1/p')
    url=${url_r}${folder}'/'${release}
else
    version=$(echo $release | cut -d- -f5)
    url=${url_s}${version}'-SNAPSHOT/'${release}
fi

rm -f hello-world.war

curl $url > hello-world.war

#wget $url

#echo 'url ' $url

#rm -rf $ssh_key

aws ec2 create-key-pair --key-name $aws_key_name --query 'KeyMaterial' --output text 2>&1 | tee $ssh_key
echo "Setting permissions for ssh key $ssh_key"
chmod 400 $ssh_key

aws cloudformation create-stack --stack-name PROD --template-body file://./ec2.yaml --parameters ParameterKey=KeyName,ParameterValue=$aws_key_name

##echo "Creating sec group $sec_name"
##ec2_sg=$(aws ec2 create-security-group --group-name $sec_name --description "$sec_desc")

##echo $ec2_sg > ec2_sg.txt
##sec_ids=$(echo $ec2_sg | sed -n 's/.*GroupId": "\(.*\)" .*/\1/p')
##echo 'sec group ids ' $sec_ids

##echo "add 22 and 8080 rule"
##aws ec2 authorize-security-group-ingress --group-name $sec_name --protocol tcp --port 22 --cidr 0.0.0.0/0
##aws ec2 authorize-security-group-ingress --group-name $sec_name --protocol tcp --port 8080 --cidr 0.0.0.0/0

echo "Creating instance ..."
##ec2_id=$(aws ec2 run-instances --image-id $aws_image_id --count 1 --instance-type $i_type --key-name $aws_key_name --security-group-ids "$sec_ids" --associate-public-ip-address)
##echo  $ec2_id > ec2_id.txt

##inst_ids=$(echo $ec2_id | sed -n 's/.*InstanceId": "\(.*\)", "ImageId.*/\1/p')
##echo 'InstanceId: '$inst_ids

##echo "Obtaining instance description ..."
#ec2_IP=$(aws ec2 describe-instances --instance-ids $inst_ids | sed -n 's/.*PublicIpAddress": "\(.*\)".*/\1/p')
##echo 'PublicIpAddress: '$ec2_IP
#ec2_IP=$(aws ec2 describe-instances --query "Reservations[*].Instances[*].PublicIpAddress" --output=text --filter Name=tag:VM,Values=Tomcat)

countdown_timer=120
temp_cnt=${countdown_timer}
while [[ ${temp_cnt} -gt 0 ]];
do
    printf "\rYou have %2d second(s) remaining to hit Ctrl+C to cancel that operation!" ${temp_cnt}
    sleep 1
    ((temp_cnt--))
done

ec2_IP=$(aws ec2 describe-instances --query "Reservations[*].Instances[*].PublicIpAddress" --output=text --filter Name=tag:VM,Values=Tomcat)

echo "IP " $ec2_IP
#scp -o "StrictHostKeyChecking no" -i $ssh_key ./target/helloworld.war ec2-user@$ec2_IP:/home/ec2-user
scp -o "StrictHostKeyChecking no" -i $ssh_key ./hello-world.war ec2-user@$ec2_IP:/home/ec2-user

## ansible-playbook --key-file aws-test-oregon.pem -i ./inventory/ec2.py -u ec2-user --limit "tag_VM_Tomcat" tomcat.yml

#aws cloudformation delete-stack --stack-name PROD
#ssh -o "StrictHostKeyChecking no" -i aws-test-key.pem ec2-user@$ec2_IP
#aws ec2 create-key-pair --key-name aws-test-key --query 'KeyMaterial' --output text 2>&1 | tee aws-test-key.pem
