 #!/bin/bash
PYTHON=python3
CVE_PATCHES_OUT_FILENAME=cve_details_patches.csv

if [ "$1" = "github" ] || [ "$1" = "bitbucket" ] || [ "$1" = "gitlab" ]; then
    echo "Filtering patches for ${1}..."
    $PYTHON get_patches_data.py --task source \
                                -fin ../data/all_$CVE_PATCHES_OUT_FILENAME \
                                -source $1   
else
    echo "Unkown source"
fi

                  

