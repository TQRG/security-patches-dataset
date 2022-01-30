#!/bin/bash
PYTHON=python3
DATA_FOLDER=../../data/nvd/year/
OUTPUT_FOLDER=../../data/nvd/
RAW_DATA_FILENAME=raw-nvd-data.csv
PATCHES_DATA_FILENAME=all-nvd-patches.csv

echo "Extract and merge data from NVD files..."
$PYTHON cli.py --task=extractor --data=$DATA_FOLDER --fout=$OUTPUT_FOLDER

echo "\nProcess references ..."
$PYTHON ../common/references.py --task=process \
                                --fin=$OUTPUT_FOLDER/$RAW_DATA_FILENAME \
                                --fout=$OUTPUT_FOLDER/$RAW_DATA_FILENAME

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
      