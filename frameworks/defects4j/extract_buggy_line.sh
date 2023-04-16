#!/usr/bin/expect -f

project_id=$1
bug_id=$2
version_id=${2}b
work_dir=$3
d4j_path=$4

cd $work_dir

IFS='%' # preserve white spaces in code
code=$(git show)
code=${code##*@@} # take the code from the last @@ sign until the end of file using
code=$(echo "$code" | sed '/^[^+]/d') # remove all lines that doesn't start with +
code=$(echo "$code" | sed 's/^[+]//') # replace the + sign with nothing

echo $code