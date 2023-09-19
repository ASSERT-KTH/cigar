export num_of_parallel_jobs=8
export apr="Capr"
export framework="defects4j"
export output_dir="output/${framework}_${apr}"
export summary_file="${output_dir}/exact_match.csv"

declare -a pool=("Chart" "Closure" "Lang" "Math" "Mockito" "Time")
declare -a Chart=(1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26)
declare -a Closure=(1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 64 65 66 67 68 69 70 71 72 73 74 75 76 77 78 79 80 81 82 83 84 85 86 87 88 89 90 91 92 94 95 96 97 98 99 100 101 102 103 104 105 106 107 108 109 110 111 112 113 114 115 116 117 118 119 120 121 122 123 124 125 126 127 128 129 130 131 132 133 134 135 136 137 138 139 140 141 142 143 144 145 146 147 148 149 150 151 152 153 154 155 156 157 158 159 160 161 162 163 164 165 166 167 168 169 170 171 172 173 174 175 176)
declare -a Lang=(1 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65)
declare -a Math=(1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65 66 67 68 69 70 71 72 73 74 75 76 77 78 79 80 81 82 83 84 85 86 87 88 89 90 91 92 93 94 95 96 97 98 99 100 101 102 103 104 105 106)
declare -a Mockito=(1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38)
declare -a Time=(1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 22 23 24 25 26 27)

# Go to root dir
cd ..

# Prepare run params
n=0
declare -a params_bug_ids
declare -a params_projects
for group in "${pool[@]}"; do
    lst="$group[@]"
    for element in "${!lst}"; do
        params_i[$n]=$n
        params_projects[$n]=$group
        params_bug_ids[$n]=$element
        n=$((n+1))
    done
done

# Remove existing parallel folder and files
rm -rf parallel_results
rm -rf parallel.log

# Reset output files

rm ${summary_file}
echo "project,bug,file_name" >> ${summary_file}

# Check diff between ground truth and plausible patch files
count_exact_match() {
    project=$1
    bug=$2

    OUTPUT_FOLDER="$(pwd)/${output_dir}/"
    PLAUSIBLE_PATCH_FOLDER="${OUTPUT_FOLDER}/plausible_patches"
    EXACT_MATCH_FOLDER="${OUTPUT_FOLDER}/exact_match_patches"
    D4JSH="$(pwd)/frameworks/defects4j.sh"
    D4J_PATH=$(grep D4J_PATH user_params.py | grep -o '".*"' | sed 's/"//g')
    JAVA_HOME=$(grep JAVA_HOME user_params.py | grep -o '".*"' | sed 's/"//g')
    TMP_DIR=$(grep TMP_DIR user_params.py | grep -o '".*"' | sed 's/"//g')/${project}_${bug}
    COMPARISON_FOLDER=/tmp/comparison/${project}_${bug}
    GUMTREE_DIFF_PATH="$(pwd)/gumtree-spoon-ast-diff.jar"

    # Check if plausible_patch_folder contains any file that name contains "${project}_${bug}"
    if [ -z "$(ls -A $PLAUSIBLE_PATCH_FOLDER | grep "${project}_${bug}_")" ]; then
        echo "No plausible patch file for ${project}_${bug}"
        return 0
    fi
    echo "Checking exact patches for ${project}_${bug}"

    sh $D4JSH checkout_bug $project $bug ${TMP_DIR} $JAVA_HOME $D4J_PATH
    sh $D4JSH compile_and_run_tests $project $bug ${TMP_DIR} $JAVA_HOME $D4J_PATH

    code_file_path=$(sh $D4JSH get_source_code_file_path $project $bug ${TMP_DIR} $JAVA_HOME $D4J_PATH)
    mkdir -p $COMPARISON_FOLDER
    echo "Copying code file to comparison folder from $code_file_path to $COMPARISON_FOLDER/buggy.java"
    cp $code_file_path $COMPARISON_FOLDER/buggy.java

    cd ${TMP_DIR}
    git checkout D4J_${project}_${bug}_FIXED_VERSION
    echo "Copying code file to comparison folder from $code_file_path to $COMPARISON_FOLDER/fixed.java"
    cp $code_file_path $COMPARISON_FOLDER/fixed.java

    # for all plausible patch file for the current bug:
    for plausible_patch_file in $(ls $PLAUSIBLE_PATCH_FOLDER | grep "${project}_${bug}_"); do
        echo "Checking plausible patch file: $plausible_patch_file"
        cd ${TMP_DIR}
        git checkout D4J_${project}_${bug}_BUGGY_VERSION
        git restore ${code_file_path}

        cp ${PLAUSIBLE_PATCH_FOLDER}/${plausible_patch_file} ${TMP_DIR}
        echo "" >> ${TMP_DIR}/${plausible_patch_file}
        git apply --ignore-space-change --ignore-whitespace $plausible_patch_file
        rm ${TMP_DIR}/${plausible_patch_file}

        patch_file=$(echo $plausible_patch_file | cut -d'.' -f1).java
        cp $code_file_path $COMPARISON_FOLDER/${patch_file}
        
        cd $COMPARISON_FOLDER
        comparison_result=$($(brew --prefix openjdk)/bin/java -jar $GUMTREE_DIFF_PATH fixed.java ${patch_file})
        echo $comparison_result
        if [ "$(echo $comparison_result | tail -n 1)" == "no AST change" ]; then
            echo "Exact match found for $plausible_patch_file"
            cp ${PLAUSIBLE_PATCH_FOLDER}/${plausible_patch_file} $EXACT_MATCH_FOLDER
            echo "${project},${bug},${plausible_patch_file}" >> $OUTPUT_FOLDER/exact_match.csv
            break
        fi
    done
}
export -f count_exact_match
# Run each bug in parallel
parallel --jobs $num_of_parallel_jobs --bar --joblog parallel.log --results parallel_results/ --resume --resume-failed count_exact_match {1} {2} ::: "${params_projects[@]}" :::+ "${params_bug_ids[@]}"

# Sort summary file
summary_file="$(pwd)/${summary_file}"
tail -n +1 "${summary_file}" | sort -t, -k2,2n > "${summary_file}.tmp"
head -n 1 "${summary_file}" > "${summary_file}"
cat "${summary_file}.tmp" >> "${summary_file}"
rm "${summary_file}.tmp"