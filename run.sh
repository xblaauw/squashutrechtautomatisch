#!/bin/bash


eval "$($(which conda) 'shell.bash' 'hook')" && \
conda activate squashutrechtautomatisch && \
python -u main.py
