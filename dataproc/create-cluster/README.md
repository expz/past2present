1. Enable Cloud Dataproc API, Compute Engine API and Google Cloud Storage API in the [console](https://console.cloud.google.com/).

2.  ```
    export PROJECT=my-project
    gcloud auth list
    gcloud config set account jskowera@gmail.com
    gcloud projects list
    gcloud config set project my-project
    ```

3. Run `gcloud auth application-default login` and click through browser prompts to give permission for API access.

4. Setup the directory by downloading `daisy`: `./setup.sh`

5. If the bucket is `gs://my-bucket` (check [image list](https://cloud.google.com/dataproc/docs/concepts/versioning/dataproc-versions#supported_cloud_dataproc_versions) for dataproc-version):
    ```
    python generate_custom_image.py --image-name gutenberg-ml --dataproc-version "1.3.19-deb9" --customization-script prepare-vm.sh --daisy-path ./daisy --zone us-central1-f --gcs-bucket gs://my-bucket --expire-days 30 --disk-size 15
    ```
    Expire days is default 30. Disk size is default 15GB.
