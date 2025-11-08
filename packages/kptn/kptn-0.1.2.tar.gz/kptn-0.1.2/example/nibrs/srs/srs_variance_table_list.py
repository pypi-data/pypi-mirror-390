import json
from pathlib import Path
from itertools import product
import pandas as pd
# from py_src.flows.util.write_mapped_task_list import write_mapped_task_list
from kptn.util.pipeline_config import PipelineConfig


def srs_variance_table_list(
    external_dir: str,
    data_year: str,
    external_config: str,
) -> list:
    """Read in the population file to get the set of permutations."""
    external_dir = Path(external_dir)
    with open(external_config, "r") as ex_path_f:
        path_dict = json.load(ex_path_f)[data_year]
        population_path = path_dict["population_srs"]
        exclude_path = path_dict["exclusion_srs"]

    population_df = pd.read_csv(
        external_dir / population_path, usecols=["PERMUTATION_NUMBER"]
    )
    permutation_list = population_df["PERMUTATION_NUMBER"].astype(int).tolist()

    exclude = pd.read_csv(external_dir / exclude_path, usecols=["PERMUTATION_NUMBER"])
    exclude_list = exclude["PERMUTATION_NUMBER"].astype(int).tolist()

    permutation_list = [x for x in permutation_list if x not in exclude_list]

    # table 1 is crossed with everything while table 2 is only for national
    all_combinations = (
        list(product(["101_TableSRS1a_Variance.Rmd"], permutation_list))
        + [("102_TableSRS2a_Variance.Rmd", 1)]
        + list(product(["103_TableSRS1araw_Variance.Rmd"], permutation_list))
    )

    # write_mapped_task_list(Path(pipeline_config.scratch_dir), all_combinations, "srs_variance_table_list.txt")
    return all_combinations