import argparse
import pandas as pd
import re
import utils
import datasets as data
import normalize as norm
import github_data
from github import Github
import csv
import features

import warnings

warnings.simplefilter(action="ignore", category=FutureWarning)


def transform_to_commits(df):
    new_df = pd.DataFrame()
    for _, row in df.iterrows():
        chain = list(row["chain"])
        patch_type = "MULTI" if len(chain) > 1 else "SINGLE"

        for i, _ in enumerate(chain):
            row["commit_href"] = chain[i]
            row["project"] = "/".join(chain[i].split("/")[0:5])
            sha = re.sub(r"http(s)?://github.com/.*/commit(s)?/", "", chain[i])
            row["commit_sha"] = sha
            row["patch"] = patch_type
            new_df = new_df.append(row, ignore_index=True)
    return new_df


def process_sources(folder):

    config = utils.load_config("config/github.json")
    git = utils.get_token(config)

    dfs = {
        source: pd.read_csv(f"sources/{source}.csv", escapechar="\\")
        for source in ("cve_details", "nvd", "osv")
    }

    for df in dfs:
        dfs[df]["dataset"] = df

    # Sources
    cve_det, osv, nvd = (
        data.CVEDetails(dfs["cve_details"]),
        data.OSV(dfs["osv"]),
        data.NVD(dfs["nvd"]),
    )

    cve_det.prepare()
    cve_det.normalize()
    cve_det.df["chain"] = cve_det.df["chain"].apply(
        lambda chain: norm.normalize_sha(git, config, chain)
    )
    cve_det.df = transform_to_commits(cve_det.df)
    cve_det.df.to_csv(
        f"{folder}/cve_details.csv",
        quoting=csv.QUOTE_NONNUMERIC,
        escapechar="\\",
        doublequote=False,
        index=False,
    )

    osv.prepare()
    osv.normalize()
    osv.df["chain"] = osv.df["chain"].apply(
        lambda chain: norm.normalize_sha(git, config, chain)
    )
    osv.df = transform_to_commits(osv.df)
    osv.df.to_csv(
        f"{folder}/osv.csv",
        quoting=csv.QUOTE_NONNUMERIC,
        escapechar="\\",
        doublequote=False,
        index=False,
    )

    nvd.prepare()
    nvd.normalize()
    nvd.df["chain"] = nvd.df["chain"].apply(
        lambda chain: norm.normalize_sha(git, config, chain)
    )
    nvd.df = transform_to_commits(nvd.df)
    nvd.df.to_csv(
        f"{folder}/nvd.csv",
        quoting=csv.QUOTE_NONNUMERIC,
        escapechar="\\",
        doublequote=False,
        index=False,
    )


def merge_sources(folder):
    dfs = [
        pd.read_csv(f"commits/{source}.csv", escapechar="\\")
        for source in ("cve_details", "osv", "nvd")
    ]
    df = pd.concat(dfs, ignore_index=True)
    print(f"Total number of entries: {len(df)}")
    df.to_csv(
        f"{folder}/sources_commits.csv",
        quoting=csv.QUOTE_NONNUMERIC,
        escapechar="\\",
        doublequote=False,
        index=False,
    )


def get_metadata(fin, folder):
    df = pd.read_csv(fin, escapechar="\\")

    if "message" in df.columns:
        print(
            f"{len(df[~pd.notnull(df['files'])])} entries \
            to go out of {len(df)}"
        )
    else:
        print(f"{len(df)} entries to go")

    config = utils.load_config("config/github.json")
    git = utils.get_token(config)

    fout = f"{folder}/sources_commits_metadata.csv"

    repos = set(df["project"])
    for repo in repos:
        print(f"📂 Getting the metadata from project {repo}...")
        git, df = github_data.metadata(repo, df, git, config)

        if "message" in df.columns:
            print(f"{len(df[~pd.notnull(df['files'])])} entries to go")
        else:
            print(f"{len(df)} entries to go")

        df.to_csv(
            fout,
            quoting=csv.QUOTE_NONNUMERIC,
            escapechar="\\",
            doublequote=False,
            index=False,
        )


def filter_data(fin, folder):
    df = pd.read_csv(fin, escapechar="\\")
    df[pd.notnull(df["message"])].to_csv(
        f"{folder}/final_dataset.csv",
        quoting=csv.QUOTE_NONNUMERIC,
        escapechar="\\",
        doublequote=False,
        index=False,
    )


def collect_feature(fin, folder, feature):
    df = pd.read_csv(fin, escapechar="\\")
    if feature == "extension":
        df["files_extension"] = df["files"].apply(
            lambda x: features.get_files_extension(x)
        )
    elif feature == "language":
        df["files"] = df["files"].apply(lambda x: norm.clean_nan(x))
        df["files_extension"] = df["files"].apply(
            lambda x: features.get_files_extension(x)
        )
        df["language"] = df["files_extension"].apply(lambda x: features.get_language(x))

        df["files"] = df["files"].apply(lambda x: features.add_metadata(x))

    df.to_csv(
        f"{folder}/vulnerabilities_v2.0.csv",
        quoting=csv.QUOTE_NONNUMERIC,
        escapechar="\\",
        doublequote=False,
        index=False,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="dataset manipulation and reproduction CLI"
    )
    parser.add_argument(
        "--task",
        dest="format",
        choices=["process", "merge", "metadata", "filter", "collection"],
    )
    parser.add_argument(
        "--folder", type=str, metavar="output folder", help="base folder"
    )
    parser.add_argument("--fin", type=str, metavar="input file", help="base file")
    parser.add_argument("--feature", dest="feature", choices=["extension", "language"])

    args = parser.parse_args()

    if args.format == "process":
        if args.folder:
            process_sources(args.folder)
    elif args.format == "merge":
        if args.folder:
            merge_sources(args.folder)
    elif args.format == "metadata":
        if args.folder and args.fin:
            get_metadata(args.fin, args.folder)
    elif args.format == "filter":
        if args.folder and args.fin:
            filter_data(args.fin, args.folder)
    elif args.format == "collection":
        if args.folder and args.fin and args.feature in ("extension", "language"):
            collect_feature(args.fin, args.folder, args.feature)
    else:
        print("Something is wrong. Verify your parameters")
