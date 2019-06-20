variable "aws_region" {
  description = "AWS Region"
  default     = "eu-west-3"
}
variable "VPCBlock" {
  description = "VPC CIDR block parameter must be in the form x.x.x.x/16-28"
  default     = "10.0.0.0/16"
}
variable "PublicSubnetCIDR" {
  description = "Public Subnet CIDR"
  default     = "10.0.10.0/24"
}
variable "PrivatSubnetCIDR" {
  description = "Privat Subnet CIDR"
  default     = "10.0.11.0/24"
}
variable "server_port" {
  description = "The port the server will use for HTTP requests"
  default     = 8080
}