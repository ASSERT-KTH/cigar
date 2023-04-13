#!/usr/bin/expect -f

project_id=$1
bug_id=$2
version_id=${2}b
work_dir=$3
d4j_path=$4

export PATH=$PATH:$d4j_path

cd $work_dir

IFS='%' # preserve white spaces in code
code=$(git show)
code=${code##*@@} # take the code from the last @@ sign until the end of file using
code=$(echo "$code" | sed '/^-/d') # remove line that starts with -
code=$(echo "$code" | sed 's/^+/ /') # replace + with white space at the beginning of each line
code=$(echo "$code" | sed 's/^[ ]//') # remove one white space from each line

echo $code