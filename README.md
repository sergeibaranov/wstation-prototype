## WStation demo - GCP deployment
### In GCP console create project and enable billing

- Note your project id

### Cloud Shell setup

- Set your project id
`gcloud config set project [PROJECT-ID]`
- Enable all necessary cloud services

```bash
gcloud services enable alloydb.googleapis.com \
                       compute.googleapis.com \
                       cloudresourcemanager.googleapis.com \
                       servicenetworking.googleapis.com \
                       vpcaccess.googleapis.com \
                       aiplatform.googleapis.com \
                       cloudbuild.googleapis.com \
                       artifactregistry.googleapis.com \
                       run.googleapis.com \
                       iam.googleapis.com
```

### Create AlloyDB cluster

- Create private IP range

```bash
gcloud compute addresses create psa-range \
    --global \
    --purpose=VPC_PEERING \
    --prefix-length=24 \
    --description="VPC private service access" \
    --network=default
```

- Create private connection using above IP range

```bash
gcloud services vpc-peerings connect \
    --service=servicenetworking.googleapis.com \
    --ranges=psa-range \
    --network=default
```

- Define password, region and cluster name. Note password

```bash
export PGPASSWORD=`openssl rand -hex 12` 
echo $PGPASSWORD
export REGION=us-central1
export ADBCLUSTER=alloydb-aip-01
```

- Create cluster

```bash
gcloud alloydb clusters create $ADBCLUSTER \
    --password=$PGPASSWORD \
    --network=default \
    --region=$REGION
```

- Create primary instance in the cluster

```bash
gcloud alloydb instances create $ADBCLUSTER-pr \
    --instance-type=PRIMARY \
    --cpu-count=2 \
    --region=$REGION \
    --cluster=$ADBCLUSTER
```

- Note DB instance IP

```bash
export INSTANCE_IP=$(gcloud alloydb instances describe $ADBCLUSTER-pr --cluster=$ADBCLUSTER --region=$REGION --format="value(ipAddress)")
echo $INSTANCE_IP
```

### Create a VM to manage the database

- Create identity for a VM

```bash
PROJECT_ID=$(gcloud config get-value project)
gcloud iam service-accounts create compute-aip --project $PROJECT_ID
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:compute-aip@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/cloudbuild.builds.editor"
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:compute-aip@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.admin"
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:compute-aip@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.admin"
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:compute-aip@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.admin"
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:compute-aip@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:compute-aip@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/alloydb.viewer"
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:compute-aip@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:compute-aip@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/serviceusage.serviceUsageConsumer"
```

- Deploy a VM

```bash
export ZONE=us-central1-a
gcloud compute instances create instance-1 \
    --zone=$ZONE \
    --create-disk=auto-delete=yes,boot=yes,image=projects/debian-cloud/global/images/$(gcloud compute images list --filter="family=debian-12 AND family!=debian-12-arm64" --format="value(name)") \
    --scopes=https://www.googleapis.com/auth/cloud-platform \
  --service-account=compute-aip@$PROJECT_ID.iam.gserviceaccount.com
```

- SSH into VM
`gcloud compute ssh instance-1 --zone=us-central1-a`
- Define DB variables

```bash
export PGPASSWORD=[noted password]
export PROJECT_ID=$(gcloud config get-value project)
export REGION=us-central1
export ADBCLUSTER=alloydb-aip-01
export INSTANCE_IP=$(gcloud alloydb instances describe $ADBCLUSTER-pr --cluster=$ADBCLUSTER --region=$REGION --format="value(ipAddress)")
```

- Create a database
`psql "host=$INSTANCE_IP user=postgres" -c "CREATE DATABASE [DB-NAME]"`

### Deploy the app to Cloud Run (in Cloud Shell)

- Clone GitHub repo
`git clone https://github.com/sergeibaranov/wstation-prototype.git`
- Create `config.yml` file in project directory
`cp config-example.yml config.yml`
- Copy DB primary instance IP, DB password and database name to `config.yml`
- Define project_id
`export PROJECT_ID=$(gcloud config get-value project)`
- Create a service account for main app; give it access to VertexAI

```bash
gcloud iam service-accounts create main-app-identity
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:main-app-identity@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"
```

- Deploy main app to Cloud Run

```bash
cd ~/wstation-prototype
gcloud alpha run deploy main-app \
    --source=./\
    --allow-unauthenticated \
    --service-account main-app-identity \
    --region us-central1 \
    --network=default \
    --quiet
```

## API reference

### List suppliers
GET /suppliers

### Create / update supplier data
POST /suppliers

Request body {"name": "[supplier name]", "email": "[supplier email]", "address": "[supplier address]"}

If data with the same email is submitted, it acts as update
### Ingest proposal email
POST /proposal_emails
 
request body {"rfp_name": "[RFP name]", "from_address": "[email address]", "text": "[email body]"}

As a result a proposal record is created in the database

### Get proposals for an RFP
GET /proposals/:rfp_name

URL path parameters: rfp_name (str)


## Scalability notes
1. Webserver layer is separated from the data layer, so that they can be scaled independently.
2. Webserver is deployed to Cloud Run - fully managed service that scales up and down depending on the traffic. It can handle spikes in traffic and stay cost-efficient during low usage.
3. Cloud Run tradeoffs are: cold starts (takes longer to respond if there was no traffic recently); statelessness (may become important if we need to store LLM session history), resource (CPU, memory) limits for 1 request
4. Database is using AlloyDB, a managed DB service that enables independent scalability of CPU and storage, that can provide most cost efficient combination for our specific needs. As a trafeoff, it may be too costly for a small scale applications.
5. As a more budget friendly solution for the prototyping phase, CloudSQL can be considered, although it is less performant and less scalable.
