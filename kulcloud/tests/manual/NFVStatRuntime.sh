#!/bin/sh

time1_total=`date +%s.%N`
URL=http://localhost:8181/1.0/NFVDB/stats/ALL
while [ : ]; 
do
    time1=`date +%s.%N`
    curl -X GET -H "Content-Type: application/json" $URL
    time2=`date +%s.%N`
    diff=`echo "$time2 - $time1" | bc`
    htime=`echo "$diff/3600" | bc`
    mtime=`echo "($diff/60) - ($diff * 60)" | bc`
    stime=`echo "$diff - (($diff/60) * 60)" | bc`
    echo "##  RUNNING TIME : ${stime}. " >> NFVStat.log
    sleep 1
done
