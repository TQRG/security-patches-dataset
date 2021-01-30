import sys
import argparse
from os import listdir
from os.path import isfile, join

import pandas as pd
import numpy as np
from tqdm import tqdm

def load_data(path):
    return [f for f in listdir(path) if isfile(join(path, f)) and '.csv' in f]

def read_data(files, path):
    df = pd.concat(dfs, axis=0, ignore_index=True)
    return df

def merge_cve_data(folder, file):
    files_name = load_data(folder)
    df_list = [pd.read_csv(folder+file_name) for file_name in files_name]
    count = sum([len(f) for f in df_list])
    df = pd.concat(df_list, axis=0, ignore_index=True)
    assert count == len(df)
    for idx, row in tqdm(df.iterrows()):
        links = {link for link in eval(row['github'])+eval(row['refs'])}
        df.at[idx, 'full_ref'] = str(links)
        df.at[idx, 'github'] = str({g_link for g_link in links if 'github.com' in g_link}) 
    df[df['github'] != 'set()'].to_csv(file, index=False)

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Merge all CVEs data contained in data/ folder:')
    parser.add_argument('-folder', type=str, metavar='folder', help='cve data folder')
    parser.add_argument('-file', type=str, metavar='output file', help='file where you want to merge the data')
    
    args = parser.parse_args()

    if args.folder != None and args.file != None:
        merge_cve_data(args.folder, args.file)
    else:
        print('Something wrong with the output file name or year.')

        