# NVD Database

Data in folder `nvd/` needs to be downloaded from the website. 
TODO: Script to get the data automatically.

Generate .yaml files with OSV Schema:
```
python3 cli.py --task=osv_generator --data=data/
```

Import data from raw .json to .csv:
```
python3 cli.py --task=extractor --data=data/ --fout=../../data/nvd/
```

Filter vulns with refs:
```
python3 cli.py --task=process --fin=../../data/nvd/raw-nvd-data.csv --fout=data/nvd/all-nvd-patches.csv
```