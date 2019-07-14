#!/bin/bash

serv=$1
echo "Check service(s):  $serv"
check_status=0

for var in $serv
do
    active_status=$(/bin/systemctl is-active $var)
    enabled_status=$(/bin/systemctl is-enabled $var)

    if [[ $active_status == "active" && $enabled_status == "enabled" && check_status -eq 0 ]]; then
                echo "OK - $var service status"
                check_status=0
        elif [[ $active_status == "active" && $enabled_status != "enabled" && check_status -le  1 ]]; then
                echo "WARNING - $var service status"
                check_status=1
        elif [[ $active_status != "active" && check_status -le  2 ]]; then
                echo "CRITICAL - $var service status"
                check_status=2
        else
                echo "UNKNOWN - $var : $active_status $enabled_status"
                exit 3
    fi
done


case "$check_status" in
    0) exit 0 ;;
    1) exit 1 ;;
    2) exit 2 ;;
esac
#=====================================================================
#!/bin/bash

serv=$1
echo "serv $serv"
check_status=""


for var in $serv
do
echo The  $var item
done

active_status=$(/bin/systemctl is-active $serv)
enabled_status=$(/bin/systemctl is-enabled $serv)

if [[ $active_status == "active" && $enabled_status == "enabled" ]]; then
                echo "OK - $serv service status"
                exit 0
        elif [[ $active_status == "active" && $enabled_status != "enabled" ]]; then
                echo "WARNING - $serv service status"
                exit 1
        elif [[ $active_status != "active" ]]; then
                echo "CRITICAL - $serv service status"
                exit 2
        else
                echo "UNKNOWN - $serv : $active_status $enabled_status"
                exit 3
fi