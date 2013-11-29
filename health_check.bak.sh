#!/bin/bash

echo "Kulcloud Server health checking..."
while [ : ]; 
do
    server_pid=`ps -ef | grep kulcloud-nbapi | grep -v 'grep' | awk '{print $2}'`
    makdi_pid=`ps -ef | grep mulmakdi | grep -v 'grep' | awk '{print $2}'`
    agent_pid=`ps -ef | grep module_check_stat3.py | grep -v 'grep' | awk '{print $2}'`
    echo "server_pid"
    echo "$server_pid"
    echo "agent_pid"
    echo "$agent_pid"
    echo "makdi_pid"
    echo "$makdi_pid"
    sleep 1
done



