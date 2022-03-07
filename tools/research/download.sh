#!/bin/bash

RESEARCH_DATASETS=("devign" "sap" "bigvul" "secbench")

for dataset in "${RESEARCH_DATASETS[@]}"; do
    dir=../../data
    if [[ ! -e $dir/$dataset/ ]]; then
        mkdir $dir/$dataset/
        echo "Creating $dir..."
    fi
done

wget -O ../../data/big-vul/big-vul-msr20.csv https://github.com/ZeoVan/MSR_20_Code_vulnerability_CSV_Dataset/raw/master/all_c_cpp_release2.0.csv

wget -O ../../data/secbench/secbench.csv https://github.com/TQRG/secbench/raw/master/dataset/secbench.csv
mv ../../data/secbench/secbench.csv ../../data/secbench/github-secbench-patches.csv

wget -O ../../data/sap/pontas-sap-msr19.csv https://github.com/SAP/project-kb/raw/master/MSR2019/dataset/vulas_db_msr2019_release.csv
echo "$(echo -n 'cve_id,project,sha,type\n'; cat ../../data/sap/pontas-sap-msr19.csv)" > ../../data/sap/pontas-sap-msr19.csv

gdown -O ../../data/devign/projects/ https://drive.google.com/uc\?id\=1Nk_U52_gVHYfnNk-pcXlnxssOBrmSllV

gdown -O ../../data/devign/projects/ https://drive.google.com/uc\?id\=1RhyA-cZl2oiNb-IJOHYw4waBgvLzViTr
