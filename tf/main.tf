terraform {
    required_version = ">= 0.8"
}

provider "aws" {
    region = "${var.aws_region}"
}
module "vpc" {
    source                              = "modules/vpc"
    aws_region     	                    = "eu-west-3"
    STACK                               = "AWS-NATGW"
    Environment                         = "QA"
    KeyName                             = "aws-test-oregon"
    # NATGW_type                          = "t2.micro"
    # NATGW_ami                           = "ami-0ebb3a801d5fb8b9b"
    VPCBlock                            = "10.0.0.0/16"
    PublicSubnetCIDR                    = "10.0.10.0/24"
    PrivatSubnetCIDR                    = "10.0.11.0/24"
    enable_dns_support                  = "true"
    #Internet-GateWay
    enable_internet_gateway             = "true"
    #NAT
    enable_nat_gateway                  = "false"
}

# # EIP and NAT Gateway
# resource "aws_eip" "nat_eip" {
#   vpc      = true
# }
# resource "aws_nat_gateway" "natgw" {
#   allocation_id = "${aws_eip.nat_eip.id}"
#   subnet_id     = "${element(aws_subnet.public_subnet.*.id, 1)}"
#   depends_on = ["aws_internet_gateway.igw"]
# }


# resource "aws_s3_bucket" "terraform-state-storage-s3" {
#     bucket = "tfstate-aws-s3-bucket"
#     versioning {
#       enabled = true
#     }
#     lifecycle {
#       prevent_destroy = true
#     }
#     tags = {
#       Name = "S3 Remote Terraform State Store"
#     }
# }
# resource "aws_dynamodb_table" "terraform_state_lock" {
#   name           = "app-state"
#   read_capacity  = 1
#   write_capacity = 1
#   hash_key       = "LockID"

#   attribute {
#     name = "LockID"
#     type = "S"
#   }
# }
# terraform {
#     backend "s3" {
#         encrypt = true
#         bucket = "tfstate-aws-s3-bucket"
#         region = "eu-west-3"
#         key = "natgw/terraform.tfstate"
#     }
# }

#====== BackEnd instance
resource "aws_instance" "BackEndInstance" {
    ami = "${var.server_ami}"
    instance_type = "${var.server_type}"
    key_name = "${var.KeyName}"

    subnet_id = "${aws_subnet.privat_subnet.id}"
    vpc_security_group_ids = ["${aws_default_security_group.NATGW_sg.id}"]
    tags = {
        STACK = "${var.STACK}"
        Name = "${var.Environment}-BackEnd"
        VM = "BackEnd"
    }
}
#====== Public Servers ====== Tomcat instance
resource "aws_instance" "TomcatInstance" {
    ami = "${var.server_ami}"
    instance_type = "${var.server_type}"
    associate_public_ip_address = "true"
    key_name = "${var.KeyName}"

    subnet_id = "${aws_subnet.public_subnet.id}"
    vpc_security_group_ids = ["${aws_security_group.public_sg.id}"]
    tags = {
        STACK = "${var.STACK}"
        Name = "${var.Environment}-Tomcat"
        VM = "Tomcat"
    }
}
#====== Tomcat instance
resource "aws_instance" "ZabbixInstance" {
    ami = "${var.server_ami}"
    instance_type = "${var.server_type}"
    associate_public_ip_address = "true"
    key_name = "${var.KeyName}"

    subnet_id = "${aws_subnet.public_subnet.id}"
    vpc_security_group_ids = ["${aws_security_group.public_sg.id}"]
    tags = {
        STACK = "${var.STACK}"
        Name = "${var.Environment}-Zabbix"
        VM = "Zabbix"
    }
}
# terraform apply -var-file=vpc.tfvars