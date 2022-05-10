# Open Source Vulnerabilities Database Tool

🔗 [https://osv.dev/list](https://osv.dev/list)

OSV is the Open Source Vulnerability Database provided by Google. 
All the resulting datasets are available at `~/data/osv/` (in case you want to check it). 

### 1. Getting the raw data

The **raw dataset** is not available in this repository. There are two means of getting the dataset:

##### Run the scripts to collect the dataset

1. Set up a GitHub Token. First, copy the github template file:

```bash
cp config/github_template.json config/github.json 
```

2. Change the placeholder to a personal github token.

```json
{
	"token": "TOKEN_VALUE"
}
```

3. Run the following bash script to collect the vulnerabilities from the different ecosystems (`GHSA`, `DWF`, `Go`, `Linux`, `Maven`, `NuGet`, `OSS-Fuzz`, `PyPI`, `RubyGems`, `crates.io`, `npm`, `Hex` `Packagist`):

```bash
source download.sh
```

This script will retrieve and process all the data for the different ecosystems. 

##### Download our mirror

The dataset is available through Google Drive. Download our google drive mirror by running the following command:
   
```bash
gdown https://drive.google.com/uc?id=1_n08wgdyEFT-j53f_gzUpDbQBMMFDqKW
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
