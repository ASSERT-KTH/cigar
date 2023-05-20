# Conversational Automated Program Repair


## Tasks

- [ ] Reproduce the process and results of [this](https://docs.gitlab.com/ee/user/project/repository/web_editor.html#upload-a-file) paper


## Reproducability

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
