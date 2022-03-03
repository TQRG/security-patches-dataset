import json
import argparse
import os
import re
import csv

import pandas as pd
import numpy as np

from os import listdir
from os.path import isfile, join

def process_ecosystem_vulns(ecosystem, fout):
    """ Process vulnerability data collected from the Open Source Vulnerability (OSV) 
        for a specific ecosystem. """

    def get_ecosytem_vulns(ecosystem):
        """ Get files downloaded for each ecosystem. """
        return [f for f in listdir(ecosystem) if isfile(join(ecosystem, f))]

    def check_if_osv_db_exists(path):
        """ Checks if OSV database already exists. """
        if os.path.exists(path):
            return pd.read_csv(path, escapechar="\\"), False
        else:
            return None, True

    def load_file(ecosystem, file):
        """ Load vulnerability data stored in a JSON file. """
        file_path = f"{ecosystem}/{file}"
        with open(file_path) as jfile:
            return json.load(jfile)
    
    def create_df(vuln_data):
        return pd.DataFrame(vuln_data, index=[0])
    
    def get_references(data):
        if 'references' in data.keys():
            return set([ref['url'] for ref in data['references'] if 'url' in ref.keys()])

    def get_commit_links(data):
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
        return introduced, fixed
            
    def get_severity(data):
        if 'affected' in data.keys():
            if 'ecosystem_specific' in data['affected'][0].keys():
                eco_spec = data['affected'][0]['ecosystem_specific']
                if 'severity' in eco_spec.keys():
                    return eco_spec['severity']


    def get_cwes(data):
        cwes = []
        if 'affected' in data.keys():
            if 'database_specific' in data['affected'][0].keys():
                db_spec = data['affected'][0]['database_specific']
                if 'cwes' in db_spec.keys():
                    for cwe in db_spec['cwes']:
                        cwes.append(cwe['cweId'])
        return cwes
    
    def get_score(data):
        if 'affected' in data.keys():
            if 'database_specific' in data['affected'][0].keys():
                db_spec = data['affected'][0]['database_specific']
                if 'cvss' in db_spec.keys():
                    if db_spec['cvss'] and type(db_spec['cvss']) != str:
                        if 'score' in db_spec['cvss'].keys():
                            return db_spec['cvss']['score']
            

    osv_path_out = f"{fout}/raw-osv-data.csv"
    df, first = check_if_osv_db_exists(osv_path_out)
    files = get_ecosytem_vulns(ecosystem)

    # iterate over the ecosystem vulns
    for file in files:
        data = load_file(ecosystem, file)
        refs = get_references(data)
        
        introduced, fixed = get_commit_links(data)
        if refs and fixed:
            refs = set.union(refs, fixed)

        cwes = get_cwes(data)
        score = get_score(data)        
        severity = get_severity(data)

        vuln_data = {
            'ecosystem': str(ecosystem),
            'vuln_id': data['id'] if 'id' in data.keys() else data['ghsaId'],
            'summary': data['summary'] if 'summary' in data.keys() else np.nan,
            'details': data['details'] if 'details' in data.keys() else np.nan,
            'aliases': str(set(data['aliases'])) if 'aliases' in data.keys() and len(data['aliases']) > 0 else np.nan,
            'modified_date': data['modified'] if 'modified' in data.keys() else data['updatedAt'],
            'published_date': data['published'] if 'published' in data.keys() else data['publishedAt'],
            'severity': severity if severity is not None else np.nan,
            'score': score if score is not None else np.nan,
            'cwe_id': str(set(cwes)) if len(cwes) > 0 else np.nan,
            'refs': str(refs) if 'references' in data.keys() and len(refs) > 0 else np.nan,
            'introduced': str(introduced) if len(introduced) > 0 else np.nan
        }

        if first:
            df, first = create_df(vuln_data), False
        else:
            df = pd.concat([df, create_df(vuln_data)], ignore_index=True)
    
    print(f"+{len(files)} vulnerabilities from {ecosystem}: len={len(df)}")
    df.to_csv(osv_path_out, 
                quoting=csv.QUOTE_NONNUMERIC, 
                escapechar="\\", 
                doublequote=False, 
                index=False)

    

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
        process_ecosystem_vulns(args.ecosystem, args.fout)
    else:
        print('Something is wrong.')
