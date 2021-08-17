import sys
import time
import argparse
import datetime
from os import path

import requests as req
import pandas as pd
from bs4 import BeautifulSoup
from tqdm import tqdm

WEBSITE_URL ='https://www.cvedetails.com'

CVES_DICT = {'cve_id':[], 'cve_href':[], 'cwe_id':[], 'vuln_type':[], 
                'publish_date':[], 'update_date':[], 'score':[], 'acces_level':[],
                'access':[], 'complexity':[], 'authentication':[], 'confidentiality':[], 
                'integrity':[], 'availability':[], 'summary':[], 'refs': []
                }

def get_refs(cve_url):
    cve_details_page = req.get(cve_url)
    soup = BeautifulSoup(cve_details_page.content, 'html.parser')
    refs_table = soup.find(id='vulnrefstable') 
    if refs_table:
        refs = refs_table.find_all('a')
        return set(ref['href'].strip() for ref in refs)
    else:
        return set()
        
def load_data(file):
    if path.exists(file):
        cve_data = pd.read_csv(file)
    else:
        cve_data = pd.DataFrame.from_dict(CVES_DICT)
    return cve_data

def get_pagination(url, soup):
    pagination = soup.find(id='pagingb') 
    pages = ['{}{}'.format(url, page['href']) for page in pagination.find_all('a')]
    return pages

def get_pages(year, page_start):
    page = req.get("{}/vulnerability-list/year-{}/vulnerabilities.html".format(WEBSITE_URL, year))
    soup = BeautifulSoup(page.content, 'html.parser')
    return get_pagination(WEBSITE_URL, soup)[page_start::]

def get_cves_rows(soup):
    cves_list = soup.find(id='searchresults')
    cves_rows = cves_list.find_all('tr')
    return cves_rows

def parse_cves_rows(rows):
    for key in CVES_DICT:
        CVES_DICT[key] = []
    for i in range(1,len(rows[1::]), 2):
        tds = rows[i].find_all('td')
        CVES_DICT['cve_id'].append(tds[1].a.getText().strip())
        CVES_DICT['cve_href'].append('{}{}'.format(WEBSITE_URL, tds[1].a['href'].strip()))
        CVES_DICT['cwe_id'].append('CWE-{}'.format(tds[2].a.getText().strip()) if tds[2].a != None else '') 
        CVES_DICT['vuln_type'].append(tds[4].getText().strip())
        CVES_DICT['publish_date'].append(tds[5].getText().strip())
        CVES_DICT['update_date'].append(tds[6].getText().strip())
        CVES_DICT['score'].append(tds[7].div.getText().strip())
        CVES_DICT['acces_level'].append(tds[8].getText().strip())
        CVES_DICT['access'].append(tds[9].getText().strip())
        CVES_DICT['complexity'].append(tds[10].getText().strip())
        CVES_DICT['authentication'].append(tds[11].getText().strip())
        CVES_DICT['confidentiality'].append(tds[12].getText().strip())
        CVES_DICT['integrity'].append(tds[13].getText().strip())
        CVES_DICT['availability'].append(tds[14].getText().strip())
        CVES_DICT['summary'].append(rows[i+1].find_all('td')[0].getText().strip())
        CVES_DICT['refs'].append(get_refs('{}{}'.format(WEBSITE_URL, tds[1].a['href'].strip())))
    return CVES_DICT

def get_cves_info(page):
    cves_list_page = req.get(page.strip())
    soup = BeautifulSoup(cves_list_page.content, 'html.parser')
    rows = get_cves_rows(soup)
    return parse_cves_rows(rows)

def scrape_cve_details(year, file):

    cve_data = load_data(file)
    page_start = int(len(cve_data)/50)
    print(f"Starting at page {page_start}")
    pages = get_pages(year, page_start)

    for page in tqdm(pages):
        print(f"Scraping page: {page}")
        cves = get_cves_info(page)
        df_cves =  pd.DataFrame.from_dict(cves)
        cve_data = cve_data.append(df_cves, ignore_index=True)
        cve_data.to_csv(file, index=False)

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Web Scraping Tool for CVE Details website (https://www.cvedetails.com/):')
    parser.add_argument('--mode', dest='format', choices=['per_year'])
    parser.add_argument('-year', type=str, metavar='year', help='year of cves')
    parser.add_argument('-file', type=str, metavar='output file', help='file where you want to save the results')
    
    args = parser.parse_args()
    
    now = datetime.datetime.now()
    years = (year for year in range(1999, now.year+1))

    if args.format == 'per_year':  
        if args.file != None and int(args.year) in years:
            scrape_cve_details(args.year, args.file)
        else:
            print('Something wrong with the output file name or year.')
    else:
        print('Mode is wrong. per_year available.')
