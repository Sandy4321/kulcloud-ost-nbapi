#!/bin/bash

echo "Kulcloud Server health checking..."
while [ : ]; 
do
    server_pid=`ps -ef | grep kulcloud-nbapi | grep -v 'grep' | awk '{print $2}'`
    agent_pid=`ps -ef | grep module_check_stat3.py | grep -v 'grep' | awk '{print $2}'`
    makdi_pid=`ps -ef | grep mulmakdi | grep -v 'grep' | awk '{print $2}'`
    if [ -z $server_pid ]; then
        echo "Kulcloud server Application Stopped."
        ./start.sh &
        date >> webserver.log
        kill -9 $makdi_pid
        pushd /usr/src/mul-nbapi/application/makdi/ >> /dev/null
        sudo ./mulmakdi -d
        popd >> /dev/null
    else
        echo "Kulcloud server Application running."
    fi
    if [ -z $agent_pid ]; then
        echo "Kulcloud Agent Application Stopped."
        pushd /usr/src/kulcloud-nbapi/ >> /dev/null
        python module_check_stat3.py &
        popd >> /dev/null
    else
        echo "Kulcloud Agent Application running."
    fi
    #if [ -z $makdi_pid ]; then
    #    echo "Kulcloud Makdi Application Stopped."
    #    pushd /usr/src/mul-nbapi/application/makdi/ >> /dev/null
    #    sudo ./mulmakdi -d
    #    popd >> /dev/null
    #else
    #    echo "Kulcloud Makdi Application running."
    #fi
    #if [ -z $agent_pid ]; then
    #    echo "Kulcloud Agent Application Stopped."
    #    pushd /usr/src/kulcloud-nbapi >> /dev/null
    #    python module_check_stat.py &
    #    popd >> /dev/null
    #else
    #    echo "Kulcloud Agent Application running."
    #fi
    sleep 1
done
