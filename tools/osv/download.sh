#!/bin/bash
GITHUB_TOKEN=TOKEN_PLACEHOLDER

dir=../../data/osv/
rm -rf $dir
if [[ ! -e $dir ]]; then
    mkdir $dir
    echo "Creating $dir..."
fi

cd osv-schema/tools/ghsa/
pipenv sync
pipenv shell
mkdir ../../../GHSA
python3 dump_ghsa.py --token $GITHUB_TOKEN ../../../GHSA
cd ../../..
echo "Extracting data for GHSA..." 
python3 process.py --ecosystem=GHSA --fout=$dir
rm -rf GHSA

ECOSYSTEMS=("DWF" "Go" "Linux" "Maven" "NuGet" "OSS-Fuzz" \
                "PyPI" "RubyGems" "crates.io" "npm")

for ecosystem in "${ECOSYSTEMS[@]}"; do
    gsutil cp gs://osv-vulnerabilities/$ecosystem/all.zip $ecosystem.zip
    mkdir $ecosystem
    unzip $ecosystem.zip -d $ecosystem
    rm $ecosystem.zip
    echo "Extracting data for $ecosystem..." 
    python3 process.py --ecosystem=$ecosystem --fout=$dir
    rm -rf $ecosystem
done

