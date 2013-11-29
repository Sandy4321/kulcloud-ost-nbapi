#!/bin/bash
while [ 1 ]
  do
    PID='ps ex|grep "module_check_stat.py"|grep -v 'grep'|awk {print $1}'
    if [ "$PID" == "" ];
    then
      CMD='python module_check_stat.py'
    else
      echo "what..."
    fi
      sleep 5
  done
