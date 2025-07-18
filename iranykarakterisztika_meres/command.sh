gcc -o pwrmtr power_meter.c -lm
rtl_sdr -f 438300000 -g 40 - | ./pwrmtr
