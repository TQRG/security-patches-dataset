#!/bin/bash
PYTHON=python3
OUTPUT_FOLDER=../../data/big-vul/
RAW_DATA_FILENAME=big-vul-msr20.csv
COMMITS_DATA_FILENAME=all-bigvul-patches.csv

python3 process.py --root-folder=$OUTPUT_FOLDER \
                    --fin=$RAW_DATA_FILENAME \
                    --fout=$COMMITS_DATA_FILENAME \
                    --name=big_vul

echo "\nGetting the commits references to github, bitbucket, gitlab and git..."
$PYTHON ../common/references.py --task=commits \
                                --fin=$OUTPUT_FOLDER/$COMMITS_DATA_FILENAME \
                                --fout=$OUTPUT_FOLDER/$COMMITS_DATA_FILENAME

echo "\nGenerating data statistics..."
$PYTHON ../common/references.py --task=stats  \
                                --fin=$OUTPUT_FOLDER/$COMMITS_DATA_FILENAME

echo "Filtering patches for Github..."
$PYTHON ../common/references.py --task=filter \
                                --fin=$OUTPUT_FOLDER/$COMMITS_DATA_FILENAME \
                                --source=github \
                                --dataset=big-vul 