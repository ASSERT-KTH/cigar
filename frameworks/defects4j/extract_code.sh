#!/usr/bin/expect -f

project_id=$1
bug_id=$2
version_id=${2}b
work_dir=$3
d4j_path=$4

cd $work_dir

IFS='%' # preserve white spaces in code

git_diff_code=$(git show)

code_middle_line_count=$(echo "$git_diff_code" | grep -n "@@" | head -n 2 | tail -n 1 | cut -d: -f2-) # take the second line that starts with @@
code_middle_line_count=$(echo "$code_middle_line_count" | cut -d- -f2-) # remove everything before the - sign in code_middle_line_count
code_middle_line_count=$(echo "$code_middle_line_count" | cut -d, -f1)

file_path=$(echo "$git_diff_code" | grep -n "diff" | head -n 2 | tail -n 1 | cut -d: -f2-) # take second line in code that starts with diff
file_path=$(echo "$file_path" | rev | cut -d/ -f1 | rev) # remove everything before the last / symbol in file_path
file_path=$(find $work_dir | grep "$file_path" | head -n 1) # take the first results of the grep search on file_path in work_dir

# Find code_start_line_count
for ((i=code_middle_line_count;i>=0;i--)); do # for loop that goes from code_middle_line_count down to 0
    line=$(sed -n "${i}p" $file_path) # take the line i in file_path
    if [[ $line == *"private"* ]] || [[ $line == *"protected"* ]] || [[ $line == *"public"* ]] || [[ $line == *"static"* ]] || [[ $line == *"void"* ]] || ([[ $line == *"JSType"* ]] && [[ $line == *"{"* ]]); then
        code_start_line_count=$i # set code_middle_line_count to i
        break # break the loop
    fi
done

# Construct end_symbol
start_line=$(sed -n "${code_start_line_count}p" $file_path) # read line code_start_line_count in file_path
for ((i=0;i<${#start_line};i++)); do # get the index of the first non-whie space character in start_line
    if [[ ${start_line:$i:1} != " " ]]; then
        start_line_index=$i
        break
    fi
done
end_symbol=$(echo "${start_line:0:$start_line_index}}") # take the substring of start_line from 0 to start_line_index and append }

# Find code_end_line_count
for ((i=code_middle_line_count;i<=1000;i++)); do # for loop that goes from code_middle_line_count up to the end of the file
    line=$(sed -n "${i}p" $file_path) # take the line i in file_path
    if [[ $line == "${end_symbol}"* ]]; then # if line contains end_symbol
        code_end_line_count=$i # set code_end_line_count to i
        break # break the loop
    fi
done

# Read code
code=$(sed -n "${code_start_line_count},${code_end_line_count}p" $file_path) # read file_path from code_start_line_count to code_end_line_count

echo $code