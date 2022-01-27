import json
import argparse
import os

import pandas as pd
from tqdm import tqdm

from os import listdir
from os.path import isfile, join

def process(ecosystem, fout):
    
    files = [f for f in listdir(ecosystem) if isfile(join(ecosystem, f))]

    osv_path_out = f"{fout}/all_osv_patches.csv"
    if os.path.exists(osv_path_out):
        df = pd.read_csv(osv_path_out)
    else:
        df = pd.DataFrame()

    count = 0
    for file in files:
        file_path = f"{ecosystem}/{file}"
        with open(file_path) as jfile:
            data = json.load(jfile)
        
        refs, code_refs = set(), set()
        if 'references' in data.keys():
            refs = set([ref['url'] for ref in data['references'] if 'url' in ref.keys()])
            code_refs = set([ref for ref in refs if 'commit/' in ref or 'commits/' in ref])
        
        introduced, fixed = set(), set()
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
        
        code_refs = set.union(code_refs, fixed)
        
        if len(code_refs) > 0:
            vuln_data = {
                'ecosystem': ecosystem,
                'vuln_id': data['id'] if 'id' in data.keys() else data['ghsaId'],
                'summary': data['summary'] if 'summary' in data.keys() else None,
                'details': data['details'] if 'details' in data.keys() else None,
                'aliases': set(data['aliases']) if 'aliases' in data.keys() else None,
                'modified_date': data['modified'] if 'modified' in data.keys() else data['updatedAt'],
                'published_date': data['published'] if 'published' in data.keys() else data['publishedAt'],
                'refs': refs if 'references' in data.keys() else None,
                'code_refs': code_refs if 'references' in data.keys() else None,
                'introduced': introduced if len(introduced) > 0 else None
            }
            count += 1
            df = df.append(vuln_data, ignore_index=True)
    
    if count > 0:
        print(f"+{count} vulnerabilities from {ecosystem}: len={len(df)}")
        df.to_csv(osv_path_out, index=False)

    

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(
        description='Open Source Vulnerability Database Processor (https://osv.dev/)'
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
