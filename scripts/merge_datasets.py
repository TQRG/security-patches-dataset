import argparse 
import os
import re

import pandas as pd

from utils import read_config


def prepare_pontas(df):
    del df['type']
    return df

def prepare_cve_details(df):
    df = df[['cve_id', 'cwe_id', 'vuln_type', 'score', 'github', 'summary']] 
    data = {label:[] for label in df.columns}
    for idx, row in df.iterrows():
        github_links = eval(row['github'])

        # check and fix anomalies 
        if len(github_links) == 1:
            link = list(github_links)[0]
            tmp =  link.count('https://')
            if tmp > 1:
                github_links = set(['{}{}'.format('https://', link) for link in link.split('https://')[1::]])

        if len(github_links) > 1:
            link = github_links.pop()
            df.at[idx, 'github'] = link
            for link in github_links:
                data_keys = [key for key in data.keys() if 'github' not in key]
                for key in data_keys:
                    data[key].append(row[key])
                data['github'].append(link)
        else:
            df.at[idx, 'github'] = link

    df_new = pd.DataFrame(data)
    return pd.concat([df, df_new])

def prepare_secbench(df):
    df = df[['owner', 'project', 'sha', 'cve_id', 'cwe_id', 'score']]
    for idx, row in df.iterrows():
        df.at[idx, 'github'] = "https://github.com/{}/{}/commit/{}".format(row['owner'], row['project'], row['sha'])
        df.at[idx, 'project'] = "https://github.com/{}/{}".format(row['owner'], row['project'])
    del df['owner']
    return df

def prepare_bigvul(df):
    info = ['cve_id', 'cwe_id', 'vulnerability_classification', 'score', 'ref_link', 'commit_id', 'summary']
    df = df[info].rename(columns={'vulnerability_classification': 'vuln_type', 'ref_link': 'github', 'commit_id': 'sha'})
    return df

def merge_datasets(file):
            
    configs = read_config('config/datasets.json')
    dfs = {config:pd.read_csv(configs[config]) for config in configs}
    
    df_pontas = prepare_pontas(dfs['pontas'])
    df_pontas['dataset'] = 'PONTAS'

    df_cve_details = prepare_cve_details(dfs['cve_details'])
    df_cve_details['dataset'] = 'CVEDETAILS'

    df_secbench = prepare_secbench(dfs['secbench'])
    df_secbench['dataset'] = 'SECBENCH'

    df_big_vul = prepare_bigvul(dfs['big_vul'])
    df_big_vul['dataset'] = 'BIGVUL'

    df = pd.concat([df_pontas, df_cve_details, df_secbench, df_big_vul], ignore_index=True)

    for idx, row in df[df['dataset'] == 'PONTAS'].iterrows():
        df.at[idx, 'github'] = "{}/commit/{}".format(row['project'], row['sha'])

    for idx, row in df[df['dataset'] == 'CVEDETAILS'].iterrows():
        if 'pull/' in row['github']:
            project, tail = row['github'].split('pull')
            sha = tail.split('commits')[1]
        else:
            project, sha = row['github'].split('commit')
        df.at[idx, 'project'] = project[0:-1]
        df.at[idx, 'sha'] = sha[1::]
        
    for idx, row in df[df['dataset'] == 'BIGVUL'].iterrows():
        if 'pull/' in row['github']:
            project, tail = row['github'].split('pull')
        else:
            if 'github.com' in row['github']:
                project, _ = row['github'].split('commit')       
    
        if 'github.com' in row['github']:
            df.at[idx, 'project'] = project[0:-1]
    
    to_delete = [idx for idx, row in df.iterrows() if 'github.com' not in row['github']]
    df = df.drop(to_delete)

    df = df.drop_duplicates(['cve_id', 'github'], keep='last')

    df.to_csv(file, index=False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Data Manipulation CLI')
    parser.add_argument('--mode', dest='format', choices=['merge'])
    parser.add_argument('-file', type=str, metavar='output file', help='base file')
    
    args = parser.parse_args()
    
    if args.format == 'merge':  
        if args.file != None:
            merge_datasets(args.file)
    else:
        print('Something is wrong. Verify your parameters')