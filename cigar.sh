#!/bin/bash

export num_of_parallel_jobs=8
export apr="CigaR"
export framework="defects4j"
export output_dir="output/${framework}_${apr}"

## Creating required directories
mkdir -p $output_dir
mkdir -p $output_dir/plausible_patches

n=0
declare -a params_bug_ids=("$2")
declare -a params_projects=($1)

# Remove existing parallel folder and files
rm -rf parallel_results
rm -rf parallel.log


# For each project, keep only the first line of the csv file
for project in "${pool[@]}"; do
    head -n 1 "${output_dir}/${project}_summary.csv" > "${output_dir}/${project}_summary.csv.tmp"
    mv "${output_dir}/${project}_summary.csv.tmp" "${output_dir}/${project}_summary.csv"
done


# Function to run a single project, in case of crash, restart
run_project_bug() {
    project=$1
    bug=$2
    # make apr all lower case
    apr=$(echo "$apr" | tr '[:upper:]' '[:lower:]')
    until $(pwd)/venv/bin/python3 "$(pwd)/main.py" -apr $apr -fr $framework -p $project -bs $bug; do 
        echo "CAPR crashed with exit code $?. Restaring in a minute..."
        sleep 60
    done
}
export -f run_project_bug
# Run each bug in parallel
parallel --jobs $num_of_parallel_jobs --bar --joblog parallel.log --results parallel_results/ --resume --resume-failed run_project_bug {1} {2} ::: "${params_projects[@]}" :::+ "${params_bug_ids[@]}"


# For each project order the summary file by bug id, first line is header
for project in "${pool[@]}"; do
    tail -n +1 "${output_dir}/${project}_summary.csv" | sort -t, -k3,3n > "${output_dir}/${project}_summary.csv.tmp"
    head -n 1 "${output_dir}/${project}_summary.csv" > "${output_dir}/${project}_summary.csv"
    cat "${output_dir}/${project}_summary.csv.tmp" >> "${output_dir}/${project}_summary.csv"
    rm "${output_dir}/${project}_summary.csv.tmp"
done
