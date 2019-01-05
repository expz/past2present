#!/bin/bash

CLUSTER='cluster-1'
BUCKET='gs://***REMOVED***'

read_char() {
  stty -icanon -echo
  eval "$1=\$(dd bs=1 count=1 2>/dev/null)"
  stty icanon echo
  echo "$char"
}

if [ -n "$1" ]; then
  DATAFILE="$1"
else
  DATAFILE="data.txt"
fi

echo -n "Create cluster $CLUSTER (y/n)? "
read_char char
if [ "$char" = 'y' ]; then
  gcloud dataproc clusters create "$CLUSTER" \
    --image=gutenberg-ml \
    --master-boot-disk-size=500GB \
    --master-boot-disk-type=pd-ssd \
    --master-machine-type=n1-highmem-16 \
    --num-masters=1 \
    --zone=us-central1-f \
    --single-node
fi

echo -n "Upload files to bucket $BUCKET (y/n)? "
read_char char
if [ "$char" = 'y' ]; then
  gsutil cp -J preprocess.py past2present.py "$DATAFILE" 'gs://***REMOVED***'
fi

echo -n "Submit PySpark job to preprocess $DATAFILE (y/n)? "
read_char char
if [ "$char" = 'y' ]; then
  gcloud dataproc jobs submit pyspark --cluster="$CLUSTER" \
    --bucket="$(echo $BUCKET | tail -c +6)" \
    --files="$DATAFILE" \
    --py-files="past2present.py" \
    preprocess.py -- --batch=16 --threads=12 "$(pwd)"
fi

echo -n "Delete cluster $CLUSTER (y/n)? "
read_char char
if [ "$char" = 'y' ]; then
  gcloud dataproc clusters delete "$CLUSTER"
fi
