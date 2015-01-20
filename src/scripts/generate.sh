#!/bin/bash
echo 'Generating 1 channel signed 16 bit 48000 sampling rate 5 ' \
     'seconds 1 Hz test data...'
sox -b 16 -r 48000 -c 1 -n /tmp/1hz.raw synth 5 sine 1
