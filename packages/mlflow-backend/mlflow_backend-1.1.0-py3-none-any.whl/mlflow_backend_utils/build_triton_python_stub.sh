
set -ex

GIT_BRANCH_NAME=$1
PYTHON_VERSION=$2
OUTPUT_PATH=$3
CHANNEL=$4
S3_OUTPUT_PATH=$5
EXTRA_CERT_PATH=$6

echo "$EXTRA_CERT_PATH"
if [ -n "$EXTRA_CERT_PATH" ]; then
  cp $EXTRA_CERT_PATH /usr/local/share/ca-certificates/extra-ca.crt
  update-ca-certificates
fi

apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y git rapidjson-dev libarchive-dev zlib1g-dev gcc build-essential

curl -L -O "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
bash Miniforge3-$(uname)-$(uname -m).sh -b -p "${HOME}/conda"
set +x
source "${HOME}/conda/etc/profile.d/conda.sh"
set -x


# install architecture appropriate awscli if S3_OUTPUT_PATH is provided
if [ -n "$S3_OUTPUT_PATH" ]; then
  curl "https://awscli.amazonaws.com/awscli-exe-linux-$(uname -m).zip" -o "awscliv2.zip"
  unzip awscliv2.zip
  ./aws/install
fi

git clone https://github.com/triton-inference-server/python_backend -b $GIT_BRANCH_NAME
cd python_backend
mkdir build && cd build

conda create -n py${PYTHON_VERSION} python=${PYTHON_VERSION} -c ${CHANNEL} -y -q
conda activate py${PYTHON_VERSION}
pip install cmake
cmake -DTRITON_ENABLE_GPU=ON -DTRITON_BACKEND_REPO_TAG=$GIT_BRANCH_NAME -DTRITON_COMMON_REPO_TAG=$GIT_BRANCH_NAME -DTRITON_CORE_REPO_TAG=$GIT_BRANCH_NAME -DCMAKE_POLICY_VERSION_MINIMUM=3.5 -DCMAKE_INSTALL_PREFIX:PATH=`pwd`/install ..
make triton-python-backend-stub

cp triton_python_backend_stub $OUTPUT_PATH
chmod 666 $OUTPUT_PATH

if [ -n "$S3_OUTPUT_PATH" ]; then
  aws s3 cp $OUTPUT_PATH $S3_OUTPUT_PATH
fi
