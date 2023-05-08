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

code=$(echo "$code" | sed 's/^\+.*$/ INFILL/g') # replace the line starting with + with the text INFILL
code=$(echo "$code" | sed 's/^-.*$/ INFILL/g') # replace the line starting with - with the text INFILL

count=$(echo "$code" | grep -c INFILL) # count number of lines that start with INFILL

# remove all lines that start with INFILL except the first one
for ((i=2;i<=count;i++)); do 
    line=$(echo "$code" | grep -n INFILL | head -n 1 | cut -d: -f1)
    code=$(echo "$code" | sed "${line}d")
done

code=$(echo "$code" | sed 's/^[ ]//') # remove one white space from each line

echo $code