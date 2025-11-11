import os

from local_config import local_options
from pyadvtools import delete_python_cache

from pyeasyphd.scripts import run_replace_to_standard_cite_keys

if __name__ == "__main__":
    path_output = local_options["path_output"]
    path_conf_j_jsons = local_options["path_conf_j_jsons"]

    options = {}

    full_tex = "/path/to/full.tex"
    full_bib = "/path/to/full.bib"
    run_replace_to_standard_cite_keys(full_tex, full_bib, path_output, path_conf_j_jsons, options)

    # delete caches
    delete_python_cache(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
