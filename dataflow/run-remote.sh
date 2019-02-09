#!/bin/bash

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"

RAW_DATA_DIR="$SCRIPT_DIR/raw"
CHUNK_DATA_DIR="$SCRIPT_DIR/chunks"

read_char() {
  stty -icanon -echo
  eval "$1=\$(dd bs=1 count=1 2>/dev/null)"
  stty icanon echo
  echo "$char"
}

usage() {
  echo "USAGE: ./run-remote.sh GCLOUD_PROJECT GOOGLE_BUCKET NUM_WORKERS

GCLOUD_PROJECT is the project in Google Cloud that hosts the dataflow and bucket
GOOGLE_BUCKET is the bucket which will store that data for processing and results
NUM_WORKERS is the number of nodes to run in the cluster"
  exit "$1"
}

if [ "$1" = "-h" ] || [ "$1" == "--help" ]; then
  usage 0
fi

if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ] || [ ! -z "$4" ]; then
  usage 1
fi

GCLOUD_PROJECT="$1"
GOOGLE_BUCKET="$2"
NUM_WORKERS="$3"

echo "The results will be saved to the Google Bucket $GOOGLE_BUCKET."
echo "The dataflow and bucket will be located in the project '$GCLOUD_PROJECT' on Google Cloud."

if [ -z "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
  export GOOGLE_APPLICATION_CREDENTIALS="$(readlink -f ./dataflow-credentials.json)"
fi

if [ ! -f "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
  echo "
*************************************************************
Please download the JSON credentials for a service account on
Google Cloud with permissions for Dataflow and save them to
'${GOOGLE_APPLICATION_CREDENTIALS}'.
*************************************************************
"
  exit 1
fi

source "$SCRIPT_DIR/venv/bin/activate"

echo
echo -n "Preprocess data in $RAW_DATA_DIR into chunks (y/n)? "
read_char char
if [ "$char" = 'y' ]; then
  python -m preprocess \
    --raw "$RAW_DATA_DIR" \
    --chunk "$CHUNK_DATA_DIR"
fi

echo
echo -n "Transfer the input data to Google Cloud Bucket $GOOGLE_BUCKET (y/n)? "
read_char char
if [ "$char" = 'y' ]; then
  gsutil -m cp -J -R past2present beam_pipeline.py "$CHUNK_DATA_DIR" "$GOOGLE_BUCKET"
fi

echo
echo -n "Setup necessary Google Cloud Bucket folders in $GOOGLE_BUCKET (y/n)? "
read_char char
if [ "$char" = 'y' ]; then
  TEMP_FOLDER="$HOME/tmp123456789"
  for folder in 'staging tmp out'; do
    mkdir -p "$TEMP_FOLDER/$folder"
    touch "$TEMP_FOLDER/$folder/DELETEME"
    cd "$TEMP_FOLDER"
    gsutil cp -J -R "$folder" "$GOOGLE_BUCKET"
    gsutil rm "$GOOGLE_BUCKET/$folder/DELETEME"
    cd "$SCRIPT_DIR"
    rm -r "$TEMP_FOLDER"
  done
fi

echo
echo -n "Run pipeline on Google Dataflow (y/n)? "
read_char char
if [ "$char" = 'y' ]; then
  python -m beam_pipeline \
    --cloud \
    --project="$GCLOUD_PROJECT" \
    --autoscaling_algorithm=NONE \
    --num_workers "$NUM_WORKERS" \
    --worker_machine_type n1-standard-2 \
    --worker_disk_type compute.googleapis.com/projects//zones//diskTypes/pd-ssd \
    --disk_size_gb 30 \
    --zone=us-central1-f \
    --staging_location="$GOOGLE_BUCKET/staging" \
    --temp_location="$GOOGLE_BUCKET/tmp" \
    --setup_file=./setup.py \
    --input "$GOOGLE_BUCKET/$(basename "$(readlink -f $CHUNK_DATA_DIR)")/*.txt" \
    --output "$GOOGLE_BUCKET/out/dataset"

  echo
  echo '**********************************************************'
  echo "Output written to $GOOGLE_BUCKET/out/dataset-*"
  echo '**********************************************************'
  echo
fi
