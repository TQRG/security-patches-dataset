Organize resources:

```bash
source from_patches_to_commits.sh
```


Process sources data (nvd, cve_details, osv):

```bash
python3 scripts/cli.py --task=process --folder=commits
```

Merge and clean duplicates from sources (nvd, cve_details, osv):

```bash
python3 scripts/cli.py --task=merge --folder=dataset
```

```
python3 scripts/cli.py --task=metadata --fin=dataset/sources_commits.csv --folder=dataset/
```


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
