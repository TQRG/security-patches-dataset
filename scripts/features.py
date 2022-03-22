import numpy as np
import pandas as pd

ext_map = {
    "Objective-C": {"m", "mm"},
    "Java": {"java", "jsp", "jspf"},
    "Scala": {"scala"},
    "C/C++": {
        "c",
        "cc",
        "cxx",
        "cpp",
        "hpp",
        "c++",
        "h",
        "hh",
        "cppm",
        "ixx",
        "cp",
        "inl",
    },
    "Groovy": {"groovy"},
    "PHP": {"php", "tpl", "inc", "ctp", "phpt", "phtml"},
    "JavaScript": {"js", "jsx", "coffee"},
    "Python": {"py"},
    "Config files": {"lock", "gradle", "json", "config", "yaml", "conf"},
    "Ruby": {"rb"},
    "HTML": {"html", "erb"},
    "Perl": {"pm"},
    "Go": {"go"},
    "Lua": {"lua"},
    "Erlang": {"erl"},
    "C#": {"cs"},
    "Rust": {"rust"},
    "Vala": {"vala"},
    "SQL": {"sql"},
    "XML": {"xml"},
    "Shell": {"sh"},
}


def get_extension(file):
    return file.split(".")[-1].lower()


def get_files_extension(files):
    extensions = set(
        [get_extension(file) for file in eval(files).keys() if len(file.split(".")) > 1]
    )
    return extensions if len(extensions) > 0 else np.nan


def get_key(val):
    for key, value in ext_map.items():
        if val in value:
            return key


def get_language(extensions):
    if not pd.notna(extensions):
        return np.nan
    languages = set([get_key(ext) for ext in extensions if get_key(ext) != None])
    return languages if len(languages) > 0 else np.nan


def add(files):
    files = eval(files)
    for file in files.keys():
        extension = get_extension(file)
        files[file]["extensions"] = extension
        files[file]["language"] = get_key(extension)
    return files
