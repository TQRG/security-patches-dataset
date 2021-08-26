import argparse 
import os
import sys
import re
import logging
import json
import os.path
from os import path
from pathlib import Path


from colored import fg, bg, attr
import pandas as pd
import github 
from github import GithubException


def set_step(commits_length):
    if commits_length < 10:
        return 50
    elif commits_length < 100:
        return 150
    else:
        return 250

def load_config(filename):
    with open("{}/{}".format(Path(__file__).parent.absolute(), filename)) as config:
        data = json.load(config)
    return data

def get_github_config():
    configs = load_config('config/github.json')
    for config in configs:
        git = github.Github(config['github_token'])
        if git.get_rate_limit().core.remaining > 0:
            return git

def get_negative_dataset(filename, proportion=30):
    
    # read positive dataset
    df = pd.read_csv(filename)
    git = get_github_config()
    
    if not git:
        print("Sorry, you don't have rate available")
        return

    logging.basicConfig(filename='app.log', filemode='w', format='%(name)s:%(levelname)s:%(message)s')

    # if path.exists('negative.csv'):
    #     df_final = pd.read_csv('negative.csv')
    #     # print(df_final['project'].unique())
    #     for repo in set(df['project']):
    #         print(set(df_final['project'].unique()))
    #         # print(repo in set(df_final['project'].unique()))
    #     repos = set([repo for repo in set(df['project']) if repo not in set(df_final['project'].unique())])
    # else:
    #     df_final = pd.DataFrame(columns=['github', 'message', 'project']) 
    #     repos = set(df['project'])
    # df_final = pd.DataFrame(columns=['github', 'message', 'project']) 
    
    negative = {'github':[], 
                    'message':[], 
                    'project':[]}

    for repo in set(df['project']):
        _,_,_, owner, project = repo.split('/')
        commits_list = df[df['project'] == repo]
        
        try:
            rep = git.get_repo('{}/{}'.format(owner, project))
        except: 
            print("Unexpected error: {}".format(sys.exc_info()[0]))
            continue
        
        commits_length = len(commits_list)
        n_commits = commits_length * proportion
        step = set_step(commits_length)
        
        print('Searching for {} commits in {} ; rate={}'.format(n_commits, repo, git.get_rate_limit().core.remaining))
        count, start = 0, 0
    
        while count < n_commits:
            try:
                commits = list(rep.get_commits()[start:start+200])
            except IndexError as error:
                print(error)
                print('%s Something wrong with %s %s' % (fg(1), repo, attr(0)))
                logging.error("ERROR: {}: Something wrong with {}".format(error, repo))
                break
            except GithubException as error:
                print(error)
                git = get_github_config()
                if not git:
                    print("Sorry, you don't have rate available")
                    return

            for commit in commits:
                message = commit.commit.message
                if not re.search('secur|patch|cve|vulnerab', message.lower()):
                    negative['github'].append('{}/commit/{}'.format(repo, commit.sha))
                    negative['message'].append(message.strip())
                    negative['project'].append(repo)
                    count+=1
                    if count == n_commits:
                        break

            start+=step
            print('%s %s commits collected... %s' % (fg(2), count, attr(0)))
        df_neg = pd.DataFrame.from_dict(negative)
        df_neg.to_csv('negative.csv', index=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get negative data')
    parser.add_argument('--mode', dest='format', choices=['default', 'proportion', 'add'])
    parser.add_argument('-file', type=str, metavar='input file', help='input file')
    parser.add_argument('-proportion', type=str, metavar='input file', help='input file')

    args = parser.parse_args()

    if args.format == 'default':  
        if args.file != None:
            get_negative_dataset(filename=args.file)
    elif args.format == 'proportion':
        if args.file != None and args.proportion != None:
            get_default_dataset(filname=args.file, proportion=args.proportion)
    else:
        print('Something is wrong. Verify your parameters')