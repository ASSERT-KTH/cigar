#!/usr/bin/expect -f

project_id=$1
bug_id=$2
version_id=${2}b
work_dir=$3
d4j_path=$4

cd $work_dir

# Get git_diff
git_diff=$(git diff --stat HEAD^)

# Export file_change_count from git_diff
last_line=$(echo "$git_diff" | tail -n 1) # Get the last line of git_diff
file_change_count=$(echo "$last_line" | awk '{print $1}') # Get the first column of the last line
# remove new line at the end of _file_change_count


# Export line_change_count from git_diff
second_line=$(echo "$git_diff" | head -n 2 | tail -n 1) # Get the second line of git_diff
second_line=${second_line#*|} # remove everything before the | character
line_change_count=$(echo "$second_line" | awk '{print $1}') # Get the first column of the second line

echo "${file_change_count}|${line_change_count}"