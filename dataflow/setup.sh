#!/bin/bash

if [ ! -d venv ]; then
  virtualenv --python=/usr/bin/python venv
fi

source venv/bin/activate

pip install -r requirements.txt

# Requires Cython and Numpy, but does not list them as dependencies.
pip install benepar[cpu]

pip install --no-deps pattern

python -m spacy download en_core_web_lg

python -m spacy download en_core_web_sm

python -c "import benepar; benepar.download('benepar_en')"

sed -i -e "s/SENTENCE_MAX_LEN = .*/SENTENCE_MAX_LEN = 10000/g" \
    "$(dirname $(which python))/../lib/python2.7/site-packages/benepar/base_parser.py"

export GOOGLE_APPLICATION_CREDENTIALS="$(readlink -f ./***REMOVED***)"
