#!/bin/bash

# Stop on first error.
set -e

export SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"

cd "$SCRIPT_DIR"

if [ ! -d venv ]; then
  if command -v python2; then
    PYTHON_CMD="$(which python2)"
  elif command -v python; then
    if [ -n "$(python --version | grep 'Python 2')" ]; then
      PYTHON_CMD="$(which python)"
    else
      echo 'this project requies python 2 to be installed and accessible on the PATH'
    fi
  else
    echo 'this project requies python 2 to be installed and accessible on the PATH'
    exit 1
  fi
  if command -v deactivate; then
    deactivate
  fi
  virtualenv --python="$PYTHON_CMD" venv
fi

source venv/bin/activate

pip install -e .

# Requires Cython and Numpy, but does not list them as dependencies.
pip install benepar[cpu]

# Has a lot of unnecessary dependencies like MySQL.
pip install --no-deps pattern

python -m spacy download en_core_web_lg

python -m spacy download en_core_web_sm

python -c "import benepar; benepar.download('benepar_en')"

export GOOGLE_APPLICATION_CREDENTIALS="$(readlink -f ./dataflow-credentials.json)"

if [ ! -f "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
  echo "
*************************************************************
Please download the JSON credentials for a service account on
Google Cloud with permissions for Dataflow and save them to
${GOOGLE_APPLICATION_CREDENTIALS}.
*************************************************************
"
fi
