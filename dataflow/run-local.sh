#!/bin/bash

export GOOGLE_APPLICATION_CREDENTIALS="$(readlink -f ./***REMOVED***)"

source venv/bin/activate

mkdir -p /tmp/past2present
mkdir -p /tmp/past2present/staging
mkdir -p /tmp/past2present/tmp

python -m beam_pipeline \
  --num_workers 3 \
  --staging_location=/tmp/past2present/staging \
  --temp_location=/tmp/past2present/tmp \
  --setup_file=./setup.py \
  --input './data/*.txt' \
  --output /tmp/past2present/dataset
