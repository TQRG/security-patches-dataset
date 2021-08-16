import sys
import time
import argparse
import datetime
from os import path
import json

import requests as req
import pandas as pd
from bs4 import BeautifulSoup
from tqdm import tqdm

WEBSITE_URL ='https://www.cvedetails.com'

def get_cve_url_content(cve_url):
    cve_details_page = req.get(cve_url)
    return BeautifulSoup(cve_details_page.content, 'html.parser')

def get_refs(cve_url_cont):    
    refs_table = cve_url_cont.find(id='vulnrefstable') 
    references = []
    if refs_table:
        refs = refs_table.find_all('a')
        for ref in refs:
            ref_url_lower = ref['href'].strip().lower()
            ref_url = ref['href'].strip()
            if 'advisory' in ref_url_lower or \
                'access.redhat.com' in ref_url_lower or \
                'advisories' in ref_url_lower:
                references.append({"type": "ADVISORY", "url": ref_url})
            elif 'commits/' in ref_url_lower or \
                'commit/' in ref_url_lower:
                references.append({"type": "FIX", "url": ref_url})
            elif 'blog' in ref_url_lower or \
                'article' in ref_url_lower:
                references.append({"type": "BLOG", "url": ref_url})
            elif 'bugs.chromium.org' in ref_url_lower or \
                'snyk.io' in ref_url_lower or \
                'gerrit' in ref_url_lower or \
                'securityfocus.com' in ref_url_lower or \
                'issues/' in ref_url_lower or \
                'pull/' in ref_url_lower:
                references.append({"type": "REPORT", "url": ref_url})
            elif 'package' in ref_url_lower:
                references.append({"type": "PACKAGE", "url": ref_url})
            elif 'exploit' in ref_url_lower:
                references.append({"type": "EXPLOIT", "url": ref_url})
            else:
                references.append({"type": "WEB", "url": ref_url})
    return references
 
def load_data(fpath):
    if path.exists(fpath):
        with open(fpath) as f:
            return json.load(f)
    return []

def get_pagination(url, soup):
    pagination = soup.find(id='pagingb') 
    return [f"{url}{page['href']}" for page in pagination.find_all('a')]

def get_pages(year, page_start):
    page = req.get(f"{WEBSITE_URL}/vulnerability-list/year-{year}/vulnerabilities.html")
    soup = BeautifulSoup(page.content, 'html.parser')
    return get_pagination(WEBSITE_URL, soup)[page_start::]

def get_cves_rows(soup):
    cves_list = soup.find(id='searchresults')
    cves_rows = cves_list.find_all('tr')
    return cves_rows

def strip_text(text):
    return text.getText().strip()

def parse_cves_rows(rows):
    cves_data = []
    for i in range(1,len(rows[1::]), 2):
        tds = rows[i].find_all('td')
        packages, affects = [], []

        cve_url = f"{WEBSITE_URL}{tds[1].a['href'].strip()}"
        cve_url_cont = get_cve_url_content(cve_url)

        database_spec = {
            "CWE": f"CWE-{strip_text(tds[2].a)}" if tds[2].a != None else "",
            "CVSS_V2": {
                "score": strip_text(tds[7].div)
            },
            "vuln_type": strip_text(tds[4]),
            "url": cve_url,
            "acess_level": strip_text(tds[8]),
            "access": strip_text(tds[9]),
            "complexity": strip_text(tds[10]),
            "authentication": strip_text(tds[11]),
            "impact": {
                "confidentiality":  strip_text(tds[12]),
                "integrity":  strip_text(tds[13]),
                "availability":  strip_text(tds[14])
            } 
        }

        cve_data = {
            "id": strip_text(tds[1].a),
            "modified": strip_text(tds[6]),
            "published": strip_text(tds[5]),
            "details": strip_text(rows[i+1].find_all('td')[0]),
            "references": get_refs(cve_url_cont),
            "database_specific": database_spec
        }
        cves_data.append(cve_data)
    return cves_data

def get_cves_info(page):
    cves_list_page = req.get(page.strip())
    soup = BeautifulSoup(cves_list_page.content, 'html.parser')
    rows = get_cves_rows(soup)
    return parse_cves_rows(rows)

def scrape_cve_details(year, fpath, db):
    fopath = f"{fpath}/{db}-{year}.json"
    cves_data = load_data(fopath)
    page_start = int(len(cves_data)/50)
    print(f"Starting at page {page_start}")
    pages = get_pages(year, page_start)

    for page in tqdm(pages):
        print(f"Scraping page: {page}")
        cves_data += get_cves_info(page)
        with open(fopath, 'w') as outfile:
            json.dump(cves_data, outfile, indent=4)

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Web Scraping Tool Known Vulnerability Databases:')
    parser.add_argument('--mode', dest='format', choices=['per_year'])
    parser.add_argument('-year', type=str, metavar='year', help='year')
    parser.add_argument('-db', type=str, metavar='database', help='database')
    parser.add_argument('-folder', type=str, metavar='output folder name', help='file path to save the results')
    
    args = parser.parse_args()
    
    now = datetime.datetime.now()
    years = (year for year in range(1999, now.year+1))

    if args.format == 'per_year':  
        if args.folder and int(args.year) in years and args.db:
            print(f"Scraping data from {WEBSITE_URL} for year {args.year} to file: {args.folder}")
            scrape_cve_details(args.year, args.folder, args.db)
        else:
            print('Something is wrong with the output file name or year.')
    if args.format == 'all':
        print(f"Scraping data from {WEBSITE_URL} from x to y to file: {args.folder}")
    else:
        print('Mode is wrong. per_year available.')
