#!/bin/bash

# download OSV data
source download.sh

# merge/process, filter refs, normalize and stats
source generate_data.sh

# filter data for github
source filter_data_by_source.sh github