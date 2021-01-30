import argparse 
import os
import sys

import pandas as pd

ext_map = {'Objective-C': {'m', 'mm'}, 'Java': {'java', 'jsp', 'jspf'}, 'Scala': {'scala'},
            'C/C++': {'c', 'cc', 'cpp', 'h', 'c++'}, 'Groovy': {'groovy'}, 'PHP': {'php', 'tpl', 'inc', 'ctp', 'phpt', 'phtml'},
            'JavaScript': {'js', 'jsx', 'coffee'}, 'Python': {'py'}, 'Config files': {'lock', 'gradle', 'json', 'config', 'yaml', 'conf'},
            'Ruby': {'rb'}, 'HTML': {'html', 'erb'}, 'Perl': {'pm'}, 'Go': {'go'}, 'Lua': {'lua'}, 'Erlang': {'erl'}, 'C#': {'cs'},
            'Rust': {'rust'}, 'Vala': {'vala'}, 'SQL': {'sql'}, 'XML': {'xml'}, 'Shell': {'sh'}}

def get_extensions(files_list):
    extensions = set()
    for f in files_list:
        extension = f.split('/')[-1].split('.')
        if len(extension) > 1:
            extensions = extensions | set([extension[-1]])
    return extensions

def add_ext_files(filename):
    df = pd.read_csv(filename)
    for idx, row in df.iterrows():
        extensions = get_extensions(eval(row['files']))
        if len(extensions) != 0:
            df.at[idx, 'ext_files'] = str(extensions)
    df.to_csv(filename, index=False)

def get_language(ext):
    languages = set()
    for lang in ext_map:
        if ext in ext_map[lang]:
            languages.add(lang)
    return languages

def add_prog_language(filename):
    df = pd.read_csv(filename)
    for idx, row in df.iterrows():
        if pd.notnull(row['ext_files']):
            ext_files = eval(row['ext_files'])
            languages = set()
            for ext in list(ext_files):
                languages = languages | get_language(ext)
            if len(languages) != 0:
                df.at[idx, 'lang'] = str(languages)
    df.to_csv(filename, index=False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Add features')
    parser.add_argument('--feature', dest='format', choices=['ext_files', 'lang'])
    parser.add_argument('-file', type=str, metavar='input file', help='input file')
    
    args = parser.parse_args()

    if args.format == 'ext_files':  
        if args.file != None:
            add_ext_files(args.file)
    elif args.format == 'lang':
        if args.file != None:
            add_prog_language(args.file)
    else:
        print('Something is wrong. Verify your parameters')