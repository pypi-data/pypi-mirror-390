import os

from local_config import local_options
from pyadvtools import delete_python_cache

from pyeasyphd.scripts import run_compare_bib_with_local

if __name__ == "__main__":
    path_output = local_options["path_output"]
    path_spidered_bibs = local_options["path_spidered_bibs"]
    path_spidering_bibs = local_options["path_spidering_bibs"]
    path_conf_j_jsons = local_options["path_conf_j_jsons"]

    options = {
        "include_publisher_list": [],
        "include_abbr_list": [],
        "exclude_publisher_list": ["arXiv"],
        "exclude_abbr_list": [],
        "compare_each_entry_with_all_local_bibs": False,
    }
    need_compare_bib = "/path/to/need_compare.bib"

    run_compare_bib_with_local(
        options, need_compare_bib, path_output, path_spidered_bibs, path_spidering_bibs, path_conf_j_jsons
    )

    # delete caches
    delete_python_cache(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
