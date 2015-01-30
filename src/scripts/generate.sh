#!/bin/bash
echo 'Generating 1 channel signed 16 bit 48000 sampling rate 5 ' \
     'seconds 1 Hz test data...'
sox -b 16 -r 48000 -c 1 -n /tmp/1hz.raw synth 5 sine 1
echo 'Generating 1 channel signed 16 bit 48000 sampling rate 5 ' \
     'seconds 1K Hz, amplidute = 0.1 * full amplitude test data...'
sox -b 16 -r 48000 -c 1 -n /tmp/10hz.raw synth 5 sine 10
sox -e signed -b 16 -r 48000 -c 1 -v 0.001 /tmp/10hz.raw -b 16 -r 48000 -c 1 /tmp/10hz_small.raw
