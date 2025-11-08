import gzip
import os
import shutil
from pathlib import Path


def write_to_out_file(
    in_file_path: Path, out_file_path: Path, file_name: str, file_list: list
) -> None:
    with gzip.open(out_file_path / file_name, "wt") as out_file:
        print("Printing to", out_file_path)
        first_file = file_list[0]
        print(first_file)
        with open(Path(in_file_path) / first_file, "r") as read_first:
            for line in read_first:
                out_file.write(line)
        for f in range(1, len(file_list)):
            file = file_list[f]
            print(file)
            with open(Path(in_file_path) / file, "r") as read_next:
                header = read_next.readline()  # skip first line
                print(header)
                for line in read_next:
                    out_file.write(line)


if __name__ == "__main__":
    outputPipelineDir = Path(os.environ["OUTPUT_PIPELINE_DIR"])
    inputPipelineDir = Path(os.environ["INPUT_PIPELINE_DIR"])

    final_folder = inputPipelineDir / "srs" / "final-estimates"
    final_folder_out = outputPipelineDir / "srs" / "final-estimates"
    final_folder_out.mkdir(exist_ok=True)

    for file in [
        "Indicator_Tables",
        "Indicator_Tables_flag_non_zero_estimates_with_no_prb",
        "Indicator_Tables_no_supp",
    ]:
        print(file)
        all_files = os.listdir(final_folder / file)
        # get the files that actually exist (some permutations might not)
        files_to_merge = [f for f in all_files if f.endswith(".csv")]
        write_to_out_file(
            in_file_path=final_folder / file,
            out_file_path=final_folder_out,
            file_name=f"{file}_Merged.csv.gz",
            file_list=files_to_merge,
        )
        shutil.make_archive(str(final_folder_out / file), "zip", final_folder_out, file)
