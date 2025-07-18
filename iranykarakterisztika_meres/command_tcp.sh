#!/bin/bash
gcc -o pwrmtr power_meter.c -lm
nc -w 2 10.73.19.31 7373 | ./pwrmtr
