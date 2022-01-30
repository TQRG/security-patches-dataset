# NVD Tool

🔗 [https://www.cvedetails.com/ data](https://nvd.nist.gov/vuln/data-feeds).

All the resulting datasets are available at `../../data/nvd/` (in case you want to check it). 

### 1. Getting the raw data

The **raw dataset** is not available throught the repository. There are two ways of getting the dataset:

1. Scrape the entire NVD data by running the following script:

```bash
source download.sh
```

This script will save the data by `year` in `../../data/nvd/year/`.

2. Download our google cloud mirror by running the following command:
   
```bash
gdown https://drive.google.com/uc\?id\=1SXaxEPEMZ44M5MAcn9Oy_1lM2uY9KCJc
```

### 2. Generate Dataset

Generate the dataset with references to commits in source code hosting websites such as `github`, `bitbucket`, `gitlab` and `git`.

1. Merge, plot stats and normalize NVD data:
```bash
source generate_data.sh
```

2. Filter NVD data by source code hosting website (`github`, `bitbucket`, `gitlab` or `git`):

```bash
source filter_data_by_source.sh github
```
