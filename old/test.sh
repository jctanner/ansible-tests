#!/bin/bash

FAILURES=""

for D in $(ls -l | egrep ^d | awk '{print $NF}'); do
    echo "RUNNING TESTS IN $D"
    cd $D
    nosetests -v
    result=$?
    if [ "$result" != "0" ]; then
        FAILURES="$FAILURES;result"
    fi
    cd ..
    echo ""
done


echo "FAILURES: $FAILURES"
