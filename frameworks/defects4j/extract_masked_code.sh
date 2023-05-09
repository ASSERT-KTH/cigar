#!/usr/bin/expect -f

project_id=$1
bug_id=$2
work_dir=$3
d4j_path=$4

framework_dir=$(exec pwd)
cd $work_dir

IFS='%' # preserve white spaces in code

# Read Code
code=$(bash ${framework_dir}/extract_code.sh $project_id $bug_id $work_dir $d4j_path)

git_diff=$(git show)
git_diff_code=${git_diff##*@@} # take the code from the last @@ sign until the end of file using

# Find line count of git diff
code_change_line_count=$(echo "$git_diff" | grep -n "@@" | head -n 2 | tail -n 1 | cut -d: -f2-) # take the second line that starts with @@
code_change_line_count=$(echo "$code_change_line_count" | cut -d- -f2-) # remove everything before the - sign in code_change_line_count
code_change_line_count=$(echo "$code_change_line_count" | cut -d, -f1)
code_change_line_count=$((code_change_line_count + 3))

# Find source code file patch
file_path=$(echo "$git_diff" | grep -n "diff" | head -n 2 | tail -n 1 | cut -d: -f2-) # take second line in code that starts with diff
file_path=$(echo "$file_path" | rev | cut -d/ -f1 | rev) # remove everything before the last / symbol in file_path
file_path=$(find $work_dir | grep "$file_path" | head -n 1) # take the first results of the grep search on file_path in work_dir

# Find code_start_line_count
for ((i=code_change_line_count;i>=0;i--)); do # for loop that goes from code_change_line_count down to 0
    line=$(sed -n "${i}p" $file_path) # take the line i in file_path
    if [[ $line == *"private"* ]] || [[ $line == *"protected"* ]] || [[ $line == *"public"* ]] || [[ $line == *"static"* ]] || [[ $line == *"void"* ]] || ([[ $line == *"JSType"* ]] && [[ $line == *"{"* ]]); then
        code_start_line_count=$i # set code_start_line_count to i
        break # break the loop
    fi
done

# Remove buggy lines
buggy_lines=$(echo "$git_diff_code" | grep "^+" | sed 's/^+//g') # grep lines that start with + symbol
masked_code=$code
for buggy_line in $buggy_lines # for each buggy_line in buggy_lines remove the buggy_line from code
do
    buggy_line=$(echo "$buggy_line" | sed 's/^+//g') # remove the starting + symbol
    masked_code=$(echo "$masked_code" | sed "/^${buggy_line}$/d") # using sed delete the line that starts with buggy_line
done

# Create masked_code
local_buggy_line_count=$((code_change_line_count - code_start_line_count + 1)) # line after the change
masked_code=$(echo "$masked_code" | sed "${local_buggy_line_count}s/^/INFILL\n&/") 

echo $masked_code