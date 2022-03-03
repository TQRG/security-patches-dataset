import argparse
import csv

import pandas as pd
import numpy as np
from tqdm import tqdm

import utils


def nvd_extractor(folder, fout):
    """Extracts raw data from NVD .json files."""

    def get_cwes(data):
        cwes = set()
        for data in cve["cve"]["problemtype"]["problemtype_data"]:
            for cwe in data["description"]:
                cwes.add(cwe["value"])
        return str(cwes) if len(cwes) > 0 else np.nan

    def get_cve(data):
        return data["cve"]["CVE_data_meta"]["ID"]

    def get_description(data):
        return data["cve"]["description"]["description_data"][0]["value"]

    def get_published_date(data):
        return data["publishedDate"]

    def get_last_modified_date(data):
        return data["lastModifiedDate"]

    def get_severity(data):
        if data["impact"]:
            if "baseMetricV2" in data["impact"].keys():
                return data["impact"]["baseMetricV2"]["severity"]
        return np.nan

    def get_exploitability(data):
        if data["impact"]:
            if "baseMetricV2" in data["impact"].keys():
                return cve["impact"]["baseMetricV2"]["exploitabilityScore"]
        return np.nan

    def get_impact(data):
        if data["impact"]:
            if "baseMetricV2" in data["impact"].keys():
                return data["impact"]["baseMetricV2"]["impactScore"]
        return np.nan

    def get_references(data):
        refs = set()
        for ref in data["cve"]["references"]["reference_data"]:
            refs.add(ref["url"])
        return str(refs) if len(refs) > 0 else np.nan

    # create output folder
    utils.create_output(fout)
    reports, first = utils.get_vulns_reports(folder), True

    for fname in reports:

        cves = utils.load_json_files(folder, fname)

        for cve in tqdm(cves):

            cve_data = {
                "cve_id": get_cve(cve),
                "cwes": get_cwes(cve),
                "description": get_description(cve),
                "severity": get_severity(cve),
                "exploitability": get_exploitability(cve),
                "impact": get_impact(cve),
                "published_date": get_published_date(cve),
                "last_modified_date": get_last_modified_date(cve),
                "refs": get_references(cve),
            }

            if first:
                df, first = pd.DataFrame(cve_data, index=[0]), False
            else:
                df = pd.concat(
                    [df, pd.DataFrame(cve_data, index=[0])], ignore_index=True
                )

        print(df)
        df.to_csv(
            f"{fout}raw-nvd-data.csv",
            quoting=csv.QUOTE_NONNUMERIC,
            escapechar="\\",
            doublequote=False,
            index=False,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NVD Database extractor.")
    parser.add_argument("--task", dest="format", choices=["extractor", "osv_generator"])
    parser.add_argument("--data", type=str, metavar="input folder", help="base folder")
    parser.add_argument("--fout", type=str, metavar="output file", help="output file")

    args = parser.parse_args()
    if args.format == "extractor":
        if args.data and args.fout:
            nvd_extractor(args.data, args.fout)
    else:
        print("Something is wrong. Verify your parameters.")
