import argparse
import os
import csv

import pandas as pd
import numpy as np

import utils


def get_references(data):
    """Gets references from vulnerability report.

    Args:
        data (dict): vulnerability report.

    Returns:
        set: set of references in report.
    """
    if "references" in data.keys():
        refs = set([ref["url"] for ref in data["references"] if "url" in ref.keys()])
        return str(refs) if len(refs) > 0 else np.nan
    return np.nan


def get_field(data, field):
    """Verifies if field exists in the vulnerability report.

    Args:
        data (dict): vulnerability report.
        field (string): field to verify.

    Returns:
        string: value from field in data.
    """
    if field in data.keys():
        return data[field]
    return np.nan


def process_ghsa_vulns(fout, ecosystem="GHSA"):
    """Processes GHSA vulnerability reports.

    Args:
        fout (string): Path to save the vulnerabilities data.
    """

    def get_cwes(data):
        """Get weakness ids from vulnerability.

        Args:
            data (dict): vulnerability report.

        Returns:
            set: set of weakness ids in report.
        """
        cwes = set()
        for cwe in data["cwes"]["nodes"]:
            cwes.add(cwe["cweId"])
        return str(cwes) if len(cwes) > 0 else np.nan

    def get_aliases(data):
        """Get aliases of vulnerability.

        Args:
            data (dict): vulnerability report.

        Returns:
            set: set of aliases in report.
        """
        aliases = set()
        for id in data["identifiers"]:
            if id["value"] != data["ghsaId"]:
                aliases.add(id["value"])
        return str(aliases) if len(aliases) > 0 else np.nan

    def get_score(data):
        """Get vulnerability score.

        Args:
            data (dict): vulnerability report.

        Returns:
            float: vulnerability score.
        """
        return data["cvss"]["score"]

    # load osv dataset if exists
    df, first = utils.load_OSV_dataset(fout)

    # get reports available for GHSA ecosystem
    files = utils.get_vulns_reports(ecosystem)

    # iterate over the ecosystem vulns
    for file in files:

        # load json file
        data = utils.load_json_file(ecosystem, file)

        vuln_data = {
            "ecosystem": ecosystem,
            "vuln_id": data["ghsaId"],
            "summary": get_field(data, "summary"),
            "details": get_field(data, "description"),
            "aliases": get_aliases(data),
            "modified_date": get_field(data, "updatedAt"),
            "published_date": get_field(data, "publishedAt"),
            "severity": get_field(data, "severity"),
            "score": get_score(data),
            "cwe_id": get_cwes(data),
            "refs": get_references(data),
        }

        if first:
            df, first = utils.create_df(vuln_data), False
        else:
            df = pd.concat([df, utils.create_df(vuln_data)], ignore_index=True)

    print(f"+{len(files)} vulnerabilities from {ecosystem}: len={len(df)}")
    df.to_csv(
        fout,
        quoting=csv.QUOTE_NONNUMERIC,
        escapechar="\\",
        doublequote=False,
        index=False,
    )


def process_ecosystem_vulns(ecosystem, fout):
    """Processes vulnerability reports per ecosystem.

    Args:
        ecosystem (string): ecosystem name.
        fout (string): path to save the vulnerabilities data.
    """

    def get_ranges(data):
        """Get the range of code repository that are
        affected by the vulnerability.

        Args:
            data (dict): vulnerability data.

        Returns:
            ranges: if exists, else return NaN
        """
        if "affected" in data.keys():
            if "ranges" in data["affected"][0].keys():
                return data["affected"][0]["ranges"]     
        return []

    def normalize_ref(repo):
        if ".git" in repo:
            return repo.replace(".git", "")
        else:
            return repo

    def get_commits(data):
        """Get commits that introduce and fix the
        vulnerbility.

        Args:
            data (dict): vulnerability data.

        Returns:
            set: commits that introduce the vulnerability
            set: commits that fix the vulnerability
        """
        introduced, fixed, ranges = set(), set(), get_ranges(data)
                    
        if len(ranges) > 0:
                for range in ranges:
                    if range["type"] == "GIT":
                        for event in range["events"]:
                            if "introduced" in event.keys():
                                if event["introduced"] != "0":
                                    repo = normalize_ref(range["repo"])
                                    introduced.add(f"{repo}/commit/{event['introduced']}")
                            elif "fixed" in event.keys():
                                repo = normalize_ref(range["repo"])
                                fixed.add(f"{repo}/commit/{event['fixed']}")
        return (
            introduced if len(introduced) > 0 else np.nan,
            fixed if len(fixed) > 0 else np.nan,
        )

    def get_severity(data):
        if "database_specific" in data.keys():
            if "severity" in data["database_specific"].keys():
                return data["database_specific"]["severity"]
        if "affected" in data.keys():
            if "ecosystem_specific" in data["affected"][0].keys():
                eco_spec = data["affected"][0]["ecosystem_specific"]
                if "severity" in eco_spec.keys():
                    return eco_spec["severity"]
        return np.nan

    def get_cwes(data):
        cwes = set()
        if "database_specific" in data.keys():
            if "cwe_ids" in data["database_specific"].keys():
                cwe_ids = data["database_specific"]["cwe_ids"]
                if len(cwe_ids) > 0:
                    return str(set(data["database_specific"]["cwe_ids"]))
        if "affected" in data.keys():
            if "database_specific" in data["affected"][0].keys():
                db_spec = data["affected"][0]["database_specific"]
                if "cwes" in db_spec.keys():
                    for cwe in db_spec["cwes"]:
                        cwes.add(cwe["cweId"])
        return cwes if len(cwes) > 0 else np.nan

    def get_score(data):
        if "affected" in data.keys():
            if "database_specific" in data["affected"][0].keys():
                db_spec = data["affected"][0]["database_specific"]
                if "cvss" in db_spec.keys():
                    if db_spec["cvss"] and type(db_spec["cvss"]) != str:
                        if "score" in db_spec["cvss"].keys():
                            return db_spec["cvss"]["score"]
        return np.nan

    def get_aliases(data):
        if 'aliases' in data.keys():
            aliases = data['aliases']
            if len(aliases) > 0:
                return str(set(aliases))
        return np.nan

    # load osv dataset if exists
    df, first = utils.load_OSV_dataset(fout)

    # get reports available for each ecosystem
    files = utils.get_vulns_reports(ecosystem)

    # iterate over the ecosystem vulns
    for file in files:

        # load json file
        data = utils.load_json_file(ecosystem, file)

        refs = get_references(data)
        introduced, fixed = get_commits(data)
        if pd.notna(fixed) and pd.notna(refs):
            refs = set.union(eval(refs), fixed)

        vuln_data = {
            "ecosystem": ecosystem,
            "vuln_id": get_field(data, "id"),
            "aliases": get_aliases(data),
            "summary": get_field(data, "summary"),
            "details": get_field(data, "details"),
            "modified_date": get_field(data, "modified"),
            "published_date": get_field(data, "published"),
            "severity": get_severity(data),
            "score": get_score(data),
            "cwe_id": get_cwes(data),
            "refs": str(refs),
            "introduced": str(introduced),
        }

        if first:
            df, first = utils.create_df(vuln_data), False
        else:
            df = pd.concat([df, utils.create_df(vuln_data)], ignore_index=True)

    print(f"+{len(files)} vulnerabilities from {ecosystem}: len={len(df)}")
    df.to_csv(
        fout,
        quoting=csv.QUOTE_NONNUMERIC,
        escapechar="\\",
        doublequote=False,
        index=False,
    )


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Open Source Vulnerability Database Extractor (https://osv.dev/)"
    )
    parser.add_argument(
        "--ecosystem",
        type=str,
        metavar="ecosystem name",
        help="visit the OSV website to see the ecosystems available",
    )
    parser.add_argument(
        "--fout",
        type=str,
        metavar="output file",
        help="file where data will be appended",
    )

    args = parser.parse_args()
    if args.ecosystem and args.fout:
        if args.ecosystem == "GHSA":
            process_ghsa_vulns(args.fout)
        else:
            process_ecosystem_vulns(args.ecosystem, args.fout)
    else:
        print("Something is wrong.")
