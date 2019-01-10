#!/bin/bash

export GOOGLE_APPLICATION_CREDENTIALS="$(readlink -f ./***REMOVED***)"

# export RAW_DATA_DIR='/home/user/nosync/data/gutenberg-corpus/raw'
# export CHUNK_DATA_DIR='/home/user/nosync/data/gutenberg-corpus/chunk'
export RAW_DATA_DIR='./data-raw'
export CHUNK_DATA_DIR='./data'
export OUTPUT_DIR='./sents'

read_char() {
  stty -icanon -echo
  eval "$1=\$(dd bs=1 count=1 2>/dev/null)"
  stty icanon echo
  echo "$char"
}

source venv/bin/activate

echo -n "Preprocess data in $RAW_DATA_DIR into chunks (y/n)? "
read_char char
if [ "$char" = 'y' ]; then
  python -m preprocess \
    --raw "$RAW_DATA_DIR" \
    --chunk "$CHUNK_DATA_DIR"
fi

echo -n "Run pipeline on data in $CHUNK_DATA_DIR (y/n)? "
read_char char
if [ "$char" = 'y' ]; then
  python -m beam_pipeline \
    --input "$CHUNK_DATA_DIR/*.txt" \
    --output "$OUTPUT_DIR/dataset"

  echo
  echo '*********************************************'
  echo "Output written to $(readlink -f $OUTPUT_DIR)/dataset-*"
  echo '*********************************************'
  echo
fi
