 #!/bin/bash

# generate the cve-details dataset
cd cve-details/
source generate_data.sh
source filter_data_by_source.sh github
cd ..