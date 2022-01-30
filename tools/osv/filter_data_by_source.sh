#!/bin/bash
PYTHON=python3
DATA_FOLDER=../../data/osv
PATCHES_DATA_FILENAME=all-osv-patches.csv
DATASET=osv

if [ "$1" = "github" ] || [ "$1" = "bitbucket" ] || [ "$1" = "gitlab" ] || [ "$1" = "git" ]; then
    echo "Filtering patches for ${1}..."
    $PYTHON ../common/references.py --task=filter \
                                --fin=$DATA_FOLDER/$PATCHES_DATA_FILENAME \
                                --source=$1  \
                                --dataset=$DATASET
else
    echo "Unkown source"
fi

                  

