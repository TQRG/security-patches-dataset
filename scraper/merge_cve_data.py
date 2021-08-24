import sys
import argparse
from os import listdir
from os.path import isfile, join

import pandas as pd
import numpy as np
from tqdm import tqdm

def load_data(path):
    return [f for f in listdir(path) \
                if isfile(join(path, f)) \
                    and '.csv' in f]  

def merge_cve_data(folder, file):
    files_name = load_data(folder)
    df_list = [pd.read_csv(f"{folder}{file_name}") \
                    for file_name in files_name]
    count = sum([len(f) for f in df_list])
    df = pd.concat(df_list, axis=0, ignore_index=True)
    assert count == len(df)
    f_out =f"../data/{file}"
    df.to_csv(f_out, index=False)
    print(f"{len(df)} CVEs saved to {f_out}")

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Merge all CVEs data contained in data/ folder:')
    parser.add_argument('-folder', type=str, metavar='folder', help='cve data folder')
    parser.add_argument('-file', type=str, metavar='output file', help='file where you want to merge the data')
    
    args = parser.parse_args()

    if args.folder != None and args.file != None:
        merge_cve_data(args.folder, args.file)
    else:
        print('Something wrong with the output file name or year.')

        