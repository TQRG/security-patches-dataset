import json
import argparse
import os

import pandas as pd
from tqdm import tqdm

from os import listdir
from os.path import isfile, join

def create_df(vuln_data):
    return pd.DataFrame(vuln_data, index=[0])

def process(ecosystem, fout):
    
    files = [f for f in listdir(ecosystem) if isfile(join(ecosystem, f))]
    
    osv_path_out = f"{fout}/raw-osv-data.csv"
    if os.path.exists(osv_path_out):
        df = pd.read_csv(osv_path_out)
        first = False
    else:
        first = True

    for file in files:
        file_path = f"{ecosystem}/{file}"
        with open(file_path) as jfile:
            data = json.load(jfile)
        
        refs = set()
        if 'references' in data.keys():
            refs = set([ref['url'] for ref in data['references'] if 'url' in ref.keys()])
        
        introduced, fixed = set(), set()
        severity, score, cwes = None, None, []
        if 'affected' in data.keys():
            if 'ranges' in data['affected'][0].keys():
                ranges = data['affected'][0]['ranges']
                if len(ranges) > 1:
                    for range in ranges:
                        if range['type'] == 'GIT':
                            for event in range['events']:
                                if 'introduced' in event.keys():
                                    if event['introduced'] != '0':
                                        introduced.add(f"{range['repo']}/commit/{event['introduced']}")
                                    else:
                                        introduced.add('0')
                                elif 'fixed' in event.keys():
                                    fixed.add(f"{range['repo']}/commit/{event['fixed']}")
            
            if 'database_specific' in data['affected'][0].keys():
                db_spec = data['affected'][0]['database_specific']
                if 'cwes' in db_spec.keys():
                    for cwe in db_spec['cwes']:
                        cwes.append(cwe['cweId'])
                if 'cvss' in db_spec.keys():
                    if db_spec['cvss'] and type(db_spec['cvss']) != str:
                        if 'score' in db_spec['cvss'].keys():
                            score = db_spec['cvss']['score']
            if 'ecosystem_specific' in data['affected'][0].keys():
                eco_spec = data['affected'][0]['ecosystem_specific']
                if 'severity' in eco_spec.keys():
                    severity = eco_spec['severity']
        
        refs = set.union(refs, fixed)
        
        vuln_data = {
                'ecosystem': str(ecosystem),
                'vuln_id': data['id'] if 'id' in data.keys() else data['ghsaId'],
                'summary': str(data['summary'].replace("\r\n"," ").replace("\n"," ")) if 'summary' in data.keys() else None,
                'details': str(data['details'].replace("\r\n"," ").replace("\n"," ")) if 'details' in data.keys() else None,
                'aliases': str(set(data['aliases'])) if 'aliases' in data.keys() else None,
                'modified_date': data['modified'] if 'modified' in data.keys() else data['updatedAt'],
                'published_date': data['published'] if 'published' in data.keys() else data['publishedAt'],
                'severity': severity,
                'score': score,
                'cwe_id': ','.join(cwes) if len(cwes) > 0 else None,
                'refs': str(refs) if 'references' in data.keys() else None,
                'introduced': str(introduced) if len(introduced) > 0 else None
            }

        if first:
            df, first = create_df(vuln_data), False
        else:
            df = pd.concat([df, create_df(vuln_data)], ignore_index=True)
            
    print(f"+{len(files)} vulnerabilities from {ecosystem}: len={len(df)}")
    df.to_csv(osv_path_out, index=False)

    

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(
        description='Open Source Vulnerability Database Extractor (https://osv.dev/)'
        )
    parser.add_argument('--ecosystem', 
                        type=str, 
                        metavar='ecosystem name', 
                        help='visit the OSV website to see the ecosystems available'
                        )
    parser.add_argument('--fout', 
                        type=str, 
                        metavar='output file', 
                        help='file where data will be appended'
                        )

    args = parser.parse_args()
    if args.ecosystem and args.fout:  
        process(args.ecosystem, args.fout)
    else:
        print('Something is wrong.')
