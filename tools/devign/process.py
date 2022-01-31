import json
import argparse
import os

import pandas as pd
from tqdm import tqdm

from os import listdir
from os.path import isfile, join

def process(root_folder, projects):
    
    files = [f for f in listdir(projects) if isfile(join(projects, f))]
    
    df = pd.concat([pd.read_csv(f"{projects}/{file}") for file in files])
    df = df[df['vulnerability'] == 1]
    df.drop('vulnerability', inplace=True, axis=1)
    df.to_csv(f"{root_folder}/github-devign-patches.csv", index=False)

    

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(
        description='Devign Dataset Processor (https://sites.google.com/view/devign)'
        )
    parser.add_argument('--root-folder', 
                        type=str, 
                        metavar='input folder', 
                        help='folder where the data is available'
                        )
    parser.add_argument('--projects', 
                        type=str, 
                        metavar='projects folder', 
                        help='folder where the data is available'
                        )


    args = parser.parse_args()
    if args.root_folder and args.projects:  
        process(args.root_folder, args.projects)
    else:
        print('Something is wrong.')
