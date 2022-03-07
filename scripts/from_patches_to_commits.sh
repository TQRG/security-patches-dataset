#!/bin/bash

dir=../commits
if [[ ! -e $dir ]]; then
    mkdir $dir
    echo "Creating $dir..."
fi

RESEARCH_DATASETS=("devign" "sap" "bigvul" "secbench")

for dataset in "${RESEARCH_DATASETS[@]}"; do
    cp ../data/$dataset/github-$dataset-patches.csv $dir/$dataset.csv
done

sources_dir=../sources
if [[ ! -e $sources_dir ]]; then
    mkdir $sources_dir
    echo "Creating $sources_dir..."
fi

SOURCES=("cve-details" "nvd" "osv")

for source in "${SOURCES[@]}"; do
    cp ../data/$source/github-$source-patches.csv $sources_dir/$source.csv
done