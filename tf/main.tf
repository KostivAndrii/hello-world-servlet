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
        # Name = "my-terraform-aws-vpc-${terraform.workspace}"
        # Environment = "${terraform.workspace}"
    }
}
# Internet Gateway
resource "aws_internet_gateway" "igw" {
    vpc_id = "${aws_vpc.main.id}"

    tags = {
        Name     = "${var.Environment}-IGW"
        # Name = "my-terraform-aws-vpc-${terraform.workspace}"
        # Environment = "${terraform.workspace}"
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
        # Name = "public_subnet_${terraform.workspace}"
    }
}
#====== Public RouteTables ========= Routes for Public Subnet RouteTables with IGW =========
resource "aws_default_route_table" "public_route" {
    default_route_table_id = "${aws_vpc.main.default_route_table_id}"
    tags = {
        Name = "${var.Environment}-PublicRouteTables"
        # Name = "PublicRouteTables_${terraform.workspace}"
    }

    route {
        cidr_block = "0.0.0.0/0"
        gateway_id = "${aws_internet_gateway.igw.id}"
    }
}
resource "aws_route_table_association" "public_route_assoc" {
    subnet_id = "${aws_subnet.public_subnet.id}"
    route_table_id = "${aws_default_route_table.public_route.id}"
}
#==================================================== Privat Subnet =========
resource "aws_subnet" "privat_subnet" {
    vpc_id     = "${aws_vpc.main.id}"
    cidr_block = "${var.PrivatSubnetCIDR}"

    tags = {
        Name = "${var.Environment}-privat_subnet"
        # Name = "public_subnet_${terraform.workspace}"
    }
}
#====== Privat RouteTables ========= Routes for Privat Subnet RouteTables with NATGW =========
resource "aws_route_table" "privat_route" {
    vpc_id = "${aws_vpc.main.id}"
    tags = {
        Name = "${var.Environment}-PrivatRouteTables"
        # Name = "PrivatRouteTables_${terraform.workspace}"
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
    route_table_id = "${aws_route_table.privat_route.id}"
}
#====== NAT GW SecurityGroup
resource "aws_security_group" "NATGW_sg" {
    name = "natgw_sg"
    tags = {
        Name = "${var.Environment}-natgw_sg"
    }
    description = "Connections for the nat instance"
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
    vpc_security_group_ids = ["${aws_security_group.NATGW_sg.id}"]
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
    vpc_security_group_ids = ["${aws_security_group.NATGW_sg.id}"]
    tags = {
        Name = "${var.Environment}-BackEnd"
        VM = "BackEnd"
    }
}
#====== Public SecurityGroup
resource "aws_default_security_group" "public_sg" {
      # name = "public_sg"
    tags = {
        Name = "${var.Environment}-public_sg"
    }
    # description = "Connections for the nat instance"
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
    vpc_security_group_ids = ["${aws_default_security_group.public_sg.id}"]
    tags = {
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
    vpc_security_group_ids = ["${aws_default_security_group.public_sg.id}"]
    tags = {
        Name = "${var.Environment}-Zabbix"
        VM = "Zabbix"
    }
}
# terraform apply -var-file=vpc.tfvars