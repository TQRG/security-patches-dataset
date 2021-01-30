
### Installation

Requirements installation:

```
virtualenv --python=python3.7 venv
source venv/bin/activate
pip install -r requirements.txt
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
python3 merge_cve_data.py -folder data/ -file cve_details.csv
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

### Data Analysis 

Jupyter notebooks are available. Charts and wordclouds are saved at `notebook/charts`.

```
source venv/bin/activate
cd notebooks
jupyter notebook
```