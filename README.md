# Collection of datasets for vulnerability prediction

This dataset is useful to conduct research in vulnerability prediction and/or empirical analysis of tools that detect software vulnerabilities through source code.

This repository integrates datasets from different sources and research papers. Datasets are available individually at `github-patches/` or collectively in a final dataset (`final-dataset/vulnerabilities.csv`). A dataset of non-security related commits is also available for machine learning experiements.

If you want us to add a new dataset, open an issue. 

**Sources:**
- [X] [NVD](https://nvd.nist.gov/) (☠️ 7316 CVEs) - CVEs data provided by the National Vulnerability Database from 2002 to 2022.
- [X] [OSV](https://osv.dev/) (☠️ 4125 CVEs) - Project maintained by Google. Open-source vulnerabilities from different ecosystems: `GHSA`, `DWF`, `Go`, `Linux`, `Maven`, `NuGet`, `OSS-Fuzz`, `PyPI`, `RubyGems`, `crates.io`, `npm`.
  
Sources data is updated monthly (last update: 04-08-2022).
  
**Research Datasets:**
- [X] [SecBench](https://github.com/TQRG/secbench) (☠️ 676 vulns, 🔗 676 commits) - Dataset of single-patches for different programming languages.
- [X] [BigVul](https://github.com/ZeoVan/MSR_20_Code_vulnerability_CSV_Dataset) (🔗 4432 commits) - C/C++ vulnerabilities.
- [X] [SAP](https://github.com/SAP/project-kb/tree/master/MSR2019) (☠️ 1288 vulns, 🔗 1288 commits) - Java vulnerabilities. 
- [X] [Devign](https://sites.google.com/view/devign) (🔗 10894 commits) - C/C++ vulnerabilities. 

Datasets that only consider vulnerabilities with patches available through GitHub.


### Installation

Configure environment to run the scripts:

```bash
conda create --name sec-patches --file requirements.txt
conda activate sec-patches
```

### `tools/` folder

Scripts to obtain the data from each source (CVE Details, NVD or OSV) are available at the `tools/` folder. For each source, there are scripts to collect the raw data, process, normalize and filter the data by source code hosting website (`github`, `bitbucket`, `gitlab` and `git`). Check the documentation provided for each source (e.g., `tools/osv/README.md`) to learn how to obtain, process, normalize and filter the data. All the datasets, except the `raw` ones are available through `data/`. The `raw` datasets can also be collected by downloading a mirror we provide through Google Drive. Check the documentation to see how.

The sources data is updated monthly by running these tools.



