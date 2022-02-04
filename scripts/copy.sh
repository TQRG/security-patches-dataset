#!/bin/bash

dir=../commits
if [[ ! -e $dir ]]; then
    mkdir $dir
    echo "Creating $dir..."
fi

cp ../data/devign/github-devign-patches.csv $dir/devign.csv

cp ../data/sap/github-sap-patches.csv $dir/sap.csv

cp ../data/big-vul/github-big-vul-patches.csv $dir/big_vul.csv

cp ../data/secbench/secbench.csv $dir/secbench.csv

sources_dir=../sources
if [[ ! -e $sources_dir ]]; then
    mkdir $sources_dir
    echo "Creating $sources_dir..."
fi

cp ../data/cve-details/github-cve-details-patches.csv $sources_dir/cve_details.csv

cp ../data/nvd/github-nvd-patches.csv $sources_dir/nvd.csv

cp ../data/osv/github-osv-patches.csv $sources_dir/osv.csv
