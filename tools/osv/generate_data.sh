#!/bin/bash
PYTHON=python3
OUTPUT_FOLDER=../../data/osv/
RAW_DATA_FILENAME=raw-osv-data.csv
PATCHES_DATA_FILENAME=all-osv-patches.csv

echo "\nGetting the commits references to github, bitbucket, gitlab and git..."
$PYTHON ../common/references.py --task=commits \
                                --fin=$OUTPUT_FOLDER/$RAW_DATA_FILENAME \
                                --fout=$OUTPUT_FOLDER/$PATCHES_DATA_FILENAME

echo "\nGenerating data statistics..."
$PYTHON ../common/references.py --task=stats  \
                                --fin=$OUTPUT_FOLDER/$PATCHES_DATA_FILENAME

echo "\nCleaning the data..."
$PYTHON ../common/references.py --task=normalize \
                                --fin=$OUTPUT_FOLDER/$PATCHES_DATA_FILENAME 
      