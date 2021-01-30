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

# WIP

def add_blobs(diff,vulPath):
    for f in diff:
        if f.a_blob is not None:
            pathA=vulPath + '/added/' + f.a_path
            utils.check_if_dir_exists(pathA)
            try:
                f.a_blob.stream_data(open(pathA, 'wb'))
            except Exception as ex:
                print('Ex:', ex)
        if f.b_blob is not None:
            pathB=vulPath + '/deleted/' + f.b_path
            utils.check_if_dir_exists(pathB)
            try:
                f.b_blob.stream_data(open(pathB, 'wb'))
            except Exception as ex:
                print('Ex:', ex)

def clone_repos(df, g, git):
    projects = set()
    for i, r in df.iterrows():
        projects.add('{}:{}'.format(r['owner'], r['project']))
    
    for proj in tqdm(projects):
        owner, project = proj.split(':')
        c_url = g.get_user(owner).get_repo(project).clone_url
        if not os.path.exists('tmp/{}_{}/'.format(owner, project)):
            repo = git.Repo.clone_from(c_url, 'tmp/{}_{}/'.format(owner, project))
        time.sleep(10)

def get_commit(c_list, sha):
    for c in c_list:
        if c.hexsha == sha:
            return c
    return False

def download(file, language, folder):
    
    df = pd.read_csv(file)
    config = utils.load_config('config/github.json')
    g = Github(config['github_token'])


    if not os.path.exists(folder):
        os.makedirs(folder)

    # filtering null cases
    df = df[df['lang'].notnull()]
    for idx, row in df.iterrows():
        languages = eval(row['lang'])
        df.at[idx, 'download'] = language in languages
    
    df = df[df['download'] == True]
    repos_list = df['project'].unique()

    if os.path.exists('tmp/'):
        utils.remove_dir('tmp/')

    for proj in tqdm(repos_list):
        commits_list = df[df['project'] == proj]
        _,_,_, owner, project = proj.split('/')

        c_url = g.get_user(owner).get_repo(project).clone_url
        repo = git.Repo.clone_from(c_url, 'tmp/{}_{}/'.format(owner, project))
        commits = list(repo.iter_commits())

        for idx, row in commits_list.iterrows():
            sha, sha_p = row['sha'], list(eval(row['parents']))[0]
            print(sha, sha_p)
            reference = get_commit(commits, sha) 
            if reference:
                repo.head.reference = get_commit(commits, sha)
                utils.archive_vuln('{}/{}_{}_{}.tar'.format(folder, owner, project, sha), repo)
            else:
                print('{} {} version is not available'.format(proj, sha))
            
            reference = get_commit(commits, sha_p)
            if reference:
                repo.head.reference = get_commit(commits, sha_p)
                utils.archive_vuln('{}/{}_{}_{}.tar'.format(folder, owner, project, sha_p), repo)
            else:
                print('{} {} version is not available'.format(proj, sha_p)) 
            
    utils.remove_dir('tmp/')       

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Collect code samples')
    parser.add_argument('-file', type=str, metavar='input file', help='base file')
    parser.add_argument('-folder', type=str, metavar='output folder', help='folder')
    parser.add_argument('-language', type=str, metavar='language', help='language')
    
    args = parser.parse_args()
    
    if args.file != None and args.language != None and args.folder != None:
        download(args.file, args.language, args.folder)
    else:
        print('Something is wrong. Verify your parameters')