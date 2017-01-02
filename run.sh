#!/bin/bash

# A script to run experimental conditions

if (( $# == 1 )); then

    if [[ ${1} =~ .$ ]] ; then
	prefix="${1%.}"
	2>&1 echo -e "Warning:\tAssuming you meant ${prefix} instead of ${1}"
    else
	prefix=${1}
    fi

    for suffix in ini pt lm py txt; do
	if [ ! -e ${prefix}.${suffix} ] ; then
	    2>&1 echo -e "${prefix}.${suffix} is required, but was not found"
	    exit -1
	fi
    done
else
    2>&1 echo -e "Usage: $0 file_prefix"
    exit -1
fi



clear

2>&1 echo -e "Condition:\t${prefix}"
2>&1 echo
2>&1 cat  ${prefix}.txt
2>&1 echo
2>&1 echo
2>&1 echo -e "Launching:\tmosesserver -v 1 -f ${prefix}.ini &> ${prefix}.log"

../bin/mosesserver -v 1 -f ${prefix}.ini --server-port 8090 &> ${prefix}.log &
server_pid=${!}

sleep 0.5

2>&1 echo -e "Launching:\tmoses client ${prefix}.py"
2>&1 echo
./${prefix}.py

kill ${server_pid}
