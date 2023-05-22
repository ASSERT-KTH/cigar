# Conversational Automated Program Repair


## Tasks

- [ ] Reproduce the process and results of [this](https://docs.gitlab.com/ee/user/project/repository/web_editor.html#upload-a-file) paper


## Reproducability

### Setup Pre-requisites

Make sure defects4j is setup on your computer properly and you can checkout any active bug in Chart, Closure, Lang, Math, Mockito and Time projects.

- For Chart bugs you may need to install svn
```
sudo apt-get install subversion
```

- For Mockito bugs you may need to export JAVA_HOME before running the python script, you can find your java path with the following command

```
# Find your java path
/usr/libexec/java_home -V

# Export it & run the script
export JAVA_HOME="/Library/Java/JavaVirtualMachines/zulu-8.jdk/Contents/Home"
$(pwd)/venv/bin/python3 "$(pwd)/main.py"
```

### Setup CAPR

Steps to reproduce the results:

- Clone the repo, cd into folder
```
git clone git@github.com:ASSERT-KTH/capr.git
cd capr
```

- Create a virtualenv for the repo, activate it
```
virtualenv venv
source venv/bin/activate
```

- Install the requiremets
```
pip install -r requirements.txt
```

- Duplicate the `user_params.py.template` file in root folder, name the duplicate file `user_params.py`

- Set the `TMP_DIR` (path to checkout the bugs to), `D4J_PATH` (path that points to your defects4j/framework/bin) and `API_KEY` (your openai api key) in the `user_params.py` file

- Now you can run capr.py with the following command
```
$(pwd)/venv/bin/python3 "$(pwd)/main.py"
```

## Tests

To test your `TMP_DIR` and `D4J_PATH` settings, you can run the following command from the root folder.

```
TMP_DIR=$(grep TMP_DIR user_params.py | grep -o '".*"' | sed 's/"//g')
D4J_PATH=$(grep D4J_PATH user_params.py | grep -o '".*"' | sed 's/"//g')

bug_id=1
project="Time"
command="checkout_bug"
work_dir="$TMP_DIR/$project-$bug_id/"
d4j_path="$D4J_PATH"

cd frameworks
bash defects4j.sh "$command" "$project" "$bug_id" "$work_dir" "$d4j_path"
cd -
```
After running the command above you should see the following console output:
```
Check out program version: Time-1b......................................... OK
```
And you should find the bug in the `$TMP_DIR` folder, that you've set.

## Continuous Running

As explained [here](https://stackoverflow.com/questions/696839/how-do-i-write-a-bash-script-to-restart-a-process-if-it-dies) you can start the script in a loop, so that it restarts if it crashes. (Which happens often with the openai api)

```
function run_capr {
    $(pwd)/venv/bin/python3 "$(pwd)/main.py"
}

until run_capr; do
    echo "CAPR crashed with exit code $?. Restaring in a second..."
    sleep 1
done
```
