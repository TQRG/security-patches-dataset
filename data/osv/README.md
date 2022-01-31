# OSV Dataset

🔗 Result are collected from  [https://osv.dev/list](https://osv.dev/list).

All the datasets provided here are the result of running the scripts available at `../../tools/osv/` (in case you want to replicate it).

- `all-osv-patches.csv` integrates all vulnerabilities data that contain commits logded into `bitbucket`, `gitlab`, `github` or `git`.
- `github-osv-patches.csv` integrates all the vulnerabilities data that contain commits logded into `github`. The bash script `../../tools/osv/filter_data_by_source.sh` can be used to generate the same file for other source code hosting websites such as `bitbucket` and `gitlab`.
  
In the previous datasets we only consider the vulnerabilities that include references to source code hosting websites. But the entire OSV database is available in a `.csv` file through the following command:

```bash
gdown https://drive.google.com/uc\?id\=1vdLJrUgkjRPk7--0NhmbRrYyVBd2UDdT
```
