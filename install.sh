#!/usr/bin/env bash

if [ "$EUID" -ne 0 ]
then echo "Usage: sudo ./install.sh"
	 exit
fi
install tocc.py /usr/bin/tocc
