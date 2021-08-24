import sys
import argparse
from os import listdir
from os.path import isfile, join

import pandas as pd
import numpy as np
from tqdm import tqdm

def load_data(path):
    return [f for f in listdir(path) if isfile(join(path, f)) and '.csv' in f]  

def merge_cve_data(folder, file):
    files_name = load_data(folder)
    df_list = [pd.read_csv(f"{folder}{file_name}") for file_name in files_name]
    count = sum([len(f) for f in df_list])
    df = pd.concat(df_list, axis=0, ignore_index=True)
    assert count == len(df)
    # print(f"Found {count} entries.")
    # print(f"Found {len(df['cve_id'].unique())} unique entries.")
    # github, bitbucket, gitlab = set(), set(), set()
    # for idx, row in tqdm(df.iterrows()):
    #     refs = eval(row['refs'])
    #     for ref in refs:
    #         if 'github' in ref:
    #             github.add(ref)
    #         elif 'bitbucket' in ref:
    #             bitbucket.add(ref)
    #         elif 'gitlab' in ref:
    #             gitlab.add(ref)
    # print(f"Found {len(github)} refs to github.com")
    # print(f"Found {len(bitbucket)} refs to bitbucket.com")
    # print(f"Found {len(gitlab)} refs to gitlab.com")
    #     # links = {link for link in eval(row['github'])+eval(row['refs'])}
    #     # df.at[idx, 'full_ref'] = str(links)
    #     # df.at[idx, 'github'] = str({g_link for g_link in links if 'github.com' in g_link}) 
    f_out =f"../dataset/{file}"
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

        