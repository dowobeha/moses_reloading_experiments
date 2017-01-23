#!/bin/bash

# A script to run experimental conditions

if (( $# == 2 )); then

    if [[ ${1} =~ /$ ]] ; then
	staticDir="${1%/}"
	2>&1 echo -e "Warning:\tAssuming you meant ${staticDir} instead of ${1}"
    else
	staticDir=${1}
    fi

    for file in moses.ini ; do
	if [ ! -e ${staticDir}/${file} ] ; then
	    2>&1 echo -e "${staticDir}/${file} is required, but was not found"
	    exit -1
	fi
    done

    if [[ ${2} =~ /$ ]] ; then
	dynamicDir="${2%/}"
	2>&1 echo -e "Warning:\tAssuming you meant ${dynamicDir} instead of ${2}"
    else
	dynamicDir=${2}
    fi

    for file in moses.ini static.pt static.lm client.py summary.txt; do
	if [ ! -e ${dynamicDir}/${file} ] ; then
	    2>&1 echo -e "${dynamicDir}/${file} is required, but was not found"
	    exit -1
	fi
    done


else
    2>&1 echo -e "Usage: $0 staticDir dynamicDir"
    exit -1
fi


cd ${staticDir}

2>&1 echo -e "Condition:\tstatic ${staticDir}\tdynamic ${dynamicDir}"
2>&1 echo
2>&1 cat  summary.txt
2>&1 echo
2>&1 echo
2>&1 echo -e "Launching:\tmosesserver -v 1 -f ${staticDir}/moses.ini &> ../${dynamicDir}/log.${staticDir}"

../../bin/mosesserver -v 1 -f moses.ini --server-port 8090 &> ../${dynamicDir}/log.${staticDir} &
static_server_pid=${!}

sleep 0.5

cd ../${dynamicDir}

2>&1 echo -e "Launching:\tmosesserver -v 1 -f ${dynamicDir}/moses.ini &> log"

echo "-v 3 -f moses.ini --server-port 8091"
gdb ../../bin/mosesserver
