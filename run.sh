#!/bin/bash

BASEDIR="/home/picam/dht11adaf"

if [ -n "$VIRTUAL_ENV" ]; then
    echo "Yes, a Python virtual environment is active."
    echo "Venv path: $VIRTUAL_ENV"
    cd $BASEDIR
    if [ -f "./dht11adafruit/dht11adaf.py" ]; then
        echo "Running dht11adaf.py"
        python3 ./dht11adafruit/dht11adaf.py
    else
        echo "Error: dht11adaf.py not found in $BASEDIR"
    fi
else
    echo "No, no virtual environment is active."
    echo "Activating Now"
    cd $BASEDIR
    source ./bin/activate
    if [ -f "./dht11adafruit/dht11adaf.py" ]; then
        echo "Running dht11adaf.py"
        python3 ./dht11adafruit/dht11adaf.py
    else
        echo "Error: dht11adaf.py not found in $BASEDIR"
    fi
fi