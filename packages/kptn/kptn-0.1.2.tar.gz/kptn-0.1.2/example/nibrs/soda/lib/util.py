from os import path

soda_dir = path.dirname(path.dirname(path.realpath(__file__)))
output_dir = path.join(soda_dir, "output")


def parse_out_schema_name(filepath: str) -> str:
    """Parse out the schema name from a filepath.

    "checks/ucr_prd/ref_agency.yml" -> "ucr_prd"
    """
    parts = filepath.split("/")
    if "." in parts[1]:
        return None
    if len(parts) < 3 or parts[0] != "checks":
        return None
    return parts[1]
