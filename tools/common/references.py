import argparse
import re

import pandas as pd

from tqdm import tqdm

def normalize_commit_data(f):
    """ Normalize commits references """
    # load data
    df = pd.read_csv(f)

    # iterate over each row
    for idx, row in df.iterrows():

        # get references and initialize output
        refs, commits = eval(row['code_refs']), []

        # iterate over references
        for ref in refs:
            # e.g., https://github.com/openstack/heat-templates/commit/65a4f8bebc72da71c616e2e378b7b1ac354db1a3CONFIRM:
            if "CONFIRM:" in ref:
                commits.append(ref.replace("CONFIRM:", ''))
            # e.g., https://github.com/intelliants/subrion/commits/develop
            # e.g., https://gitlab.gnome.org/GNOME/gthumb/commits/master/extensions/cairo_io/cairo-image-surface-jpeg.c
            # e.g., https://github.com/alkacon/opencms-core/commits/branch_10_5_x
            elif not re.search(r"\b[0-9a-f]{5,40}\b", ref): 
                continue     
            # e.g., https://github.com/gnuboard/gnuboard5/commits/master?after=831219e2c233b2d721a049b7aeb054936d000dc2+69          
            elif '/master?' in ref:
                continue   
            # e.g., https://github.com/roundcube/roundcubemail/commit/40d7342dd9c9bd2a1d613edc848ed95a4d71aa18#commitcomment-15294218          
            elif '#' in ref and ('#comments' in ref or '#commitcomment' in ref):
                commits.append(ref.split('#')[0])
            # e.g., https://github.com/fedora-infra/python-fedora/commit/b27f38a67573f4c989710c9bfb726dd4c1eeb929.patch
            elif '.patch' in ref:
                commits.append(ref.replace('.patch',''))
            # e.g., https://github.com/absolunet/kafe/commit/c644c798bfcdc1b0bbb1f0ca59e2e2664ff3fdd0%23diff-f0f4b5b19ad46588ae9d7dc1889f681252b0698a4ead3a77b7c7d127ee657857
            elif '%23' in ref:
                commits.append(ref.replace('%23', '#'))
            else:
                commits.append(ref)

        # save new set of commits
        if len(commits) > 0:
            df.at[idx, 'code_refs'] = set(commits)

    # drop row with no code refs after normalization 
    df = df.dropna(subset=['code_refs'])

    # save new dataframe
    df.to_csv(f, index=False)

    print(f"{df.shape[0]} patches were saved to {f}")


def collect_commits(fin, fout):
    """
        Collects commits references for source code hosting websites 
        such as github, bitbucket, gitlab and git.
    """
    # read the csv
    df = pd.read_csv(fin)

    # get references to source code hosting websites 
    for idx, row in tqdm(df.iterrows()):
        refs = eval(row['refs'])
        patch_refs = []
        for ref in refs:
            found = re.search(r'(github|bitbucket|gitlab|git).*(/commit/|/commits/)', ref)
            if found: 
                patch_refs.append(ref)
        if len(patch_refs) > 0:
            df.at[idx, 'code_refs'] = str(patch_refs)
    
    # filter cases without any references to source code hosting websites
    df_code_ref = df.dropna(subset=['code_refs'])

    # save data
    df_code_ref.to_csv(fout, index=False)
    print(f"{len(df_code_ref)} patches were saved to {fout}")




if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='CLI to process references')
    parser.add_argument('--task', dest='format', choices=['normalize', 'commits', 'filter'])    
    parser.add_argument('--fin', type=str, metavar='input file', help='file to clean')
    parser.add_argument('--fout', type=str, metavar='file', help='new file')
   
    args = parser.parse_args()

    if args.format == 'normalize':
        if args.fin:
            normalize_commit_data(args.fin)
    elif args.format == 'commits':
        if args.fin and args.fout:
            collect_commits(args.fin, args.fout)
    else:
        print('Something wrong with the output file name or year.')

        