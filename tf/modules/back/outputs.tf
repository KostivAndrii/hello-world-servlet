output "Tomcat_IP" {
  value = "${aws_instance.TomcatInstance.*.public_ip}"
}
output "Zabbix_IP" {
  value = "${aws_instance.ZabbixInstance.*.public_ip}"
}
output "NATGW_IP" {
  value = "${aws_instance.NATGWInstance.*.public_ip}"
}
