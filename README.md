# Collection of datasets for vulnerability prediction

This dataset is useful to conduct research in vulnerability prediction and/or empirical analysis of tools that detect software vulnerabilities through source code.

This repository integrates datasets from different sources and research papers. Datasets are available individually at `github-patches/` or collectively in a final dataset (`final-dataset/vulnerabilities.csv`). A dataset of non-security related commits is also available for machine learning experiements.

Release 1: Code [here](https://github.com/TQRG/security-patches-dataset/tree/3d974be51e955b211c02a16b520cc5c7a10704ae); Paper [here](https://arxiv.org/abs/2110.09635)

If you want us to add a new dataset, open an issue. 

**Sources:**
- [X] [CVEDetails](https://www.cvedetails.com/) - CVEs data from 1999 to 2022.
- [X] [NVD](https://nvd.nist.gov/) - CVEs data provided by the National Vulnerability Database from 2002 to 2022.
- [X] [OSV](https://osv.dev/) - Project maintained by Google. Open-source vulnerabilities from different ecosystems: `GHSA`, `DWF`, `Go`, `Linux`, `Maven`, `NuGet`, `OSS-Fuzz`, `PyPI`, `RubyGems`, `crates.io`, `npm`.
  
Sources data is updated monthly (last update: 31-01-2022).
  
**Research Datasets:**
- [X] [SecBench](https://github.com/TQRG/secbench) - Dataset with 687 single-patches for different programming languages.
- [X] [BigVul](https://github.com/ZeoVan/MSR_20_Code_vulnerability_CSV_Dataset)
- [X] [SAP](https://github.com/SAP/project-kb/tree/master/MSR2019)
- [X] [Devign](https://sites.google.com/view/devign) 

Datasets that only consider vulnerabilities with patches available through GitHub.


### Installation

Configure environment to run the scripts:

```bash
conda create --name sec-patches --file requirements.txt
conda activate sec-patches
```

### `final-dataset/` folder

### `scripts/` folder


### `github-patches/` folder


### `tools/` folder

Scripts to obtain the data from each source are available at the `tools/` folder. For each source, there are scripts to collect the raw data, process, normalize and filter the data by source code hosting website (`github`, `bitbucket`, `gitlab` and `git`). Check the documentation provided for each source (e.g., `tools/osv/README.md`) to learn how to obtain, process, normalize and filter the data. All the datasets, except the `raw` ones are available through `data/`. The `raw` datasets can also be collected by downloading a mirror we provide through Google Drive. Check the documentation to see how.

The sources data is updated monthly by running these tools.



