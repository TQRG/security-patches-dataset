import re
import sys

import pandas as pd
import numpy as np

import utils

from github import RateLimitExceededException


def join(summary, details):
    return f"{summary if pd.notna(summary) else ''} {details if pd.notna(details) else ''}".rstrip()


def to_set(cell):
    return set([cell]) if pd.notnull(cell) else np.nan


def clean_nan(files):
    return eval(files.replace("nan", "None"))


def split_commits(chain):
    new_chain = set()
    for ref in eval(chain):
        if "http://" in ref:
            protocol = "http://"
        else:
            protocol = "https://"

        count = ref.count(protocol)
        if count > 1:
            if "," in ref:
                new_chain = set.union(
                    new_chain, set([r for r in ref.split(",") if "github.com" in r])
                )
            else:
                new_chain = set.union(
                    new_chain,
                    set(
                        [
                            f"{protocol}{r}"
                            for r in ref.split(protocol)
                            if "github.com" in r
                        ]
                    ),
                )
        else:
            new_chain = set.union(new_chain, set([ref]))
    return new_chain if len(new_chain) > 0 else np.nan


def commit(refs):
    chain = set()
    for ref in refs:
        # FIXME: github links to diffs are not considered
        # for now; looking into a solution for it
        # e.g., https://github.com/WBCE/WBCE_CMS/commit/0da620016aec17ac2d2f3a22c55ab8c2b55e691e#diff-7b380285e285160d0070863099baabe0
        if "#diff" in ref:
            continue
        # e.g., https://github.com/SerenityOS/serenity/commit/c841012f569dba4fa72e9eb8989bb847be4535bc:889e1d3db9fe19197a4d22c9bfb2e67b3937a0c5
        if re.match(r".*github.com.*:.*", ref):
            continue
        # clean files and functions lines
        # e.g., https://github.com/liblime/LibLime-Koha/commit/8ea6f7bc37d05a9ec25b5afbea011cf9de5f1e49#C4/Output.pm
        elif "#" in ref:
            chain.add(ref.split("#")[0])
        # clean commits when the commit key is not available
        # e.g., https://github.com/nats-io/nats-server/commits/master
        elif not re.match(re.compile(r".*[0-9a-f]{6,40}.*"), ref):
            continue
        elif "?w=1" in ref:
            chain.add(ref.replace("?w=1", ""))
        elif "?branch=" in ref:
            chain.add(ref.split("?branch=")[0])
        elif "?diff=split" in ref:
            chain.add(ref.replace("?diff=split", ""))
        elif re.match(r".*(,|/)$", ref):
            if "/" in ref:
                chain.add(ref[0:-1])
            else:
                chain.add(ref.replace(",", ""))
        elif ")" in ref:
            chain.add(ref.replace(")", ""))
        else:
            chain.add(ref)

    return chain if len(chain) > 0 else np.nan


def project_from_chain(refs):
    for ref in refs:
        proj = re.split("/commit/|/commits/", ref)[0]
        if "pull" in proj:
            proj = re.split("/pull/", proj)[0]
    return proj


def date(datetime):
    return datetime.split("T")[0]


def chain(owner, project, fix_commit):
    return set([f"https://github.com/{owner}/{project}/{fix_commit}"])


def project_from_meta(owner, project):
    return f"https://github.com/{owner}/{project}"


def normalize_sha(git, config, chain):
    new_chain = []
    for commit in chain:

        # FIXME: WTF? Find why...
        if "//commit" in commit:
            commit = commit.replace("//commit", "/commit")

        if "pull/" in commit:
            owner, project, _, _, _, sha = commit.split("/")[3::]
        else:
            owner, project, _, sha = commit.split("/")[3:7]

        if len(sha) != 40:
            try:
                repo = git.get_repo("{}/{}".format(owner, project))
            except RateLimitExceededException:
                print("Unexpected error: {}".format(sys.exc_info()))
                git = utils.get_token(config)

            try:
                gcommit = repo.get_commit(sha=sha.strip())
                new_chain.append(
                    f"https://github.com/{owner}/{project}/commit/{gcommit.commit.sha}"
                )
            except RateLimitExceededException:
                print("Unexpected error: {}".format(sys.exc_info()))
                git = utils.get_token(config)
        else:
            new_chain.append(commit)
    return set(new_chain)
