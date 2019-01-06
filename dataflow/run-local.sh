#!/bin/bash

export GOOGLE_APPLICATION_CREDENTIALS="$(readlink -f ./***REMOVED***)"

# export RAW_DATA_DIR='/home/user/nosync/data/gutenberg-corpus/raw'
# export CHUNK_DATA_DIR='/home/user/nosync/data/gutenberg-corpus/chunk'
export RAW_DATA_DIR='./data-raw'
export CHUNK_DATA_DIR='./data'

read_char() {
  stty -icanon -echo
  eval "$1=\$(dd bs=1 count=1 2>/dev/null)"
  stty icanon echo
  echo "$char"
}

source venv/bin/activate

mkdir -p /tmp/past2present
mkdir -p /tmp/past2present/staging
mkdir -p /tmp/past2present/tmp

echo -n "Preprocess data in $RAW_DATA_DIR into chunks (y/n)? "
read_char char
if [ "$char" = 'y' ]; then
  python -m preprocess \
    --raw "$RAW_DATA_DIR" \
    --chunk "$CHUNK_DATA_DIR"
fi

python -m beam_pipeline \
  --num_workers 3 \
  --staging_location=/tmp/past2present/staging \
  --temp_location=/tmp/past2present/tmp \
  --setup_file=./setup.py \
  --input "$CHUNK_DATA_DIR/*.txt" \
  --output /tmp/past2present/dataset

echo
echo '*********************************************'
echo 'Output written to /tmp/past2present/dataset-*'
echo '*********************************************'
echo
