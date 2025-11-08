from kptn.util.pipeline_config import PipelineConfig


def srs_variance_tables_prb(
    srs_variance_table_list: list[tuple[str, int]],
) -> list:
    """Filter the set of permutations to exclude SRS1araw"""
    # Filter out SRS1araw
    filtered_combinations = [x for x in srs_variance_table_list if x[0] != "103_TableSRS1araw_Variance.Rmd"]
    # 101_TableSRS1a_Variance.Rmd -> SRS1a
    renamed_combinations = [(x[0].split('_')[1].replace('Table', ''), x[1]) for x in filtered_combinations]

    return renamed_combinations