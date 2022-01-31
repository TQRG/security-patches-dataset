#!/bin/bash
PYTHON=python3
OUTPUT_FOLDER=../../data/big-vul/
RAW_DATA_FILENAME=big-vul-msr20.csv
PATCHES_DATA_FILENAME=all-big-vul-patches.csv

echo "\nGetting the commits references to github, bitbucket, gitlab and git..."
$PYTHON ../common/references.py --task=commits \
                                --fin=$OUTPUT_FOLDER/$RAW_DATA_FILENAME \
                                --fout=$OUTPUT_FOLDER/$PATCHES_DATA_FILENAME