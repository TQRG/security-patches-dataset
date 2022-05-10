#!/bin/bash
GITHUB_TOKEN=$(jq '.token' config/github.json)

dir=../../data/osv/
file=raw-osv-data.csv
rm $dir/*.csv
if [[ ! -e $dir ]]; then
    mkdir $dir
    echo "Creating $dir"
fi

cd osv-schema/tools/ghsa/
mkdir ../../../GHSA
python3 dump_ghsa.py --token "${GITHUB_TOKEN//\"}" ../../../GHSA
cd ../../..
echo "Extracting data for GHSA..." 
python3 process.py --ecosystem=GHSA --fout=$dir/$file
rm -rf GHSA

ECOSYSTEMS=("DWF" "Go" "Linux" "Maven" "NuGet" "OSS-Fuzz" \
                "PyPI" "RubyGems" "crates.io" "npm" "GSD" "Hex" "Packagist")

for ecosystem in "${ECOSYSTEMS[@]}"; do
    gsutil cp gs://osv-vulnerabilities/$ecosystem/all.zip $ecosystem.zip
    mkdir $ecosystem
    unzip $ecosystem.zip -d $ecosystem
    rm $ecosystem.zip
    echo "Extracting data for $ecosystem..." 
    python3 process.py --ecosystem=$ecosystem --fout=$dir/$file
    rm -rf $ecosystem
done

