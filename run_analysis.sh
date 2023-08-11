export num_of_parallel_jobs=8
export apr="rapidcapr"
export framework="defects4j"

declare -a pool=("Math")
declare -a Chart=(1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26)
declare -a Closure=(1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 64 65 66 67 68 69 70 71 72 73 74 75 76 77 78 79 80 81 82 83 84 85 86 87 88 89 90 91 92 94 95 96 97 98 99 100 101 102 103 104 105 106 107 108 109 110 111 112 113 114 115 116 117 118 119 120 121 122 123 124 125 126 127 128 129 130 131 132 133 134 135 136 137 138 139 140 141 142 143 144 145 146 147 148 149 150 151 152 153 154 155 156 157 158 159 160 161 162 163 164 165 166 167 168 169 170 171 172 173 174 175 176)
declare -a Lang=(1 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65)
declare -a Math=(1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65 66 67 68 69 70 71 72 73 74 75 76 77 78 79 80 81 82 83 84 85 86 87 88 89 90 91 92 93 94 95 96 97 98 99 100 101 102 103 104 105 106)
declare -a Mockito=(1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38)
declare -a Time=(1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 22 23 24 25 26 27)


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


# For each project, keep only the first line of the csv file
for project in "${pool[@]}"; do
    head -n 1 "results/${project}_summary.csv" > "results/${project}_summary.csv.tmp"
    mv "results/${project}_summary.csv.tmp" "results/${project}_summary.csv"
done


# Function to run a single project, in case of crash, restart
run_project_bug() {
    project=$1
    bug=$2
    until $(pwd)/venv/bin/python3 "$(pwd)/main.py" -apr $apr -fr $framework -p $project -bs $bug; do 
        echo "CAPR crashed with exit code $?. Restaring in a minute..."
        sleep 60
    done
}
export -f run_project_bug
# Run each bug in parallel
parallel --jobs $num_of_parallel_jobs --bar --joblog parallel.log --results parallel_results/ --resume --resume-failed run_project_bug {1} {2} ::: "${params_projects[@]}" :::+ "${params_bug_ids[@]}"


# For each project order the summary file by bug id
for project in "${pool[@]}"; do
    sort -t, -k2,2n "results/${project}_summary.csv" > "results/${project}_summary.csv.tmp"
    mv "results/${project}_summary.csv.tmp" "results/${project}_summary.csv"
done

# Merge all summary files into one, first line is the header
head -n 1 "results/${pool[0]}_summary.csv" > "results/summary.csv"
for project in "${pool[@]}"; do
    tail -n +2 "results/${project}_summary.csv" >> "results/summary.csv"
done