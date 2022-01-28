# Collection of datasets for vulnerability prediction

This repository integrates datasets from different sources and research papers. All the datasets provide commits for security patches.

Release 1: Code [here](https://github.com/TQRG/security-patches-dataset/tree/3d974be51e955b211c02a16b520cc5c7a10704ae); Paper [here](https://arxiv.org/abs/2110.09635)

**Datasets:**
- [X] [CVEDetails](https://www.cvedetails.com/) - Includes data from CVEs from 1999 to 2021 (6486 patches) -- last update: 17-01-2022.
- [X] [SecBench](https://github.com/TQRG/secbench) - Dataset with 687 patches for different programming languages.
- [X] [BigVul](https://github.com/ZeoVan/MSR_20_Code_vulnerability_CSV_Dataset)
- [X] [SAP](https://github.com/SAP/project-kb/tree/master/MSR2019)
- [X] [Devign](https://sites.google.com/view/devign) - FFmpeg and Qemu commits ()
- [X] [OSV](https://osv.dev/) - Project maintained by Google. It integrates vulnerabilities from 
different ecosystems: `DWF`, `Go`, `Linux`, `Maven`, `NuGet`, `OSS-Fuzz`, `PyPI`, `RubyGems`, `crates.io`, `npm`.


### Installation

Requirements installation:

```
virtualenv --python=python3.8 venv
source venv/bin/activate
pip install -r requirements.txt
```

### Data Analysis 



<!-- Clean cve_details data:
```
source venv/bin/activate
cd scraper
python3 clean_data.py -file cve_details.csv
``` -->

### Dataset

Merge all datasets:
```
source venv/bin/activate
python3 scripts/merge_datasets.py --mode merge -file positive.csv
```

Get CVE Details to complete the data from other datasets:
```
source venv/bin/activate
python3 scripts/get_metadata.py --source cvedetails -file positive.csv
```

Configure the github API at `scripts/config/`. 
```
source venv/bin/activate
cd scripts/config/
cp github_template.json github.json
```

Add a token and username to the file with permissions for repositories and users information.

Get GitHub data: 
```
source venv/bin/activate
python3 scripts/get_metadata.py --source github -file positive.csv
```

### Add features

Adding the extension of files involved in changes (ext_files):
```
source venv/bin/activate
python scripts/add_features.py --feature ext_files -file positive.csv
```

Adding programming languages (lang):
```
source venv/bin/activate
python scripts/add_features.py --feature lang -file positive.csv
```

### Add Code Changes

Adding code changes/diff information to the dataset:
```
source venv/bin/activate
python3 scripts/get_code_changes.py -fin dataset/positive.csv -fout dataset/data.csv
```

### Download codebases

To download Scala samples:

```
source venv/bin/activate
python3 scripts/download.py -file dataset/positive.csv -folder code_samples -language Scala
```
