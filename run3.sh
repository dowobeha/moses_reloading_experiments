#!/bin/bash

# A script to run experimental conditions

if (( $# == 1 )); then

    if [[ ${1} =~ /$ ]] ; then
	workingDir="${1%/}"
	2>&1 echo -e "Warning:\tAssuming you meant ${workingDir} instead of ${1}"
    else
	workingDir=${1}
    fi

    for file in moses.0.s.ini moses.1.s.ini \ 
                moses.0.d.ini moses.1.d.ini \
                static.0.pt static.1.pt \
                static.0.lm \
        ; do
        if [ ! -e ${workingDir}/${file} ] ; then
            2>&1 echo -e "${workingDir}/${file} is required, but was not found"
            exit -1
        fi
    done

else
    2>&1 echo -e "Usage: $0 workingDir"
    exit -1
fi


cd ${workingDir}

2>&1 echo -e "Condition:\t${workingDir}"
2>&1 echo
2>&1 cat  /summary.txt
2>&1 echo
2>&1 echo
2>&1 echo -e "Launching:\tmosesserver -v 1 -f moses.0.s.ini &> log.0.s"

../../bin/mosesserver -v 1 -f moses.0.s.ini --server-port 8081 &> log.0.s &
static_server_0_pid=${!}

sleep 0.5

2>&1 echo -e "Launching:\tmosesserver -v 1 -f moses.1.s.ini &> log.1.s"

../../bin/mosesserver -v 1 -f moses.1.s.ini --server-port 8082 &> log.1.s &
static_server_1_pid=${!}

sleep 0.5

2>&1 echo -e "Launching:\tmosesserver -v 1 -f moses.0.d.ini &> log.0.d"

../../bin/mosesserver -v 1 -f moses.0.d.ini --server-port 8083 &> log.0.d &
dynamic_server_0_pid=${!}

sleep 0.5

2>&1 echo -e "Launching:\tmosesserver -v 1 -f moses.1.s.ini &> log.1.d"

../../bin/mosesserver -v 1 -f moses.1.d.ini --server-port 8084 &> log.1.d &
dynamic_server_1_pid=${!}

sleep 0.5


2>&1 echo -e "Launching:\tmoses client.py"
2>&1 echo
./client.py

#set -o xtrace

#echo "Killing ${static_server_pid} and ${dynamic_server_pid}"
kill ${static_server_0_pid} || echo "Failed to kill static Moses server ${static_server_0_pid}"
kill ${static_server_1_pid} || echo "Failed to kill static Moses server ${static_server_1_pid}"
kill ${dynamic_server_0_pid} || echo "Failed to kill dynamic Moses server ${dynamic_server_0_pid}"
kill ${dynamic_server_1_pid} || echo "Failed to kill dynamic Moses server ${dynamic_server_1_pid}"
