#!/bin/bash

ScriptDir=$(cd $(dirname $0); pwd)
#DataDir='/pcap7/vulndb'
DataDir="$ScriptDir/data"
today=`date +"%Y%m%d"`
hour=`date +"%H"`
hourago=`date -d '1 hour ago' +"%H"`
yesterday=`date -d '1 day ago' +"%Y%m%d"`
lastmonth=`date -d '1 day ago' +"%Y-%m"`
month=`date +"%Y-%m"`

if [[ $hour = "00" ]]; then
    files=`find ${DataDir}/${lastmonth} | grep ${yesterday}_${hourago}`
else
    files=`find ${DataDir}/${month} | grep ${today}_${hourago}`
fi

echo "$files" | while read file
do
    ${ScriptDir}/insert2db.py $file
done

