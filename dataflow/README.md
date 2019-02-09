# Past2Present on Apache Beam/Google Dataflow

Transform sentences using Apache Beam.

The preprocessing is specially designed to work with plain text files from the Gutenberg project and removes things like footnotes and character prompts in plays.

__This project uses Python 2, because Python 3 is not supported by Google Cloud.__

## Prerequisites

To run on Google Cloud this project requires `gcloud` to be installed. It also requires a project to be ceated at the [cloud console](https://console.cloud.google.com). The project must have the dataflow API enabled. Then `gcloud` must be set up using
```
gcloud config set account name@gmail.com
gcloud config set project my-project
gcloud auth login  # This will open a web browser to complete the login.
```

## Usage (Local)

0. Run `./setup.sh` if you have not already.

1. Put documents to transform in the `raw` directory.

2. Run `./run-local.sh`

## Usage (Google Cloud)

0. Run `./setup.sh` if you have not already.

1. Put documents to transform in the `raw` directory.

2. Save the JSON credentials for a service account with permission to access Google Dataflow and Google Cloud Buckets to `dataflow-credentials.json`.

3. Run `./run-remote.sh`

## Tests

To run the tests, from this directory run
```
source venv/bin/activate
pytest -v test/test_past2present.py
pytest -v test/test_clean_text.py
pytest -v test/test_beam_pipeline.py
```
