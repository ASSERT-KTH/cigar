### Install OS specific requirements
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Linux detected"
    sudo apt install subversion
    sudo apt install openjdk-8-jdk -y
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Mac detected"
    brew install svn
    brew install openjdk@8
else
    echo "OS not supported"
    exit 1
fi

### Install python requirements
# Create virtualenv for the repo
pip3 install virtualenv
virtualenv venv
source venv/bin/activate
# Install requirements
pip install -r requirements.txt

### Download tools & dependencies
# To count diff lines download gumtree-spoon-ast-diff.jar from https://github.com/SpoonLabs/gumtree-spoon-ast-diff
wget https://search.maven.org/remote_content\?g\=fr.inria.gforge.spoon.labs\&a\=gumtree-spoon-ast-diff\&v\=LATEST\&c\=jar-with-dependencies -O gumtree-spoon-ast-diff.jar
# Download Defects4J
git clone https://github.com/rjust/defects4j.git

### Set parameters
rm user_params.py
cp user_params.py.template user_params.py
user_params=$(<user_params.py)
# set TMP_DIR to "/tmp/defects4j"
user_params=${user_params//path_to_defects4j/\/tmp\/defects4j}
# set D4J_PATH to "$(pwd)/defects4j/framework/bin"
user_params=${user_params//path_to_d4j_bin/$(pwd)\/defects4j\/framework\/bin}
# set JAVA_HOME to $(/usr/libexec/java_home -version 1.8)
java_home=$(/usr/libexec/java_home -version 1.8)
user_params=${user_params//path_to_java_home/$java_home}

# write to file
echo "$user_params" > user_params.py

# Print that user should set API_KEY
echo "Please set your API_KEY in user_params.py"