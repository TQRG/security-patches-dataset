# NVD Dataset

🔗 Result are collected from https://nvd.nist.gov/vuln/data-feeds

All the datasets provided here are the result of running the scripts available at `../tools/nvd` (in case you want to replicate it).

- `all-cve-details-patches.csv` integrates all the CVEs data that contain commits logded into `bitbucket`, `gitlab` or `github`.
- `github-cve-details.csv` integrates all the CVEs data that contain commits logded into `github`. The bash script `../tools/cve-details/filter_data_by_source.sh` can be used to generate the same file for other source code hosting websites such as `bitbucket` and `gitlab`.
  
In the previous datasets we only consider the CVEs that include references to source code hosting websites. But the entire CVE Details database is available in a `.csv` file through the following command:

```
gdown https://drive.google.com/uc\?id\=1qGrndhvMBbY15t9VUK7XTyb1UIhHu3mY
```

The `year/` folder provides the raw data that resulted from scraping the CVE-Details per year. Therefore, merging all the `.csv` files in `year/` will retrive the same results as the previous command.