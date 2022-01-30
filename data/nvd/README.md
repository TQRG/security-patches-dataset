# NVD Dataset

🔗 Result are collected from https://nvd.nist.gov/vuln/data-feeds.

All the datasets provided here are the result of running the scripts available at `../../tools/nvd/` (in case you want to replicate it).

- `all-nvd-patches.csv` integrates all the CVEs data that contain commits logded into `bitbucket`, `gitlab`, `github` or `git`.
- `github-nvd-patches.csv` integrates all the CVEs data that contain commits logded into `github`. The bash script `../../tools/nvd/filter_data_by_source.sh` can be used to generate the same file for other source code hosting websites such as `bitbucket` and `gitlab`.
  
In the previous datasets we only consider the CVEs that include references to source code hosting websites. But the entire NVD database is available in a `.csv` file through the following command:

```bash
gdown https://drive.google.com/uc\?id\=1SXaxEPEMZ44M5MAcn9Oy_1lM2uY9KCJc
```

The `year/` folder provides the raw data that is download from the NVD website. Therefore, merging all the `.json` files in `year/` will retrieve the same results as the previous command; check `../../tools/nvd/generate_data.sh` to see how.