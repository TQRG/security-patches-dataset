#!/bin/bash

dir=../../data/nvd/year
rm -rf $dir
if [[ ! -e $dir ]]; then
    mkdir $dir
    echo "Creating $dir..."
fi

for i in $(seq 2002 2022); do 
    wget -P $dir https://nvd.nist.gov/feeds/json/cve/1.1/nvdcve-1.1-$i.json.zip 
    mv $dir/nvdcve-1.1-$i.json.zip $dir/nvdcve-1.1-$i.zip
    unzip $dir/nvdcve-1.1-$i.zip -d $dir
    rm $dir/nvdcve-1.1-$i.zip
done