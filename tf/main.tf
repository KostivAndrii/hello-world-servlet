terraform {
  required_version = ">= 0.8"
}

provider "aws" {
  region = "${var.aws_region}"
}


resource "aws_vpc" "main" {
  cidr_block = "${var.VPCBlock}"

  tags = {
    Name     = "my-terraform-aws-vpc"
    # Name = "my-terraform-aws-vpc-${terraform.workspace}"
    # Environment = "${terraform.workspace}"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "igw" {
  vpc_id = "${aws_vpc.main.id}"
}

# EIP and NAT Gateway
resource "aws_eip" "nat_eip" {
  vpc      = true
}

resource "aws_nat_gateway" "natgw" {
  allocation_id = "${aws_eip.nat_eip.id}"
  subnet_id     = "${element(aws_subnet.public_subnet.*.id, 1)}"

  depends_on = ["aws_internet_gateway.igw"]
}

resource "aws_subnet" "public_subnet" {
  vpc_id     = "${aws_vpc.main.id}"
  cidr_block = "${var.PublicSubnetCIDR}"

  tags {
    Name = "public_subnet"
    # Name = "public_subnet_${terraform.workspace}"
  }
}
resource "aws_subnet" "privat_subnet" {
  vpc_id     = "${aws_vpc.main.id}"
  cidr_block = "${var.PrivatSubnetCIDR}"

  tags {
    Name = "privat_subnet"
    # Name = "public_subnet_${terraform.workspace}"
  }
}




resource "aws_launch_configuration" "example" {
  image_id        = "ami-0a8e17334212f7052"
  instance_type   = "t2.micro"
  security_groups = ["${aws_security_group.instance.id}"]

  user_data = <<-EOF
              #!/bin/bash
              echo "Hello, World" > index.html
              nohup busybox httpd -f -p "${var.server_port}" &
              EOF

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_autoscaling_group" "example" {
  launch_configuration = "${aws_launch_configuration.example.id}"
  availability_zones   = data.aws_availability_zones.all.names

  load_balancers    = ["${aws_elb.example.name}"]
  health_check_type = "ELB"

  min_size = 2
  max_size = 10

  tag {
    key                 = "Name"
    value               = "terraform-asg-example"
    propagate_at_launch = true
  }
}

resource "aws_security_group" "instance" {
  name = "terraform-example-instance"

  ingress {
    from_port   = "${var.server_port}"
    to_port     = "${var.server_port}"
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  lifecycle {
    create_before_destroy = true
  }
}

data "aws_availability_zones" "all" {}

resource "aws_elb" "example" {
  name               = "terraform-asg-example"
  availability_zones = data.aws_availability_zones.all.names
  security_groups    = ["${aws_security_group.elb.id}"]

  listener {
    lb_port           = 80
    lb_protocol       = "http"
    instance_port     = "${var.server_port}"
    instance_protocol = "http"
  }

  health_check {
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 3
    interval            = 30
    target              = "HTTP:${var.server_port}/"
  }
}

resource "aws_security_group" "elb" {
  name = "terraform-example-elb"

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}