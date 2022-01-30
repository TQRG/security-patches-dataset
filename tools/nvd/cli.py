import argparse
import json
import os
from os import listdir
from os.path import isfile, join

import pandas as pd
from tqdm import tqdm

def nvd_extractor(folder, fout):
    """ Extracts raw data from NVD .json files. """
    # create output folder
    if not os.path.exists(fout):
        os.mkdir(fout)

    cve_files = [f for f in listdir(folder) if isfile(join(folder, f)) and '.json' in f]
    df = pd.DataFrame()

    for fname in cve_files:
        print(fname)
        with open(f"{folder}{fname}") as f:
            cve_items = json.load(f)['CVE_Items']

        for cve in tqdm(cve_items):
            cve_id = cve['cve']['CVE_data_meta']['ID']
            year = cve_id.split('-')[1]

            for data in cve['cve']['problemtype']['problemtype_data']:
                cwe_ids = set([cwe['value'] for cwe in data['description']])
            
            refs = cve['cve']['references']['reference_data']
            
            description = cve['cve']['description']['description_data'][0]['value']

            if cve['impact']:
                if 'baseMetricV2' in cve['impact'].keys():
                    severity = cve['impact']['baseMetricV2']['severity']
                    exploitability = cve['impact']['baseMetricV2']['exploitabilityScore']
                    impact = cve['impact']['baseMetricV2']['impactScore']

            published_date = cve['publishedDate']
            last_modified_date = cve['lastModifiedDate']
            df = df.append({'cve_id': cve_id, 'year': year, 'cwes': cwe_ids, \
                                'description': description, 'severity': severity, \
                                'exploitability': exploitability, 'impact': impact, \
                                'published_date': published_date, 'last_modified_date': last_modified_date, \
                                'refs': refs}, ignore_index=True)
        df.to_csv(f"{fout}raw-nvd-data.csv", index=False)
        df.to_csv(f"{fout}osv-raw-nvd-data.csv", index=False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='NVD Database extractor.')
    parser.add_argument('--task', dest='format', choices=['extractor', 'osv_generator'])
    parser.add_argument('--data', type=str, metavar='input folder', help='base folder')
    parser.add_argument('--fout', type=str, metavar='output folder', help='output folder')
    
    args = parser.parse_args()
    if args.format == 'extractor':
      if args.data and args.fout:
        nvd_extractor(args.data, args.fout)
    else:
        print('Something is wrong. Verify your parameters.')