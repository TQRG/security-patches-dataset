 #!/bin/bash
PYTHON=python3
CVE_DATA_FOLDER=data/
CVE_DATA_OUT_FILENAME=cve_details_data.csv
CVE_PATCHES_OUT_FILENAME=cve_details_patches.csv
SOURCE=github

echo "Merging data scraped per year from the cve details database..."
$PYTHON merge_cve_data.py -folder $CVE_DATA_FOLDER \
                            -file $CVE_DATA_OUT_FILENAME

echo "\nGetting the patches with references to github, bitbucket and gitlab..."
$PYTHON get_patches_data.py --task filter \
                                -fin ../dataset/$CVE_DATE_OUT_FILENAME \
                                -fout ../dataset/all_$CVE_PATCHES_OUT_FILENAME

echo "\nGenerating data statistics..."
$PYTHON get_patches_data.py --task stats  \
                                -fin ../dataset/all_$CVE_PATCHES_OUT_FILENAME
                     