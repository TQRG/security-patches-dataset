import argparse 
import os
import sys

import pandas as pd
from github import Github
from bs4 import BeautifulSoup
import requests as req

import utils

def get_metadata_github(filename):
    df = pd.read_csv(filename)
    config = utils.load_config('config/github.json')
    git = Github(config['github_token'])

    repos = set(df['project'])
    for repo in repos:
        _,_,_, owner, project = repo.split('/')
        
        if 'message' in df.columns:
            commits_list = df[(df['project'] == repo) & (~pd.notnull(df['message']))]
        else:
            commits_list = df[df['project'] == repo]

        try:
            repo = git.get_repo('{}/{}'.format(owner, project))
        except: 
            print("Unexpected error: {}".format(sys.exc_info()[0]))
            continue
        save_count = 0
        for idx, row in commits_list.iterrows():
            print('{}/{} ... sha={}'.format(owner, project, row['sha']))
            try:
                commit = repo.get_commit(sha=row['sha'].strip())
            except: 
                print("Unexpected error: {}".format(sys.exc_info()[0]))
                continue
            
            df.at[idx, 'message'] = commit.commit.message.strip()
            df.at[idx, 'author'] = commit.commit.author.name.strip()
            df.at[idx, 'date'] = commit.commit.author.date.strftime("%m/%d/%Y, %H:%M:%S")

            comments = {}
            count = 1
            for comment in commit.get_comments():
                comment_info = {}
                comment_info['author'] = comment.user.login
                comment_info['date'] = comment.created_at.strftime("%m/%d/%Y, %H:%M:%S")
                comment_info['body'] = comment.body.strip()
                comments['com_{}'.format(count)] = comment_info
                count+=1
            
            df.at[idx, 'comments'] = str(comments)

            files = {}
            for f in commit.files:
                file_changed = {}
                file_changed['additions'] = f.additions
                file_changed['deletions'] = f.deletions
                file_changed['changes'] = f.changes
                file_changed['status'] = f.status
                files[f.filename] = file_changed
            
            df.at[idx, 'files'] = str(files)
            df.at[idx, 'parents'] = str(set([p.sha for p in commit.parents]))
            save_count += 1
            if save_count == 200:
                df.to_csv(filename, index=False)
                save_count = 0
        df.to_csv(filename, index=False)

def get_metadata_cvedetails(filename):
    df = pd.read_csv(filename)
    count = 0
    for idx, row in df.iterrows():
        if pd.notnull(row['cve_id']) and 'CVE' in row['cve_id']:
            print(idx, row['cve_id'])
            cve_details_page = req.get("https://www.cvedetails.com/cve-details.php?cve_id={}".format(row['cve_id']))
            soup = BeautifulSoup(cve_details_page.content, 'html.parser')
            if not pd.notnull(row['summary']):
                summary = soup.find_all('div', class_='cvedetailssummary')
                if len(summary) > 0:
                    summary_text = summary[0].getText().strip() 
                    df.at[idx, 'summary'] = summary_text
            
            if not pd.notnull(row['score']):
                score = soup.find_all('div', class_='cvssbox')
                if len(score) > 0:
                    score_text = score[0].getText().strip()
                    df.at[idx, 'score'] = score_text

            if not pd.notnull(row['vuln_type']):
                vuln_type = soup.find_all('span', class_='vt_dos')
                if len(vuln_type) > 0:
                    vuln_type_text = vuln_type[0].getText().strip()
                    df.at[idx, 'vuln_type'] = vuln_type_text
            
            if not pd.notnull(row['cwe_id']):
                table_rows = soup.find(id="cvssscorestable")
                if table_rows:
                    trs = table_rows.find_all('tr')
                    cwe = trs[-1].find('td')
                    if cwe.find('a'):
                        df.at[idx, 'cwe_id'] = "CWE-{}".format(cwe.a.getText())
        count += 1
        if count == 100:
            df.to_csv(filename, index=False)
            count = 0
    
    # clean deprecated cases
    to_remove = []
    for idx, row in df.iterrows():
        if not pd.notnull(row['date']) and not pd.notnull(row['parents']):
            to_remove.append(idx)
    df = df.drop(to_remove)

    df.to_csv(filename, index=False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Data Manipulation CLI')
    parser.add_argument('--source', dest='format', choices=['github', 'cvedetails'])
    parser.add_argument('-file', type=str, metavar='input file', help='input file')
    
    args = parser.parse_args()
    if args.format == 'github':  
        if args.file != None:
            get_metadata_github(args.file)
    elif args.format == 'cvedetails':
        if args.file != None:
            get_metadata_cvedetails(args.file)
    else:
        print('Something is wrong. Verify your parameters')