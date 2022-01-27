#!/bin/bash
PYTHON=python3
DATA_FOLDER=data/
OUTPUT_FOLDER=../../data/nvd/
RAW_DATA_FILENAME=raw-nvd-data.csv
PATCHES_DATA_FILENAME=all-nvd-patches.csv

echo "Extract and merge data from NVD files..."
$PYTHON cli.py --task=extractor --data=$DATA_FOLDER --fout=$OUTPUT_FOLDER

echo "Process NVD data..."
$PYTHON cli.py --task=process --fin=$OUTPUT_FOLDER/$RAW_DATA_FILENAME \
                                --fout=$OUTPUT_FOLDER/$PATCHES_DATA_FILENAME

                     