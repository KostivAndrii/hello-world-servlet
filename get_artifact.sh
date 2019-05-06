#!/bin/bash

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
