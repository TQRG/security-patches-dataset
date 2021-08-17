import argparse 
import os
import git
import time
import sys
import shutil

import pandas as pd

from os import listdir
from os.path import isfile, join
from tqdm import tqdm
from github import Github

import utils
     
def get_diff(fin, fout):
    
    df = pd.read_csv(fin)
    config = utils.load_config('config/github.json')
    g = Github(config['github_token'])
    repos_list = df['project'].unique()

    if not os.path.exists('tmp/'):
        os.makedirs('tmp/')
    
    print(f"Found {len(repos_list)} projects.")

    for proj in tqdm(repos_list):
        
        print(f"Downloading code changes for {proj}.")
        
        if 'code_changes' in df.keys():
            patches = df[(df['project'] == proj) & (~pd.notnull(df['code_changes']))]
        else:
            patches = df[df['project'] == proj]

        if len(patches) < 1:
            print(f"Already completed: {proj}")
            continue

        _,_,_, owner, project = proj.split('/')
        if not os.path.exists(f"tmp/{owner}_{project}/"):
            c_url = g.get_user(owner).get_repo(project).clone_url
            repo = git.Repo.clone_from(c_url, f"tmp/{owner}_{project}/")
            print(f"Cloning {c_url} for tmp/{owner}_{project}/")
        else:
            repo = git.Repo(f"tmp/{owner}_{project}/")
            print(f"Loading tmp/{owner}_{project}/ ...")
        
        for idx, row in patches.iterrows():            
            sha = row['sha']
            parents = eval(row['parents'])
            diffs = []
            for parent in parents:
                try:
                    diff = repo.git.diff(parent, sha)
                    diffs.append({f"diff_{parent}_{sha}": diff})
                except:
                    print(f"diff_{parent}_{sha} skipped...")
                    continue
                print(f"diff_{parent}_{sha} added to db.")
            df.at[idx, 'code_changes'] = diffs
        utils.remove_dir(f"tmp/{owner}_{project}/")
        df.to_csv(fout, index=False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get code changes or diff information.')
    parser.add_argument('-fin', type=str, metavar='input file', help='base file')
    parser.add_argument('-fout', type=str, metavar='output file', help='base file')
    
    args = parser.parse_args()
    if args.fin:
        get_diff(args.fin, args.fout)
    else:
        print('Something is wrong. Verify your parameters')