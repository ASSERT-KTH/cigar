#!/usr/bin/expect -f
set -e

project_id=$1
bug_id=$2
version_id=${2}b
work_dir=$3
d4j_path=$4
patch=$5

IFS='%' # preserve white spaces in code
export PATH=$PATH:$d4j_path

cd $work_dir

# Restore original git state
git restore .

# Export buggy line
buggy_line=$(git show)
buggy_line=${buggy_line##*@@} # take the code from the last @@ sign until the end of file using
buggy_line=$(echo "$buggy_line" | sed '/^[^+]/d') # remove all lines that doesn't start with +
buggy_line=$(echo "$buggy_line" | sed 's/^[+]//') # replace the + sign with nothing

# Extract buggy code path
code_file_path=$(git show | grep "+++" | sed '2!d')
code_file_path=${code_file_path#*+++} # trim code_file_path to remove everything before +++
code_file_path=${code_file_path#*/} # remove everything before the first / in code_file_path
code_file_path=$work_dir/$code_file_path

# Get the line number of the buggy line
line_number=$(grep -n "$buggy_line" $code_file_path | cut -d: -f1)

# Remove line at line_number (buggy line)
cp $code_file_path ${code_file_path}.tmp &&
sed "${line_number}d" <${code_file_path}.tmp >$code_file_path &&
rm -f ${code_file_path}.tmp
# Remove patch at line_number
cp $code_file_path ${code_file_path}.tmp
awk -v line_number="$line_number" -v patch="$patch" 'NR==line_number{print patch}1' ${code_file_path}.tmp > $code_file_path
rm -f ${code_file_path}.tmp

defects4j compile

defects4j test -r
