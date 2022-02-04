#!/bin/bash
PYTHON=python3
OUTPUT_FOLDER=../../data/devign/
PROJECTS=../../data/devign/projects/

$PYTHON process.py --root-folder=$OUTPUT_FOLDER \
                    --projects=$PROJECTS \
                    --name=devign
                    