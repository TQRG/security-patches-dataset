# Open Source Vulnerabilities Database Tool

🔗 [https://osv.dev/list](https://osv.dev/list)

OSV is the Open Source Vulnerability Database provided by Google. 
All the resulting datasets are available at `../../data/osv/` (in case you want to check it). 

### 1. Getting the raw data

The **raw dataset** is not available in this repository. There are two means of getting the dataset:

1. Run the following bash script (`$GITHUB_TOKEN` needs to be assigned inside). It downloads the vulnerabilities from several ecosystems (`GHSA`, `DWF`, `Go`, `Linux`, `Maven`, `NuGet`, `OSS-Fuzz`, `PyPI`, `RubyGems`, `crates.io`, `npm`):

```bash
source download.sh
```

This script will retrieve and process all the data for the different ecosystems. We also provide a mirror of the data through Google Cloud.

1. Download our google cloud mirror by running the following command:
   
```bash
gdown https://drive.google.com/uc\?id\=1gmKSCDuZwUtXmO41fvXtzvh3Uy0-y25R
```

### 2. Generate Dataset

Filter the entries with references to commits in source code hosting websites such as `github`, `bitbucket`, `gitlab` and `git`.

1. Merge, plot stats and normalize OSV data:
```bash
source generate_data.sh
```

2. Filter OSV data by source code hosting website (`github`, `bitbucket`, `gitlab` or `git`):

```bash
source filter_data_by_source.sh github
```
