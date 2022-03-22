import json
import os 
import shutil
import time

from pathlib import Path
from github import Github


def read_config(file_path):
    f = open("{}/{}".format(Path(__file__).parent.absolute(), file_path)) 
    data = json.load(f) 
    f.close()
    return data

def load_config(filename):
    with open("{}/{}".format(Path(__file__).parent.absolute(), filename)) as config:
        data = json.load(config)
    return data

def get_token(tokens):
    for token in tokens:
        git = Github(token['github_token'])
        if git.rate_limiting[0] > 0:
            print(f"Using {token['github_username']}'s token {git.rate_limiting}...")
            return git
    print(f"No tokens available. Waiting 1h...")
    time.sleep(3610)

def archive_vuln(path, repo):
    with open(path, 'wb') as vv:
        repo.archive(vv)

def remove_dir(path):
    for the_file in os.listdir(path):
        file_path = os.path.join(path, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(e)
    if os.path.exists(path+'/'):
        shutil.rmtree(path+'/')

def check_if_dir_exists(path):
    d=os.path.dirname(path)
    if not os.path.exists(d):
        os.makedirs(d)
