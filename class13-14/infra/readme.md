
# Dev
## Terraform init

terraform init -backend-config=vars/dev.tfbackend

terraform plan -var-file=vars/dev.tfvars

terraform apply -var-file=vars/dev.tfvars


# prod
## Terraform init

terraform init -backend-config=vars/prod.tfbackend


terraform plan -var-file=vars/prod.tfvars

terraform apply -var-file=vars/prod.tfvars


# if kms key creation fail with name duplicate

aws kms schedule-key-deletion --key-id <KeyId> --pending-window-in-days 0
