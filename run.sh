#!/bin/bash

# A script to run experimental conditions

if (( $# == 1 )); then

    if [[ ${1} =~ /$ ]] ; then
	dir="${1%/}"
	2>&1 echo -e "Warning:\tAssuming you meant ${prefix} instead of ${1}"
    else
	dir=${1}
    fi

    for file in moses.ini static.pt static.lm client.py summary.txt; do
	if [ ! -e ${dir}/${file} ] ; then
	    2>&1 echo -e "${dir}/${file} is required, but was not found"
	    exit -1
	fi
    done
else
    2>&1 echo -e "Usage: $0 dir"
    exit -1
fi


cd ${dir}

2>&1 echo -e "Condition:\t${dir}"
2>&1 echo
2>&1 cat  summary.txt
2>&1 echo
2>&1 echo
2>&1 echo -e "Launching:\tmosesserver -v 1 -f ${dir}/moses.ini &> ${dir}/log"

../../bin/mosesserver -v 1 -f moses.ini --server-port 8090 &> log &
server_pid=${!}

sleep 0.5

2>&1 echo -e "Launching:\tmoses client.py"
2>&1 echo
./client.py

kill ${server_pid}
