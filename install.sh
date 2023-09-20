### Check requirements
if ! type "virtualenv" > /dev/null; then
    echo "virtualenv not installed"
    exit 1
    # To install run: pip3 install virtualenv
fi
if ! type "svn" > /dev/null; then
    echo "subversion (svn) not installed"
    exit 1
    # To install run: 
    # linux: sudo apt install subversion
    # mac: brew install svn
fi
if ! type "java" > /dev/null; then
    echo "java not installed"
    exit 1
    # To install run: 
    # linux: sudo apt install openjdk-8-jdk -y
    # mac: install openjdk@8
fi
# Get java 8 home path
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    java_home=$(readlink -f /usr/bin/java | sed "s:bin/java::")
elif [[ "$OSTYPE" == "darwin"* ]]; then
    java_home=$(/usr/libexec/java_home -version 1.8)
else
    echo "OS not supported"
    exit 1
fi
# Check if java_home is set
if [ -z "$java_home" ]; then
    echo "java_home not set"
    exit 1
fi

### Install python requirements
virtualenv venv
source venv/bin/activate
# Install requirements
pip3 install -r requirements.txt

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
user_params=${user_params//patch_to_tmp_dir/\/tmp\/defects4j}
# set D4J_PATH to "$(pwd)/defects4j/framework/bin"
user_params=${user_params//path_to_d4j_bin/$(pwd)\/defects4j\/framework\/bin}
# set JAVA_HOME to $(/usr/libexec/java_home -version 1.8)
user_params=${user_params//path_to_java_home/$java_home}
# write to file
echo "$user_params" > user_params.py

# Print that user should set API_KEY
echo
echo "Please set your API_KEY in user_params.py"