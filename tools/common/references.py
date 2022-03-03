import argparse
import csv
import re
import csv

import pandas as pd
import numpy as np

from tqdm import tqdm

LINE = "---------------------------"

def get_source(refs):
    """ Get source for each reference. """
    refs, sources = eval(refs), []
    for ref in refs:
        if 'github' in ref:
            sources.append('github')
        elif 'bitbucket' in ref:
            sources.append('bitbucket')
        elif 'gitlab' in ref:
            sources.append('gitlab')
        elif 'git' in ref:
            sources.append('git')
        else:
            sources.append('other')
    return sources

def split_commits(chain):
    """ Normalizes the chain of commits for each CVE
        e.g., from link1,link2 to {link1, link2}.
    
    Args:
        chain (string): chain of commits

    Returns:
        new_chain: set of commits normalized
    """

    new_chain = set()
    for ref in eval(chain):
        if 'http://' in ref:
            protocol = 'http://'
        else:
            protocol = 'https://'

        count = ref.count(protocol)
        if count > 1:
            if ',' in ref:
                new_chain = set.union(new_chain, set([r for r in ref.split(',')]))
            else:
                new_chain = set.union(new_chain, set([f"{protocol}{r}" for r in ref.split(protocol)]))
        else:
            new_chain = set.union(new_chain, set([ref]))
    return new_chain if len(new_chain) > 0 else np.nan


def normalize_commits(f):
    """ 
        Normalize commits references
    """
    # load data
    df = pd.read_csv(f, escapechar="\\")

    # iterate over each row
    for idx, row in df.iterrows():

        # get references and initialize output
        refs, commits = eval(row['code_refs']), []

        # iterate over references
        for ref in refs:
            # e.g., https://github.com/{owner}/{repo}/commit/{sha}CONFIRM:
            if "CONFIRM:" in ref:
                commits.append(ref.replace("CONFIRM:", ''))
            # e.g., https://github.com/intelliants/subrion/commits/develop
            # e.g., https://gitlab.gnome.org/GNOME/gthumb/commits/master/extensions/cairo_io/cairo-image-surface-jpeg.c
            # e.g., https://github.com/{owner}/{repo}/commits/{branch}
            elif not re.search(r"\b[0-9a-f]{5,40}\b", ref): 
                continue     
            # e.g., https://github.com/{owner}/{repo}/commits/master?after={sha}+{no_commits}          
            elif '/master?' in ref:
                continue   
            # e.g., https://github.com/{owner}/{repo}/commit/{sha}#commitcomment-{id}          
            elif '#' in ref and ('#comments' in ref or '#commitcomment' in ref):
                commits.append(ref.split('#')[0])
            # e.g., https://github.com/{owner}/{repo}/commit/{sha}.patch
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
    df.to_csv(f, 
              quoting=csv.QUOTE_NONNUMERIC, 
              escapechar="\\", 
              doublequote=False, 
              index=False)

    print(f"{df.shape[0]} patches were saved to {f}")


def collect_commits(fin, fout):
    """
        Collects commits references for source code hosting websites 
        such as github, bitbucket, gitlab and git.
    """
    # read the csv
    df = pd.read_csv(fin, escapechar="\\")

    # drop cases with no refs
    df = df.dropna(subset=['refs'])

    # normalize refs
    df['refs'] = df['refs'].apply(lambda ref: split_commits(ref))

    # get references to source code hosting websites 
    for idx, row in tqdm(df.iterrows()):
        commits = []
        for ref in row['refs']:
            found = re.search(r'(github|bitbucket|gitlab|git).*(/commit/|/commits/)', ref)
            if found: 
                commits.append(ref)
        if len(commits) > 0:
            df.at[idx, 'code_refs'] = str(set(commits))
    
    # filter cases without any references to source code hosting websites
    df_code_ref = df.dropna(subset=['code_refs'])

    # save data
    df_code_ref.to_csv(fout, 
                        quoting=csv.QUOTE_NONNUMERIC, 
                        escapechar="\\", 
                        doublequote=False, 
                        index=False)
    print(f"{len(df_code_ref)} patches were saved to {fout}")


def print_commits_stats(fin):
    """ Print commits statistics. """

    def set_len(x):
        return len(eval(x))

    # read the csv
    df = pd.read_csv(fin, escapechar="\\")

    # get number of commits involved in each patch
    df['n_commits'] = df['code_refs'].transform(set_len)

    print(f"{LINE}\ncommits (#)\tpatches (#)\n{LINE}")
    # iterate over the stats
    for n in np.sort(df['n_commits'].unique()):
        print(f"{n}\t\t{len(df[df['n_commits'] == n])}")
    print(f"{LINE}\n👀 n security patches where\nperformed using y commits\n{LINE}\n")
    
    # get commits source
    sources = []
    for s in df['code_refs'].transform(get_source):
        sources += s

    print(f"{LINE}{LINE}\nSOURCE\t\tcommits (#)\tcommits (%)\n{LINE}{LINE}")
    # iterate over the different sources 
    for source in set(sources):
        n_source = len([s for s in sources if s == source])
        if source == 'bitbucket':
            print(f"{source}\t{n_source}\t\t{(n_source/len(sources))*100:.2f}%")
        else:
            print(f"{source}\t\t{n_source}\t\t{(n_source/len(sources))*100:.2f}%")
    print(f"{LINE}{LINE}\n")


def commits_source(fin, dataset, source):
    """Infer commits source (e.g., git, github, bitbucket, gitlab, etc).

    Args:
        fin (string): name of the file that contains the commits data
        dataset (string): dataset name
        source (string): git, github, bibucket, gitlab
    """
    # read csv
    df = pd.read_csv(fin, escapechar="\\")

    # get commits from source
    for idx, row in df.iterrows():
        refs, commits = eval(row['code_refs']), []
        for ref in refs:
            if source in ref:
                commits.append(ref)
        if len(commits) > 0:
            df.at[idx, 'commits'] = str(set(commits))
        else:
            df.at[idx, 'commits'] = np.nan
    
    # drop rows without commits for source
    df_source = df.dropna(subset=['commits'])

    # save patches
    fout = f'../../data/{dataset}/{source}-{dataset}-patches.csv'
    
    df_source.to_csv(fout, 
                        quoting=csv.QUOTE_NONNUMERIC, 
                        escapechar="\\", 
                        doublequote=False, 
                        index=False)
    print(f"{len(df_source)} patches were saved to {fout}")


def process_nvd_commits(fin, fout):
    # read the csv
    df = pd.read_csv(fin, escapechar="\\")

    # get references to source code hosting websites 
    for idx, row in tqdm(df.iterrows()):
        refs, frefs = eval(row['refs']), []
        for ref in refs:
            frefs.append(ref['url'])
        if len(frefs) > 0:
            df.at[idx, 'refs'] = set(frefs)
    
    # drop rows without refs
    df = df.dropna(subset=['refs'])
    df.to_csv(fout, 
                quoting=csv.QUOTE_NONNUMERIC, 
                escapechar="\\", 
                doublequote=False, 
                index=False)    
    print(f"{len(df)} patches were saved to {fout}")


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='CLI to process references')
    parser.add_argument('--task', dest='format', 
                                    choices=['normalize', 'commits', 'stats', 'filter', 'process'])    
    parser.add_argument('--fin', type=str, 
                                    metavar='input file', 
                                    help='input file')
    parser.add_argument('--fout', type=str, 
                                    metavar='file', 
                                    help='output file')
    parser.add_argument('--source', type=str, 
                                    metavar='str', 
                                    help='name of the source')
    parser.add_argument('--dataset', type=str, 
                                    metavar='str', 
                                    help='name of the dataset')
   
    args = parser.parse_args()

    if args.format == 'normalize':
        if args.fin:
            normalize_commits(args.fin)
    elif args.format == 'commits':
        if args.fin and args.fout:
            collect_commits(args.fin, args.fout)
    elif args.format == 'stats':
        if args.fin:
            print_commits_stats(args.fin)
    elif args.format == 'filter':
        if args.fin and args.dataset and args.source:
            commits_source(args.fin, args.dataset, args.source)
    elif args.format == 'process':
        if args.fin and args.fout:
            process_nvd_commits(args.fin, args.fout)
    else:
        print('Something wrong with the output file name or year.')

        