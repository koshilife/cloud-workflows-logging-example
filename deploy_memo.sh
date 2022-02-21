gcloud config set project ${GCP_PROJECT}

app_version="v1"
# app_version="v2"
app_name_prefix="logging-example"
app_name="${app_name_prefix}-${app_version}"

# ==============================================================
# Cloud Run

cloudrun_name=${app_name}
cloudrun_path="cloudruns/${app_version}"

# deploy
gcloud run deploy ${cloudrun_name} \
  --source ${cloudrun_path} \
  --no-allow-unauthenticated \
  --ingress internal \
  --region asia-northeast1 \
  --max-instances 2 \
  --min-instances 0 \
  --cpu 1 \
  --memory 1Gi \
  --set-env-vars "GCP_PROJECT=${GCP_PROJECT}"

# grants the workflow's service account to invoke the Cloud Run
gcloud run services add-iam-policy-binding ${cloudrun_name} \
    --region=asia-northeast1 \
    --member=serviceAccount:${WORKKFLOWS_SERVICE_ACCOUNT} \
    --role=roles/run.invoker

# ==============================================================
# Cloud Functions

func_name=${app_name}
func_path="./functions/${app_version}"

# deploy
gcloud functions deploy ${func_name} \
  --entry-point main \
  --runtime python39 \
  --trigger-http \
  --region asia-northeast1 \
  --timeout 120 \
  --memory 128MB \
  --min-instances 0 \
  --max-instances 2 \
  --source $func_path \
  --set-env-vars "GCP_PROJECT=${GCP_PROJECT}"

# grants the workflow's service account to invoke the Cloud Functions
gcloud functions add-iam-policy-binding ${func_name} \
    --region=asia-northeast1 \
    --member=serviceAccount:${WORKKFLOWS_SERVICE_ACCOUNT} \
    --role=roles/cloudfunctions.invoker

# ==============================================================
# Cloud Workflows

workflow_name=${app_name}
source_path="./workflows/${app_version}.yml"

# deploy
gcloud workflows deploy ${workflow_name} \
                --source=${source_path} \
                --location=asia-southeast1 \
                --service-account=${WORKKFLOWS_SERVICE_ACCOUNT}

# executes the workflow
gcloud workflows run --project=${GCP_PROJECT} --location=asia-southeast1 ${workflow_name} --data='{}'
