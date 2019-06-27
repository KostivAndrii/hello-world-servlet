terraform {
    required_version = ">= 0.8"
}

provider "aws" {
    region = "${var.aws_region}"
}

resource "aws_vpc" "main" {
    cidr_block = "${var.VPCBlock}"

    tags = {
        Name     = "${var.Environment}-vpc"
    }
}
# Internet Gateway
resource "aws_internet_gateway" "igw" {
    vpc_id = "${aws_vpc.main.id}"

    tags = {
        Name     = "${var.Environment}-IGW"
    }
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

#==================================================== Public Subnet =========
resource "aws_subnet" "public_subnet" {
    vpc_id     = "${aws_vpc.main.id}"
    cidr_block = "${var.PublicSubnetCIDR}"

    tags = {
        Name = "${var.Environment}-public_subnet"
    }
}
#====== Public RouteTables ========= Routes for Public Subnet RouteTables with IGW =========
resource "aws_route_table" "public_route" {
    vpc_id = "${aws_vpc.main.id}"
    tags = {
        Name = "${var.Environment}-PublicRouteTables"
    }

    route {
        cidr_block = "0.0.0.0/0"
        gateway_id = "${aws_internet_gateway.igw.id}"
    }
}
resource "aws_route_table_association" "public_route_assoc" {
    subnet_id = "${aws_subnet.public_subnet.id}"
    route_table_id = "${aws_route_table.public_route.id}"
}
#==================================================== Privat Subnet =========
resource "aws_subnet" "privat_subnet" {
    vpc_id     = "${aws_vpc.main.id}"
    cidr_block = "${var.PrivatSubnetCIDR}"

    tags = {
        Name = "${var.Environment}-privat_subnet"
    }
}
#====== Privat RouteTables ========= Routes for Privat Subnet RouteTables with NATGW =========
resource "aws_default_route_table" "privat_route" {
    default_route_table_id = "${aws_vpc.main.default_route_table_id}"
    tags = {
        Name = "${var.Environment}-PrivatRouteTables"
    }

    route {
        cidr_block = "0.0.0.0/0"
        # gateway_id = "${aws_internet_gateway.igw.id}"
        instance_id = "${aws_instance.NATGWInstance.id}"
    }
    depends_on = ["aws_instance.NATGWInstance"]
}
resource "aws_route_table_association" "privat_route_assoc" {
    subnet_id = "${aws_subnet.privat_subnet.id}"
    route_table_id = "${aws_default_route_table.privat_route.id}"
}
#====== NAT GW SecurityGroup
resource "aws_default_security_group" "NATGW_sg" {
    # aws_default_security_group
    # name = "natgw_sg"
    tags = {
        Name = "${var.Environment}-natgw_sg"
    }
    # description = "Connections for the nat instance"
    vpc_id = "${aws_vpc.main.id}"
    ingress {
        from_port   = "0"
        to_port     = "0"
        protocol    = "-1"
        cidr_blocks = ["${var.VPCBlock}"]
    }
    ingress {
        from_port   = "22"
        to_port     = "22"
        protocol    = "TCP"
        cidr_blocks = ["0.0.0.0/0"]
    }
    egress {
        from_port = 0
        to_port = 0
        protocol = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }
}
#====== NAT GW instance
resource "aws_instance" "NATGWInstance" {
    ami = "${var.NATGW_ami}"
    instance_type = "${var.NATGW_type}"
    associate_public_ip_address = "true"
    key_name = "${var.KeyName}"

    subnet_id = "${aws_subnet.public_subnet.id}"
    vpc_security_group_ids = ["${aws_default_security_group.NATGW_sg.id}"]
    source_dest_check = "false"
    user_data = <<-EOF
                #!/bin/bash -xe
                #sed -i "s/net.ipv4.ip_forward = 0/net.ipv4.ip_forward = 1/" /etc/sysctl.conf
                echo "net.ipv4.ip_forward = 1" >> /etc/sysctl.conf
                sysctl -p
                echo "iptables -t nat -A POSTROUTING -s ${var.VPCBlock} -j MASQUERADE" >> /etc/rc.local
                iptables -t nat -A POSTROUTING -s ${var.VPCBlock} -j MASQUERADE
                EOF
    tags = {
        STACK = "${var.STACK}"
        Name = "${var.Environment}-NATGW"
        VM = "NATGW"
    }
}
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
#====== Public SecurityGroup
resource "aws_security_group" "public_sg" {
    name = "public_sg"
    tags = {
        Name = "${var.Environment}-public_sg"
    }
    description = "Connections for the nat instance"
    vpc_id = "${aws_vpc.main.id}"
    ingress {
        from_port   = "80"
        to_port     = "80"
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }
    ingress {
        from_port   = "8080"
        to_port     = "8080"
        protocol    = "TCP"
        cidr_blocks = ["0.0.0.0/0"]
    }
    ingress {
        from_port   = "1050"
        to_port     = "1052"
        protocol    = "TCP"
        cidr_blocks = ["0.0.0.0/0"]
    }
    ingress {
        from_port   = "12345"
        to_port     = "12345"
        protocol    = "TCP"
        cidr_blocks = ["0.0.0.0/0"]
    }
    ingress {
        from_port   = "0"
        to_port     = "0"
        protocol    = "-1"
        cidr_blocks = ["${var.VPCBlock}"]
    }
    egress {
        from_port = 0
        to_port = 0
        protocol = "-1"
        cidr_blocks = ["0.0.0.0/0"]
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
# terraform apply -var-file=vpc.tfvars
# terraform apply -var-file=vpc.tfvars

# # terraform apply -var-file=vpc.tfvars
# #  + resource "aws_default_route_table" "privat_route"
# #  + resource "aws_route_table_association" "privat_route_assoc"
# #  + resource "aws_route_table_association" "public_route_assoc"

#  terraform import aws_vpc.main vpc-0321ac1bf77541e1b
#  terraform import aws_internet_gateway.igw igw-0e26e3d3a372db2a3
#  terraform import aws_subnet.public_subnet subnet-0f171c69415460292
#  terraform import aws_route_table.public_route rtb-05c5f728d093a14c5
#  terraform import aws_subnet.privat_subnet subnet-011ce27b4b5ab99ae
#  terraform import aws_default_route_table.privat_route rtb-0668aebf872babd2c
#  Error: resource aws_default_route_table doesn't support import
#  terraform import aws_default_security_group.NATGW_sg sg-0d2b33d50a1d8cbb4
#  terraform import aws_security_group.public_sg sg-05ac91ba1b74c5df9
#  terraform import aws_instance.NATGWInstance i-085c6fb72a0838288
#  terraform import aws_instance.BackEndInstance i-022e2ef5b62595a2b
#  terraform import aws_instance.TomcatInstance i-01b6c51bc96504b47
#  terraform import aws_instance.ZabbixInstance i-0645ad50701f0b3ed