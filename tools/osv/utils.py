import json
import os

import pandas as pd


def load_json_file(ecosystem, file):
    """Load JSON file that stores vulnerability data.

    Args:
        ecosystem (string): name of the ecosystem
        file (file): vulnerability report file name

    Returns:
        data: json data
    """
    file_path = f"{ecosystem}/{file}"
    with open(file_path) as jfile:
        return json.load(jfile)


def get_vulns_reports(ecosystem):
    """Search vulnerability reports per ecosystem.

    Args:
        ecosystem (string): folder that stores the reports

    Returns:
        list: list of reports
    """
    return [
        f for f in os.listdir(ecosystem) if os.path.isfile(os.path.join(ecosystem, f))
    ]


def load_OSV_dataset(path):
    """Loads OSV dataset if exists into a dataframe.
    If dataset does not exist, it returns None.

    Args:
        path (string): path to the osv dataset

    Returns:
        dataframe: returns dataframe if dataframe does not exist, else None
        bool: return True if processing the first bulk of data, else False
    """
    if os.path.exists(path):
        return pd.read_csv(path, escapechar="\\"), False
    else:
        return None, True


def create_df(data):
    """Create dataframe from vuln data.

    Args:
        data (dict): dictionary with vulnerability data

    Returns:
        dataframe: dataframe with vulnerability data
    """
    return pd.DataFrame(data, index=[0])
