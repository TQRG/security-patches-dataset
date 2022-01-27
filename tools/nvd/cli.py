import argparse
import json
import yaml

from os import listdir
from os.path import isfile, join
from tqdm import tqdm
import os

import pandas as pd

def nvd_extractor(folder, fout):

    # create output folder
    if not os.path.exists(fout):
        os.mkdir(fout)

    cve_files = [f for f in listdir(folder) if isfile(join(folder, f)) and '.json' in f]
    df = pd.DataFrame()

    for fname in cve_files:
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

def check_if_oss(references):
    refs = set(ref['url'] for ref in references)
    return len(set(r for r in refs if 'commit/' in r)) > 0, refs

def get_refs(refs):
    cve_refs = []
    for ref in refs:
        if 'commit/' in ref or 'commits/' in ref:
            cve_refs.append({'type': 'FIX', 'url': ref})
        elif 'issue' in ref or 'issues' in ref or 'show_bug' in ref or \
            'bugs.debian.org/' in ref or 'bugs.gentoo.org/' in ref or \
            'syzkaller.appspot.com/bug?' in ref or 'savannah.gnu.org/bugs' in ref or \
            'bugs.launchpad.net' in ref or 'hackerone.com/bugs' in ref or\
            'hackerone.com/bugs' in ref:
            cve_refs.append({'type': 'REPORT', 'url': ref})
        elif 'advisory' in ref or 'advisories' in ref or 'www.debian.org/security/' in ref:
            cve_refs.append({'type': 'ADVISORY', 'url': ref})
        elif 'arxiv.org' in ref:
            cve_refs.append({'type': 'ARTICLE', 'url': ref})
        else:
            cve_refs.append({'type': 'WEB', 'url': ref})
    return cve_refs

def process_cpe(cpe, cpes):
    cpe_s = cpe['cpe23Uri'].split(':')
    cpe, product, version = ':'.join(cpe_s[0:5]), cpe_s[4], cpe_s[5] 

    if product == '\\' or product == '*':
        print(f"Something wrong with the cpe: {cpe_s}")
        return True, cpes

    if product != '*':
        if cpe not in cpes:
            cpes[cpe] = [version] if version not in ('*', '-') else []
        else:
            if version not in ('*', '-'):
                cpes[cpe].append(version)  
    return False, cpes 

def osv_schema_generator(data):

    # create output for osv import
    vulns_output = 'vulns/'
    if not os.path.exists(vulns_output):
        os.mkdir(vulns_output)

    # list all the nvd files available
    cve_files = list(reversed([f for f in listdir(data) if isfile(join(data, f)) and '.json' in f]))

    # iterate over each nvd.json file
    for fname in cve_files:
        # read cves data from nvd.json file
        with open(f"{data}{fname}") as f:
            cve_items = json.load(f)['CVE_Items']
        
        # iterate over each cve
        for cve in cve_items:
            # visit only the open-sourced ones
            is_oss, refs = check_if_oss(cve['cve']['references']['reference_data'])
            
            # if not available
            if not is_oss:
                continue

            # get product names and respective cpes
            cpes = {}
            for node in cve['configurations']['nodes']:
                if node['operator'] == 'OR':
                    for cpe in node['cpe_match']:
                        if cpe['vulnerable']:
                            skip, cpes = process_cpe(cpe, cpes) 
                            if skip:      
                                continue
                else:
                    for children in node['children']:
                        for cpe in children['cpe_match']:
                            if cpe['vulnerable']:
                                skip, cpes = process_cpe(cpe, cpes) 
                                if skip:      
                                    continue

            severity = []
            if 'baseMetricV3' in cve['impact'].keys():
                cvss3 = cve['impact']['baseMetricV3']['cvssV3']
                cwes = [cwe['value'] for cwe in cve['cve']['problemtype']['problemtype_data'][0]['description']]
                severity.append({'type': 'CVSS_V3', 'score': cvss3['baseScore']})
            if 'baseMetricV2' in cve['impact'].keys():
                severity.append({'type': 'CVSS_V2', 'score': cve['impact']['baseMetricV2']['cvssV2']['baseScore']})

            cve_refs, ranges, aliases = get_refs(refs), [], []
            for ref in cve_refs:
                if ref['type'] == 'FIX':
                    url_s = ref['url'].split('/commit/')
                    if len(url_s) != 2:
                        # e.g., https://github.com/systemd/systemd/pull/20256/commits/441e0115646d54f080e5c3bb0ba477c892861ab9
                        try:
                            link, sha = ref['url'].split('/commits/')
                        except Exception as e:      
                            print("Something wrong with the url:", cve['cve']['CVE_data_meta']['ID'], url_s)
                            continue
                        link = link.split('/pull/')[0].replace('/-','/')
                        sha = sha.replace('?id=','')
                    else:
                        # e.g., https://github.com/LoicMarechal/libMeshb/commit/8cd68c54e0647c0030ae4506a225ad4a2655c316
                        link, sha = url_s
                        link = link.replace('/-','/')
                        sha = sha.replace('?id=','')
                    ranges.append({'type': 'GIT', 'repo': link, 'events': [{'introduced': '0'}, {'fixed': sha}]})
                
                if ref['type'] == 'ADVISORY':
                    if 'GHSA' in ref['url']:
                        aliases.append(ref['url'].split('/')[-1])
                if 'OSV-' in ref['url']:
                    aliases.append(ref['url'].split('/')[-1].replace('.yaml',''))

            for cpe in cpes:
                # get product name from cpe:2.3:*:owner:product
                product = cpe.split(':')[-1]

                # create product folder if does not exist
                if not os.path.exists(f"{vulns_output}/{product}/"):
                    try:
                        os.mkdir(f"{vulns_output}/{product}/")
                    except Exception as e:   
                        print(f"Folder for product {product} not created.")   
                        continue 
                
                affected = []
                affected.append({'package': {
                                    'name': product,
                                    'cpe': cpe 
                                }})
                
                affected.append({'ranges': ranges})

                if len(cpes[cpe]) > 0:
                    affected.append({'versions': list(set(cpes[cpe]))})

                # only saving CVSS for V3, should we add V2?
                if 'baseMetricV3' in cve['impact'].keys():
                    affected.append({'database_specific': {
                        'CWE': cwes,
                        'CVSS': {
                            'Score': cvss3['baseScore'],
                            'Severity': cvss3['baseSeverity'],
                            'Code': cvss3['vectorString']
                        }
                    }})
                
                # cve data (OSV schema: https://ossf.github.io/osv-schema/)
                cve_file = {'schema_version': '1.2.0', 
                            'id': cve['cve']['CVE_data_meta']['ID'], 
                            'aliases': list(set(aliases)), 
                            'modified': cve['lastModifiedDate'], 
                            'published': cve['publishedDate'], 
                            'details': cve['cve']['description']['description_data'][0]['value'],
                            'severity': severity,
                            'affected': affected, 
                            'references': cve_refs
                }

                # save data in yaml file   
                try:          
                    with open(f"{vulns_output}/{product}/{cve['cve']['CVE_data_meta']['ID']}.yaml", 'w') as file:
                        yaml.dump(cve_file, file, default_flow_style=False, sort_keys=False)
                except Exception as e:      
                    print(e)   

def nvd_process(fin, fout):
    df = pd.read_csv(fin)
    for idx, row in tqdm(df.iterrows()):
        refs = set([ref['url'] for ref in eval(row['refs']) \
                        if 'commit/' in ref['url']])
        if len(refs) > 0:
            df.at[idx, 'code_refs'] = refs 
    # save d
    df[df['code_refs'].notnull()].to_csv(fout, index=False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='NVD database processor.')
    parser.add_argument('--task', dest='format', choices=['extractor', 'process', 'osv_generator'])
    parser.add_argument('--data', type=str, metavar='input folder', help='base folder')
    parser.add_argument('--fout', type=str, metavar='output folder', help='output folder')
    parser.add_argument('--fin', type=str, metavar='input file', help='input file')
    
    args = parser.parse_args()
    if args.format == 'extractor':
      if args.data and args.fout:
        nvd_extractor(args.data, args.fout)
    elif args.format == 'process':
      if args.fin and args.fout:
        nvd_process(args.fin, args.fout)
    elif args.format == 'osv_generator':
      if args.data:
        osv_schema_generator(args.data)
    else:
        print('Something is wrong. Verify your parameters.')