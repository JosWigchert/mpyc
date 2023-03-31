#!/bin/bash

python3 pseudoinverse.py "$@"
python3 np_id3gini.py "$@"
python3 np_lpsolver.py "$@"
python3 np_lpsolverfxp.py "$@"
python3 np_bnnmnist.py -d0 "$@"
python3 np_cnnmnist.py 1.5 "$@"
python3 np_aes.py -1 "$@"
python3 np_onewayhashchains.py -k2 "$@"
python3 sha3.py "$@"
