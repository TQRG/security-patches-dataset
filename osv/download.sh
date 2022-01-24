#!/bin/bash
GITHUB_TOKEN=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

cd osv-schema/tools/ghsa/
pipenv sync
pipenv shell
mkdir ../../../GHSA
python3 dump_ghsa.py --token $GITHUB_TOKEN ../../../GHSA
cd ../../..

ECOSYSTEMS=("DWF" "Go" "Linux" "Maven" "NuGet" "OSS-Fuzz" \
                "PyPI" "RubyGems" "crates.io" "npm")

for ecosystem in "${ECOSYSTEMS[@]}"; do
    gsutil cp gs://osv-vulnerabilities/$ecosystem/all.zip $ecosystem.zip
    mkdir $ecosystem
    unzip $ecosystem.zip -d $ecosystem
    rm $ecosystem.zip
done