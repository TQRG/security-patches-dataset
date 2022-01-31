import json
import argparse
import os

import pandas as pd
from tqdm import tqdm

from os import listdir
from os.path import isfile, join

def devign(root_folder, projects):
    
    files = [f for f in listdir(projects) if isfile(join(projects, f))]
    
    df = pd.concat([pd.read_csv(f"{projects}/{file}") for file in files])
    df = df[df['vulnerability'] == 1]
    df.drop('vulnerability', inplace=True, axis=1)
    df.to_csv(f"{root_folder}/github-devign-patches.csv", index=False)

def big_vul(root_folder, fin):

    df = pd.read_csv(f"{root_folder}/{fin}")
    df = df[df['ref_link'].str.contains("github.com")]
    df.to_csv(f"{root_folder}/github-big-vul-patches.csv", index=False)


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(
        description='Research Datasets Processor'
        )
    parser.add_argument('--root-folder', 
                        type=str, 
                        metavar='input folder', 
                        help='folder where the data is available'
                        )
    parser.add_argument('--fin', 
                        type=str, 
                        metavar='input file', 
                        help='file where the data is available'
                        )
    parser.add_argument('--projects', 
                        type=str, 
                        metavar='projects folder', 
                        help='folder where the data is available'
                        )
    parser.add_argument('--name', 
                        type=str, 
                        metavar='research dataset name', 
                        help='research dataset name'
                        )


    args = parser.parse_args()
    if args.root_folder and args.projects and args.name == 'devign':
        devign(args.root_folder, args.projects, args.name)
    elif args.root_folder and args.fin and args.name == 'big_vul':  
        big_vul(args.root_folder, args.fin)
    else:
        print('Something is wrong.')
