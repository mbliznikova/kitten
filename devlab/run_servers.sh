#!/usr/bin/env bash

export FLASK_APP=/vagrant/sample.py

screen -dmS servers -t "bash" bash

for port in $(seq 5000 5003); do
    screen  -S servers -X screen screen -t "http-${port}" flask run -p ${port}
done
