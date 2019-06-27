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
