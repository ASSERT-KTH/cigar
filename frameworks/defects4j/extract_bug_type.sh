#!/usr/bin/expect -f

project_id=$1
bug_id=$2
version_id=${2}b
work_dir=$3
d4j_path=$4

cd $work_dir

# Bug Types
SINGLE_LINE="SL, SH, SF"
SINGLE_HUNK="SH, SF"
SINGLE_FUNCTION="SF"
OTHER="OT"

IFS='%' # preserve white spaces in code

# Get git details
git_show=$(git show)
git_diff=$(git diff --stat HEAD^)

# Export file_change_count from git_diff
last_line=$(echo "$git_diff" | tail -n 1) # Get the last line of git_diff
file_change_count=$(echo "$last_line" | awk '{print $1}') # Get the first column of the last line

# Export line_change_count from git_diff
second_line=$(echo "$git_diff" | head -n 2 | tail -n 1) # Get the second line of git_diff
second_line=${second_line#*|} # remove everything before the | character
line_change_count=$(echo "$second_line" | awk '{print $1}') # Get the first column of the second line

# Get the code changes
# TODO: The way I get the code below might not be correct, it may skip changes in one file in different locations
code=${git_show##*@@ } # take the code from the last @@ sign until the end of file using
numbered_list_of_changes=$(echo "$code" | grep -n -E '^\+|^-') # get a numbered list of lines that start with + and - 

if [ $file_change_count -gt 2 ]; then
    bug_type=$OTHER # if file_change_count > 2, then it is OT
elif [ $line_change_count -lt 2 ]; then
    bug_type=$SINGLE_LINE # else if line_change_count < 2, then it is SL
elif [ $line_change_count -lt 3 ]; then
    first_line_count=$(echo "$numbered_list_of_changes" | head -n 1 | awk -F: '{print $1}')
    second_line_count=$(echo "$numbered_list_of_changes" | head -n 2 | tail -n 1 | awk -F: '{print $1}')
    diff=$((second_line_count - first_line_count))
    if [ $diff -eq 1 ]; then
        bug_type=$SINGLE_LINE
    else
        # TODO: Check if changes are in the same function -> SF, else OT
        bug_type=$OTHER
    fi
else
    # TODO check if the bug is SH or SF

    bug_type=$OTHER
fi

echo $code
echo ""
echo $bug_type
