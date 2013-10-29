#!/bin/bash

for D in $(ls -l | egrep ^d | awk '{print $NF}'); do
    echo "RUNNING TESTS IN $D"
    cd $D
    nosetests -v
    cd ..
done
