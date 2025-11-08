
project_root="$( dirname "${BASH_SOURCE[0]}" )/../.."
cd $project_root/soda

KEY="invalid_count(data_year) = 0"

for file in checks/*
do
  echo "Editing $file"
  yq -i 'del(.["checks for *"][] | select(.[strenv(KEY)] ))' $file
done
