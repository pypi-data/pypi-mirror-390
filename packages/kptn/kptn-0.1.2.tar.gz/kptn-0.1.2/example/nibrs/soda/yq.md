
# yq

[yq](https://github.com/mikefarah/yq) is like `jq` but for YAML: a CLI tool for editing files. It's helpful if you want to apply updates on many of the files in the `checks/` directory.

## Usage

Before using `yq`, it's strongly recommended to read the docs and try out some examples on test files.

### Example: Deleting a check

In the statement below, `.["checks for *"][]` matches all list items (all checks), filters on the one we want, and wraps the entire statement with a `del()` to delete. 

```bash
yq -i 'del(.["checks for *"][] | select(.["invalid_count(data_year) = 0"] ))' checks/ref_agency_yearly.yml
```

To apply the operation on all files, use the `bin/yq-all.sh` script.
