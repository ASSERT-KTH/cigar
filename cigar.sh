#!/bin/bash

export num_of_parallel_jobs=8
export apr="CigaR"
export framework="defects4j"
export output_dir="output/${framework}_${apr}"

## Creating required directories
mkdir -p $output_dir
mkdir -p $output_dir/plausible_patches

$(pwd)/venv/bin/python3 "$(pwd)/main.py" -apr ${apr,,} -fr $framework -p $1 -bs $2
