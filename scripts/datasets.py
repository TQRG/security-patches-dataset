import normalize as norm
import pandas as pd
import numpy as np

class Devign:
    def __init__(self, df):
        self.df = df

    def prepare(self):
        """ Prepare Devign dataset. """
        self.df = self.df.rename(columns={'sha_id': 'fix_commit'})

    
class SAP:
    def __init__(self, df):
        self.df = df

    def prepare(self):
        """ Prepare SAP dataset. """
        self.df = self.df.rename(columns={'sha': 'fix_commit', 'cve_id': 'vuln_id', 'commits': 'chain'})
        del self.df['type']
    
    def normalize(self):
        print("Normalizing SAP ...")
        self.df['chain'] = self.df['chain'].apply(lambda x: norm.split_commits(x))
        self.df['chain'] = self.df['chain'].apply(lambda x: norm.commit(x))
        print(f"Entries: {len(self.df)}")
        self.df = self.df.dropna(subset=['chain'])
        print(f"Entries (After duplicates): {len(self.df)}")
        self.df['chain_len'] = self.df['chain'].apply(lambda x: len(x))
        self.df['commit_href'] = self.df['chain'].apply(lambda x: len(x))
        del self.df['refs']
        del self.df['code_refs']
        print(self.df.keys())

class SECBENCH:
    def __init__(self, df):
        self.df = df

    def prepare(self):
        """ Prepare SECBENCH dataset. """
        self.df = self.df.rename(columns={'sha': 'fix_commit', 
                                            'cve_id': 'vuln_id'})
        self.df['cwe_id'] = self.df['cwe_id'].apply(lambda x: norm.to_set(x))
        self.df = self.df[['owner', 'project', 'fix_commit', 'vuln_id', 'cwe_id', 'score', 'dataset']]
    
    def normalize(self):
        print("Normalizing Secbench ...")
        self.df['chain'] = self.df.apply(lambda x: norm.chain(x['owner'], x['project'], x['fix_commit']), axis=1)        
        self.df['chain'] = self.df['chain'].apply(lambda x: norm.commit(x))
        print(f"Entries: {len(self.df)}")
        self.df = self.df.dropna(subset=['chain'])
        print(f"Entries (After duplicates): {len(self.df)}")
        self.df['chain_len'] = self.df['chain'].apply(lambda x: len(x))
        self.df['project'] = self.df.apply(lambda x: norm.project_from_meta(x['owner'], x['project']), axis=1)
        del self.df['owner']


class BIGVUL:
    def __init__(self, df):
        self.df = df

    def prepare(self):
        """ Prepare BIG-VUL dataset. """
        self.df = self.df.rename(columns={'commit_id': 'fix_commit', 
                                            'cve_id': 'vuln_id', 
                                            'publish_date': 'published_date', 
                                            'commits': 'chain'})
        self.df['cwe_id'] = self.df['cwe_id'].apply(lambda x: norm.to_set(x))
        self.df = self.df[['vuln_id', 'cwe_id', 'score', 'chain', 'fix_commit', 'dataset', 'summary', 'published_date', 'project']]

    def normalize(self):
        print("Normalizing Big-Vul ...")
        self.df['chain'] = self.df['chain'].apply(lambda x: norm.split_commits(x))
        # for each vuln_id
        for vuln_id in self.df['vuln_id'].unique():
            # if nan vuln_id, vuln belongs to the Chrome project; 
            # Chrome only contains single patches; this was verified earlier
            if not pd.notna(vuln_id):
                self.df.at[rows.index.values[0], 'commit'] = next(iter(self.df['chain'].iloc[rows.index].values[0]))
                self.df.at[rows.index.values[0], 'patch'] = 'SINGLE'
                continue
            # get all the commits for each vuln
            rows = self.df[self.df['vuln_id'] == vuln_id]
            # if multi commit patch (n_commits > 1)
            if len(rows) > 1:
                chain = [list(commit)[0] for commit in rows['chain']]
                count = 0
                for idx, row in rows.iterrows():                
                    self.df.at[idx, 'chain'] = set(chain)
                    self.df.at[idx, 'commit'] = chain[count]
                    self.df.at[idx, 'patch'] = 'MULTI'
                    count+=1
            # if single commit patch (n_commits == 1)
            else:
                self.df.at[rows.index.values[0], 'commit'] = next(iter(self.df['chain'].iloc[rows.index].values[0]))
                self.df.at[rows.index.values[0], 'patch'] = 'SINGLE'
        
        self.df['chain'] = self.df['chain'].apply(lambda x: norm.commit(x))
        print(f"Entries: {len(self.df)}")
        self.df = self.df.dropna(subset=['chain'])
        print(f"Entries (After duplicates): {len(self.df)}")
        self.df['chain_len'] = self.df['chain'].apply(lambda x: len(x))
        self.df['project'] = self.df['chain'].apply(lambda x: norm.project_from_chain(x))


class NVD:
    def __init__(self, df):
        self.df = df

    def prepare(self):
        """ Prepare NVD dataset."""
        self.df = self.df.rename(columns={'cve_id': 'vuln_id', 'cwes':'cwe_id', 'commits': 'chain', 'description': 'summary', 'impact': 'score'})
        self.df = self.df[['vuln_id', 'cwe_id', 'score', 'chain', 'dataset', 'summary', 'published_date']]
        
    def normalize(self):
        print("Normalizing NVD ...")
        self.df['chain'] = self.df['chain'].apply(lambda x: norm.split_commits(x))
        self.df['chain'] = self.df['chain'].apply(lambda x: norm.commit(x))
        print(f"Entries: {len(self.df)}")
        self.df = self.df.dropna(subset=['chain'])
        print(f"Entries (After duplicates): {len(self.df)}")
        self.df['chain_len'] = self.df['chain'].apply(lambda x: len(x))
        self.df['project'] = self.df['chain'].apply(lambda x: norm.project_from_chain(x))
        self.df['published_date'] = self.df['published_date'].apply(lambda x: norm.date(x))

class OSV:
    def __init__(self, df):
        self.df = df

    def prepare(self):
        """ Prepare OSV dataset. """
        self.df = self.df.rename(columns={'commits': 'chain'})
        self.df['summary'] = self.df.apply(lambda x: norm.join(x['summary'], x['details']), axis=1)
        self.df = self.df[['vuln_id', 'cwe_id', 'score', 'chain', 'dataset', 'summary', 'published_date']]

    def normalize(self):
        print("Normalizing OSV ...")
        self.df['chain'] = self.df['chain'].apply(lambda x: norm.split_commits(x))
        self.df['chain'] = self.df['chain'].apply(lambda x: norm.commit(x))
        print(f"Entries: {len(self.df)}")
        self.df = self.df.dropna(subset=['chain'])
        print(f"Entries (After duplicates): {len(self.df)}")
        self.df['chain_len'] = self.df['chain'].apply(lambda x: len(x))
        self.df['project'] = self.df['chain'].apply(lambda x: norm.project_from_chain(x))
        self.df['published_date'] = self.df['published_date'].apply(lambda x: norm.date(x))

class CVEDetails:
    def __init__(self, df):
        self.df = df

    def prepare(self):
        """ Prepare CVE Details dataset. """
        self.df = self.df.rename(columns={'cve_id': 'vuln_id', 'publish_date': 'published_date', 'commits': 'chain'})
        self.df['cwe_id'] = self.df['cwe_id'].apply(lambda x: norm.to_set(x))
        self.df = self.df[['vuln_id', 'cwe_id', 'score', 'chain', 'summary', 'dataset', 'published_date']]

    def normalize(self):
        print("Normalizing CVE Details ...")
        self.df['chain'] = self.df.apply(lambda x: norm.split_commits(x['chain']), axis=1)
        self.df['chain'] = self.df['chain'].apply(lambda x: norm.commit(x))
        print(f"Entries: {len(self.df)}")
        self.df = self.df.dropna(subset=['chain'])
        print(f"Entries (After duplicates): {len(self.df)}")
        self.df['chain_len'] = self.df['chain'].apply(lambda x: len(x))
        self.df['project'] = self.df['chain'].apply(lambda x: norm.project_from_chain(x))