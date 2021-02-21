#!/bin/bash

cd core/c_ext/
sudo python3 setup.py install
cd ../../



green="\033[1;32m"
cc="\033[0m"

run=false

while getopts ":r:s:" opt; do
	case $opt in
		r) run=true
		   script="$OPTARG"
		;;
		s) run=true
		   script="$OPTARG"
		;;
		\?) echo "Invalid Argument -$OPTARG"
		    exit 1
		;;
	esac
done



if $run == true; 
then
	printf "\n${green}Running script: $script${cc}\n\n"
	python3 $script
fi

