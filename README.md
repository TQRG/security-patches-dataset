
Building a ground truth dataset of real security patches for machine learning and testing activities.

Datasets:
- [X] [CVEDetails](https://www.cvedetails.com/) - Includes data from CVEs from 1999 to 2021 (6486 patches) -- last update: 28-08-2021.
- [X] [SecBench](https://github.com/TQRG/secbench) - Dataset with 687 patches for different programming languages.
- [X] [BigVul](https://github.com/ZeoVan/MSR_20_Code_vulnerability_CSV_Dataset)
- [X] [SAP](https://github.com/SAP/project-kb/tree/master/MSR2019)
- [ ] [OSV](https://osv.dev/) - Project maintained by Google. It integrates vulnerabilities from 
different ecosystems: 
[Go](https://github.com/golang/vulndb), [Google Rust](https://github.com/RustSec/advisory-db), [PyPI](https://github.com/pypa/advisory-db), [DWF](https://github.com/distributedweaknessfiling/dwflist), [OSS-Fuzz](https://github.com/google/oss-fuzz-vulns).
- [ ] [CrossVul](https://dimitro.gr/assets/papers/NDLM21.pdf)
- [ ] [CVEFixes](https://arxiv.org/pdf/2107.08760.pdf)


### Installation

Requirements installation:

```
virtualenv --python=python3.8 venv
source venv/bin/activate
pip install -r requirements.txt
```

### Data Analysis 

Jupyter notebooks are available. Charts and wordclouds are saved at `notebook/charts`.

```
source venv/bin/activate
cd notebooks
jupyter notebook
```

### CVE Details

Scrapping cvedetails for CVEs in 1999:
```
source venv/bin/activate
cd scraper
python3 scrape_cve_details.py --mode per_year -file data/1999.csv -year 1999
```

Merge data from data folder:
```
source venv/bin/activate
cd scraper
python3 merge_cve_data.py -folder data/ -file cve_details_data.csv
```

Clean cve_details data:
```
source venv/bin/activate
cd scraper
python3 clean_data.py -file cve_details.csv
```

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
