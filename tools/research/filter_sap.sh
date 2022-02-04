#!/bin/bash
PYTHON=python3
OUTPUT_FOLDER=../../data/sap
RAW_DATA_FILENAME=pontas-msr19.csv
COMMITS_DATA_FILENAME=all-sap-patches.csv
DATASET=sap

python3 process.py --root-folder=$OUTPUT_FOLDER \
                    --fin=$RAW_DATA_FILENAME \
                    --name=$DATASET

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
                                --dataset=$DATASET 