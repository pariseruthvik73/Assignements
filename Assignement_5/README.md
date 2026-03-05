# Assignment 5: Deploy PHP App with PostgreSQL on AWS EC2

## 1. Project Overview

This project deploys a PHP-based daily task tracker called DayFlow on AWS EC2 with a managed PostgreSQL database (RDS). The assignment demonstrates a full cloud deployment lifecycle using Docker, ECR, RDS, and Route53.

Live URL: https://nov25.ruthvik.com  
Student: Ruthvik Parise  
Tech Stack: PHP 8.2, nginx, PostgreSQL (RDS), Docker, AWS EC2

---

## 2. AWS CLI Setup

We installed AWS CLI in GitHub Codespaces to manage AWS resources from the browser.

```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure credentials
aws configure
# Enter: Access Key ID, Secret Access Key, region: us-east-1

# Verify identity
aws sts get-caller-identity
```

---

## 3. Build and Push Docker Image to ECR

```bash
# Create ECR repository
aws ecr create-repository --repository-name nov25-class5 --region us-east-1

# Build for EC2 compatibility
docker build --platform linux/amd64 -t 312846473135.dkr.ecr.us-east-1.amazonaws.com/nov25-class5:1.0 .

# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 312846473135.dkr.ecr.us-east-1.amazonaws.com

# Push image
docker push 312846473135.dkr.ecr.us-east-1.amazonaws.com/nov25-class5:1.0
```

---

## 4. Create RDS PostgreSQL Database

We created a managed PostgreSQL database on AWS RDS via the console with these settings:

```
Engine: PostgreSQL 16
Instance: db.t3.micro
Database: postgres
Username: postgres
Password: Admin123
Security Group: rds-postgres-sg (allows port 5432 from ec2-web-sg only)
```

Get RDS endpoint:

```bash
aws rds describe-db-instances --region us-east-1 --query 'DBInstances[*].[DBInstanceIdentifier,Endpoint.Address]' --output table
```

RDS Endpoint: `nov25-class5.cy9waccq8dq8.us-east-1.rds.amazonaws.com`

---

## 5. Launch and Configure EC2 Instance

```bash
# Get EC2 IP
aws ec2 describe-instances --region us-east-1 --query 'Reservations[*].Instances[*].[PublicIpAddress,State.Name]' --output table

# Get Codespaces IP (changes every session)
curl checkip.amazonaws.com

# Add Codespaces IP to EC2 security group for SSH
aws ec2 authorize-security-group-ingress --group-name ec2-web-sg --protocol tcp --port 22 --cidr <CODESPACES_IP>/32 --region us-east-1

# SSH into EC2
ssh -i nov25-class5-key.pem ec2-user@34.205.191.236
```

Install Docker on EC2:

```bash
sudo dnf update -y
sudo dnf install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ec2-user

# Install Docker Compose
DOCKER_CONFIG=${DOCKER_CONFIG:-$HOME/.docker}
mkdir -p $DOCKER_CONFIG/cli-plugins
curl -SL https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-linux-x86_64 -o $DOCKER_CONFIG/cli-plugins/docker-compose
chmod +x $DOCKER_CONFIG/cli-plugins/docker-compose
```

Attach IAM Role `EC2-ECR-Access-Role` to EC2 instance (via console) so it can pull from ECR without storing credentials.

---

## 6. Deploy Application on EC2

```bash
# Login to ECR from EC2
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 312846473135.dkr.ecr.us-east-1.amazonaws.com

# Test RDS connectivity
docker run --rm -it postgres:16 psql -h nov25-class5.cy9waccq8dq8.us-east-1.rds.amazonaws.com -p 5432 -U postgres -d postgres

# Run PHP app connected to RDS
docker run \
  -e DB_HOST=nov25-class5.cy9waccq8dq8.us-east-1.rds.amazonaws.com \
  -e DB_PORT=5432 \
  -e DB_NAME=postgres \
  -e DB_USER=postgres \
  -e DB_PASSWORD=Admin123 \
  -td -p 80:80 \
  312846473135.dkr.ecr.us-east-1.amazonaws.com/nov25-class5:1.0
```

Result: App successfully connected to RDS PostgreSQL and served on port 80.

---

## 7. SSL Certificate with Let's Encrypt

Free ACM certificates cannot be exported, so we used Let's Encrypt via Certbot.

```bash
# Install Certbot
sudo dnf install -y python3-pip
sudo pip3 install certbot

# Stop containers to free port 80
docker stop $(docker ps -q)

# Request SSL certificate
sudo certbot certonly --standalone -d nov25.ruthvik.com --email pariseruthvik73@gmail.com --agree-tos --non-interactive
```

Result: Certificate saved at `/etc/letsencrypt/live/nov25.vishnukosuri.com/fullchain.pem`

Copy certificates for Docker volume mount:

```bash
mkdir -p ~/ssl
sudo cp /etc/letsencrypt/live/nov25.ruthvik.com/fullchain.pem ~/ssl/cert.pem
sudo cp /etc/letsencrypt/live/nov25.ruthvik.com/privkey.pem ~/ssl/key.pem
sudo chmod 644 ~/ssl/cert.pem
sudo chmod 600 ~/ssl/key.pem
```

---

## 8. Configure DNS with Route53

We pointed `nov25.ruthvik.com` (registered on GoDaddy) to EC2 using Route53.

```bash
# List hosted zones
aws route53 list-hosted-zones --query 'HostedZones[*].[Id,Name]' --output table

# Get Route53 nameservers
aws route53 list-resource-record-sets --hosted-zone-id Z07804063UTVB9OMK1MMB --query "ResourceRecordSets[?Type=='NS'].ResourceRecords[*].Value" --output text
```

Updated GoDaddy nameservers to (remove trailing dots):

```
ns-172.awsdns-21.com
ns-1009.awsdns-62.net
ns-1437.awsdns-51.org
ns-1555.awsdns-02.co.uk
```

Add A record pointing to EC2:

```bash
aws route53 change-resource-record-sets --hosted-zone-id Z07804063UTVB9OMK1MMB --change-batch '{
  "Changes": [{
    "Action": "CREATE",
    "ResourceRecordSet": {
      "Name": "nov25.ruthvik.com",
      "Type": "A",
      "TTL": 300,
      "ResourceRecords": [{"Value": "34.205.191.236"}]
    }
  }]
}'
```

---

## 9. Final Deployment with HTTPS

Updated nginx.conf to handle SSL and rebuilt image as tag 3.0.

```bash
# Stop old containers
docker stop $(docker ps -q)
docker rm $(docker ps -aq)

# Pull latest image
docker pull 312846473135.dkr.ecr.us-east-1.amazonaws.com/nov25-class5:3.0

# Run with SSL certificates mounted
docker run \
  -e DB_HOST=nov25-class5.cy9waccq8dq8.us-east-1.rds.amazonaws.com \
  -e DB_PORT=5432 \
  -e DB_NAME=postgres \
  -e DB_USER=postgres \
  -e DB_PASSWORD=Admin123 \
  -v ~/ssl:/etc/nginx/ssl \
  -td -p 80:80 -p 443:443 \
  312846473135.dkr.ecr.us-east-1.amazonaws.com/nov25-class5:3.0

# Verify HTTP redirects to HTTPS
curl -I http://nov25.ruthvik.com
```

Result: `HTTP/1.1 301 Moved Permanently` — Successfully redirecting to HTTPS.

---

## 10. Troubleshooting

### Port 80 Already Allocated

```
Error: Bind for 0.0.0.0:80 failed: port is already allocated
```

Fix: Stop all containers before launching new ones.

```bash
docker stop $(docker ps -q)
docker rm $(docker ps -aq)
```

### SSH Connection Timed Out

Cause: Codespaces IP changes every session.

Fix: Check new IP and update security group.

```bash
curl checkip.amazonaws.com
aws ec2 authorize-security-group-ingress --group-name ec2-web-sg --protocol tcp --port 22 --cidr <NEW_IP>/32 --region us-east-1
```

### ACM Certificate Cannot Be Exported

Cause: Free ACM public certificates don't support export.

Fix: Used Let's Encrypt via Certbot instead.

### GoDaddy Nameserver Error

Cause: AWS CLI outputs nameservers with trailing dots.

Fix: Remove trailing dot before entering in GoDaddy.

### Commands on Wrong Terminal

Two terminals open (Codespaces and EC2 SSH) — ran AWS commands on EC2 which lacks IAM permissions.

Identify terminal:

```
Codespaces:  @pariseruthvik73 ➜ /workspaces/Assignements/Assignement_5 (main) $
EC2:         [ec2-user@ip-172-31-6-139 ~]$
```

---

## 11. Key Concepts Learned

### Docker Environment Variables

We passed database credentials into the container using `-e` flags at runtime. This means the same Docker image can connect to different databases without rebuilding.

```bash
docker run -e DB_HOST=my-rds-endpoint -e DB_PASSWORD=secret my-image
```

Inside PHP, `db.php` reads these with `getenv('DB_HOST')`.

### SSL Offloading (SSL Termination)

nginx handles all HTTPS encryption and decryption. The PHP app only ever receives plain HTTP — it never has to deal with SSL directly.

```
Browser → HTTPS → nginx (decrypts SSL) → HTTP → PHP-FPM
```

### Volume Mounts

The `-v` flag maps a folder on the EC2 host into the container's filesystem.

```bash
-v ~/ssl:/etc/nginx/ssl
# ~/ssl on EC2 maps to /etc/nginx/ssl inside container
```

### IAM Roles vs Access Keys

EC2 instance uses an IAM Role to access ECR — no access keys stored on the server. This is more secure than hardcoding credentials.

### DNS Record Types

| Record | Purpose |
|--------|---------|
| A | Maps domain name directly to an IP address |
| CNAME | Creates an alias — maps one domain to another domain |
| NS | Declares which nameservers are authoritative for a domain |

---

## 12. Architecture

```
User Browser
     │
     ▼ HTTPS (port 443)
Route53 DNS (nov25.ruthvik.com)
     │
     ▼
EC2 Instance (34.205.191.236)
     │
     └── Docker Container: nov25-class5:3.0
              │
              ├── nginx → SSL termination → HTTP redirect
              └── PHP-FPM → Runs app
                       │
                       ▼ Port 5432
              RDS PostgreSQL (nov25-class5.cy9waccq8dq8.us-east-1.rds.amazonaws.com)
```

---

## 13. AWS Resources

| Resource | Value |
|----------|-------|
| EC2 IP | 34.205.191.236 |
| EC2 Instance | student-portal-server (t2.micro, Amazon Linux 2023) |
| RDS Endpoint | nov25-class5.cy9waccq8dq8.us-east-1.rds.amazonaws.com |
| ECR Repository | 312846473135.dkr.ecr.us-east-1.amazonaws.com/nov25-class5 |
| Domain | nov25.ruthvik.com |
| Route53 Hosted Zone | Z07804063UTVB9OMK1MMB |
| IAM Role | EC2-ECR-Access-Role |

---

## 14. Stop Resources (Avoid Charges)

```bash
# On EC2
docker stop $(docker ps -q)
```

In AWS Console:
- EC2 → `student-portal-server` → Stop
- RDS → `nov25-class5` → Stop temporarily

---

## 15. Conclusion

This assignment successfully demonstrated:

1. Containerizing a PHP application with nginx using Docker
2. Pushing images to AWS ECR private registry
3. Provisioning managed PostgreSQL on AWS RDS
4. Deploying to EC2 with Docker and IAM roles
5. Securing with Let's Encrypt SSL certificates
6. Configuring DNS with Route53
7. Full HTTPS deployment with SSL termination at nginx

Key Takeaway: Docker environment variables allow the same image to work in different environments (local development with docker-compose, production with RDS) without rebuilding. SSL termination at the proxy layer (nginx) simplifies application code by handling encryption separately.

---

*Assignment 5 — AWS EC2 PHP Deployment | March 2026*
