#!/usr/bin/expect -f

project_id=$1
bug_id=$2
version_id=${2}b
tmp_dir=$3
d4j_path=$4

work_dir=$tmp_dir/$project_id-$bug_id
export PATH=$PATH:$d4j_path

defects4j info -p $project_id -b $bug_id

defects4j checkout -p $project_id -v $version_id -w $work_dir

cd $work_dir

defects4j compile

defects4j test -r

# Collect all bug details that are needed in d4j.py