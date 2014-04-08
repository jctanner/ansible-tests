#!/bin/bash

THIS_RUN=$(python -m cProfile $( which ansible-playbook )  -i inventory site-one.yml) 
