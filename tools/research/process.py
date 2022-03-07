import argparse
import csv

import pandas as pd

from os import listdir
from os.path import isfile, join


def devign(root_folder, projects):
    files = [f for f in listdir(projects) if isfile(join(projects, f))]

    df = pd.concat([pd.read_csv(f"{projects}/{file}") for file in files])
    df = df[df["vulnerability"] == 1]
    df.drop("vulnerability", inplace=True, axis=1)
    df.to_csv(f"{root_folder}/github-devign-patches.csv", index=False)


def big_vul(root_folder, fin, fout):
    df = pd.read_csv(f"{root_folder}/{fin}")
    df = df.rename(columns={"ref_link": "refs"})
    df["refs"] = df["refs"].apply(lambda ref: set([ref]))
    df.to_csv(
        f"{root_folder}/{fout}",
        quoting=csv.QUOTE_NONNUMERIC,
        escapechar="\\",
        doublequote=False,
        index=False,
    )


def sap(root_folder, fin, fout):
    df = pd.read_csv(f"{root_folder}/{fin}")
    df["refs"] = df.apply(lambda x: f"{x['project']}/commit/{x['sha']}", axis=1)
    df.to_csv(f"{root_folder}/{fout}", index=False)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Research Datasets Processor")
    parser.add_argument(
        "--root-folder",
        type=str,
        metavar="input folder",
        help="folder where the data is available",
    )
    parser.add_argument(
        "--fin", type=str, metavar="input file", help="file where the data is available"
    )
    parser.add_argument(
        "--fout",
        type=str,
        metavar="input file",
        help="file where the data is available",
    )
    parser.add_argument(
        "--projects",
        type=str,
        metavar="projects folder",
        help="folder where the data is available",
    )
    parser.add_argument(
        "--name",
        type=str,
        metavar="research dataset name",
        help="research dataset name",
    )

    args = parser.parse_args()
    if args.root_folder and args.projects and args.name == "devign":
        devign(args.root_folder, args.projects)
    elif args.root_folder and args.fin and args.name == "big_vul":
        big_vul(args.root_folder, args.fin, args.fout)
    elif args.root_folder and args.fin and args.fout and args.name == "sap":
        sap(args.root_folder, args.fin, args.fout)
    else:
        print("Something is wrong.")
