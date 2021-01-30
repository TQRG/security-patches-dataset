import sys
import argparse
from os import listdir
from os.path import isfile, join

import pandas as pd
import numpy as np
import re

def clean_cve_data(file):
    df = pd.read_csv(file)
    for idx, row in df.iterrows():
        github_refs = eval(row['github'])
        to_remove = set()
        link_to_add = ''
        for ref in github_refs:
            if not re.search(r"\b[0-9a-f]{5,40}\b", ref) \
                or re.search("/master$", ref) \
                or re.search("/master/", ref) \
                or 'commit' not in ref \
                or re.search("/commits$", ref):
                to_remove.add(ref)
            elif '#commitcomment' in ref:
                link_to_add = ref.split('#')[0]
                to_remove.add(ref)
            elif ".patch" in ref:
                link_to_add = ref.replace('.patch','')
                to_remove.add(ref)
        
        for github_ref in to_remove:
            github_refs.remove(github_ref)
        if link_to_add != '':
            github_refs.add(link_to_add)
        df.at[idx, 'github'] = str(github_refs)

    file_name = "{}_new.csv".format(file.split('.')[0])
    df[df['github'] != 'set()'].to_csv(file_name, index=False)    

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Clean cve_details data:')
    parser.add_argument('-file', type=str, metavar='output file', help='file where you want to merge the data')
    
    args = parser.parse_args()

    if args.file != None:
        clean_cve_data(args.file)
    else:
        print('Something wrong with the output file name or year.')

        