#!/bin/bash

export GOOGLE_APPLICATION_CREDENTIALS="$(readlink -f ./***REMOVED***)"

source venv/bin/activate

gsutil -m cp -J -R past2present beam_pipeline.py data gs://***REMOVED***/past2present

python -m beam_pipeline \
  --cloud \
  --project=***REMOVED*** \
  --autoscaling_algorithm=NONE \
  --num_workers 16 \
  --worker_machine_type n1-standard-2 \
  --worker_disk_type compute.googleapis.com/projects//zones//diskTypes/pd-ssd \
  --disk_size_gb 30 \
  --zone=us-central1-f \
  --staging_location=gs://***REMOVED***/past2present/staging \
  --temp_location=gs://***REMOVED***/tmp \
  --setup_file=./setup.py \
  --input 'gs://***REMOVED***/past2present/data/*.txt' \
  --output 'gs://***REMOVED***/past2present/out/dataset'
