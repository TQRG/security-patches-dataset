import os
import json


def create_output(fout):
    """Create output folders to save
    the NVD dataset.

    Args:
        fout (string): output file name.
    """
    if not os.path.exists(fout):
        os.mkdir(fout)


def get_vulns_reports(folder):
    """List vuln reports collected from NVD.

    Args:
        folder (string): folder name.

    Returns:
        list: list of vuln reports file names.
    """
    return [f for f in os.listdir(folder) if os.path.join(folder, f) and ".json" in f]


def load_json_files(folder, name):
    """Load JSON file.

    Args:
        folder (string): folder name.
        name (string): name of the nvd file.

    Returns:
        json: json data
    """
    with open(f"{folder}{name}") as f:
        return json.load(f)["CVE_Items"]
