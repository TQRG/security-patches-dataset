import sys
import time

import pandas as pd
import numpy as np
import utils 

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

from github import RateLimitExceededException
from github import UnknownObjectException

def load_missing_commits(df, repo):
    if 'files' in df.columns:
        print(f"some entries already completed")
        commits_list = df[(df['project'] == repo) & (~pd.notnull(df['files']))]
    else:
        print(f"no entries completed; starting from 0")
        commits_list = df[df['project'] == repo]
    return commits_list

def sort_chain(repo, chain):
    chain_list = list(eval(chain))
    df = pd.DataFrame()
    for commit in chain_list:
        try:
            sha = commit.split('/')[-1]
            gcommit = repo.get_commit(sha=sha.strip())
            author = gcommit.commit.author
            df = df.append({'commit': gcommit, 'datetime': author.date}, ignore_index = True)
        except Exception as e:
            print("Unexpected error: {}".format(e))
            return None, None 
    
    df = df.drop_duplicates()
    df = df.sort_values(by='datetime', ascending=True)

    # chain of commit and datetime
    return list(df['commit']), list(df['datetime'])
        

def get_parents(chain_commit):
    parents = set([commit.sha for commit in chain_commit.commit.parents])
    return parents

def set_commits_info(df, idx, last_commit, chain_datetime, chain_idx):
    parents = set([commit.sha for commit in last_commit.commit.parents])
    df.loc[idx, 'before_first_fix_commit'] = str(parents)
    df.loc[idx, 'last_fix_commit'] = last_commit.commit.sha
    df.loc[idx, 'chain_ord_pos'] = chain_idx + 1
    df.loc[idx, 'commit_datetime'] = chain_datetime[chain_idx].strftime("%m/%d/%Y, %H:%M:%S")


def metadata(repo, df, git, config):
    
    # get owner and project
    if not pd.notna(repo):
        return df
    owner, project = repo.split('/')[3::]

    # get entries to complete per repo
    commits_list = load_missing_commits(df, repo)

    try:
        repo = git.get_repo('{}/{}'.format(owner, project))
    except RateLimitExceededException:
        git = utils.get_token(config)
    except UnknownObjectException:
        print(f"🚨 Repo not found. Skipping {owner}/{project} ...")
        return git, df

    for idx, row in commits_list.iterrows():
        chain_ord, chain_datetime = sort_chain(repo, row['chain'])
        
        # FIXME: one of the source vulns still has the href in 
        # the commit_sha column when it reaches here. For some
        # reason this is not fixed in the normalization phase.
        # Find why!
        if 'http' in row['commit_sha']:
            row['commit_sha'] = row['commit_sha'].split('/')[-1]
              
        if not chain_ord and not chain_datetime:
            print(f"🚨 Skipping {row['vuln_id']} ...")
            continue

        try:
            chain_ord_sha = [commit.commit.sha for commit in chain_ord]
            print(chain_ord_sha)
            df.loc[idx, 'chain_ord'] = str(chain_ord_sha)
            if len(chain_ord) == 1:
                last_commit = chain_ord[0]
                df.loc[idx, 'before_first_fix_commit'] = str(get_parents(last_commit))
                chain_idx = chain_ord_sha.index(row['commit_sha'])
                set_commits_info(df, idx, last_commit, chain_datetime, chain_idx)
            else:
                first_commit, last_commit = chain_ord[0], chain_ord[-1]
                df.loc[idx, 'before_first_fix_commit'] = str(get_parents(first_commit))
                chain_idx = chain_ord_sha.index(row['commit_sha'])
                set_commits_info(df, idx, last_commit, chain_datetime, chain_idx)

            commit = chain_ord[chain_idx]
            df.loc[idx, 'message'] = commit.commit.message.strip()
            df.loc[idx, 'author'] = commit.commit.author.name.strip()
        
       
            comments, count = {}, 1
            for comment in commit.get_comments():
                comments[f'com_{count}'] = {
                'author': comment.user.login,
                'datetime': comment.created_at.strftime("%m/%d/%Y, %H:%M:%S"),
                'body': comment.body.strip()
                }
                count += 1
            df.loc[idx, 'comments'] = str(comments) if len(comments) > 0 else np.nan
        except RateLimitExceededException:
            git = utils.get_token(config)
   
        df.loc[idx, 'stats'] = str({'additions': commit.stats.additions, 
                                    'deletions': commit.stats.deletions, 
                                    'total': commit.stats.total})

        files = {}
        for f in commit.files:
            files[f.filename] = {
                'additions': f.additions,
                'deletions': f.deletions,
                'changes': f.changes,
                'status': f.status,
                'raw_url': f.raw_url,
                'patch': f.patch.strip() if f.patch else None
            }
        df.loc[idx, 'files'] = str(files)

    return git, df
