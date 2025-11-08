import os
from pathlib import Path

import pandas as pd

if __name__ == "__main__":
    outputPipelineDir = Path(os.environ["OUTPUT_PIPELINE_DIR"])
    inputPipelineDir = Path(os.environ["INPUT_PIPELINE_DIR"])
    DATA_YEAR = os.environ["DATA_YEAR"]

    final_folder = inputPipelineDir / "QC_output_files"
    final_folder_out = outputPipelineDir / "QC_output_files"
    final_folder_out.mkdir(exist_ok=True)

    state_files = os.listdir(final_folder)
    state_files = [
        s
        for s in state_files
        if s.startswith("missing")
        and s.endswith(".xlsx")
        and (not s.endswith("_merged.xlsx"))
    ]

    with pd.ExcelWriter(  # type: ignore[abstract]
        final_folder_out / f"missing_variables_allstates_merged_{DATA_YEAR}.xlsx"
    ) as writer:
        for sheet in [
            f"Offense {DATA_YEAR}",
            f"Admin {DATA_YEAR}",
            f"Property {DATA_YEAR}",
            f"Victim {DATA_YEAR}",
            f"Offender {DATA_YEAR}",
            f"Arrestee {DATA_YEAR}",
        ]:
            df_list = []
            for file in state_files:
                df = pd.read_excel(
                    final_folder / file,
                    header=[0, 1],
                    index_col=[0, 1],
                    sheet_name=sheet,
                ).dropna(how="all")
                df["State"] = file.split("_")[-2]
                df_list.append(df)
            df_merge = pd.concat(df_list)
            df_merge.to_excel(writer, sheet_name=sheet)
