import time
_date=time.strftime("%x").replace("/", "-")

# Init Values
project_id = "vtxdemos"
region = "us-central1"
staging_bucket = "gs://vtxdemos-staging/ecommerce"
display_name_job = "tf-ecommerce-customjob"

#Docker Images
custom_train_image_uri_cpu = "us-central1-docker.pkg.dev/vtxdemos/custom-trains/tf-preprocess_cpu:1.0"
custom_train_image_uri_gpu = "us-central1-docker.pkg.dev/vtxdemos/custom-trains/tf-preprocess_gpu:1.0"
prebuilt_train_image_uri_cpu = "us-docker.pkg.dev/vertex-ai/training/tf-cpu.2-12.py310:latest"
prebuilt_train_image_uri_gpu = "us-docker.pkg.dev/vertex-ai/training/tf-gpu.2-12.py310:latest"
prebuilt_train_package_uri = "gs://vtxdemos-dist/ai-flex-train/trainer-0.1.tar.gz"
custom_predict_image_uri_cpu = "us-central1-docker.pkg.dev/vtxdemos/custom-predictions/tf-preprocess_cpu:1.0"
custom_predict_image_uri_gpu = "us-central1-docker.pkg.dev/vtxdemos/custom-predictions/tf-preprocess_gpu:1.0"
prebuilt_predict_image_uri_cpu = "us-docker.pkg.dev/vertex-ai/prediction/tf2-cpu.2-12:latest"
prebuilt_predict_image_uri_gpu = "us-docker.pkg.dev/vertex-ai/prediction/tf2-gpu.2-12:latest"

# Data source and storage
dataset_uri = "gs://vtxdemos-datasets-public/ecommerce/train.csv"
model_uri = f"gs://vtxdemos-models/ecommerce/{_date}"

# Machine Types
machine_type_cpu = "n1-standard-4"
machine_type_gpu = "n1-standard-4"
accelerator_type = "NVIDIA_TESLA_P100"
accelerator_count = 1
replica_count = 1