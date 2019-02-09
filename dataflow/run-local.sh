#!/bin/bash

SCRIPT_DIR="$(dirname "$(readlink -f "0")")"

# RAW_DATA_DIR="$HOME/nosync/data/gutenberg-corpus/raw"
# CHUNK_DATA_DIR="$HOME/nosync/data/gutenberg-corpus/chunk"
RAW_DATA_DIR="$SCRIPT_DIR/raw"
CHUNK_DATA_DIR="$SCRIPT_DIR/chunks"
OUTPUT_DIR="$SCRIPT_DIR/output"

read_char() {
  stty -icanon -echo
  eval "$1=\$(dd bs=1 count=1 2>/dev/null)"
  stty icanon echo
  echo "$char"
}

source "$SCRIPT_DIR/venv/bin/activate"

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
  echo '******************************************************'
  echo "Output written to $(readlink -f $OUTPUT_DIR)/dataset-*"
  echo '******************************************************'
  echo
fi
