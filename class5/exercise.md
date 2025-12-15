# End-to-End Project Exercise: Deploy Flask App with PostgreSQL on AWS EC2

## Project Architecture
```
User → Route53 (DNS) → EC2 (NGINX + Flask Container) → RDS PostgreSQL
```

---

## Prerequisites Checklist
- [ ] AWS Account created
- [ ] Domain purchased (GoDaddy/Namecheap)
- [ ] Docker installed on local machine
- [ ] AWS CLI installed locally
- [ ] Git installed

---

## PART 1: Local Development Setup

### Step 1: Clone the Repository
```bash
git clone <your-repo-url>
cd <project-folder>
```

Your project structure should match:
```
├── app/
│   ├── app.py
│   ├── requirements.txt
│   ├── static/
│   └── templates/
├── ssl/
│   ├── cert.pem
│   └── key.pem
├── docker-compose.yaml
├── Dockerfile
├── nginx.conf
└── readme.md
```

### Step 2: Install AWS CLI
Follow: https://docs.aws.amazon.com/cli/v1/userguide/cli-chap-install.html

**For Mac/Linux:**
```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

**Verify installation:**
```bash
aws --version
```

### Step 3: Configure AWS Credentials

**Create IAM User:**
1. Go to AWS Console → IAM → Users → Create User
2. Name: `nov25-bootcamp`
3. **Don't** check console access
4. Attach policy: `AdministratorAccess` (for learning - use restricted in production)
5. Create access key → CLI
6. Save Access Key ID and Secret Access Key

**Configure CLI:**
```bash
aws configure
# Enter:
# AWS Access Key ID: <your-access-key>
# AWS Secret Access Key: <your-secret-key>
# Default region: ap-south-1
# Default output format: json
```

**Verify configuration:**
```bash
# View config files
cat ~/.aws/config
cat ~/.aws/credentials

# Test AWS connection
aws ec2 describe-instances --region ap-south-1
```

---

## PART 2: AWS ECR Setup

### Step 4: Create ECR Repository
```bash
# Login to AWS Console → ECR
# Click "Create repository"
# Repository name: nov25-class5
# Keep default settings → Create
```

**Note your ECR URI:**
```
879381241087.dkr.ecr.ap-south-1.amazonaws.com/nov25-class5
```

### Step 5: Build Docker Image (Platform Specific)

**Important:** For Mac M1/M2/M3 users, must specify platform!

```bash
# Build with platform specification
docker build --platform linux/amd64 -t 879381241087.dkr.ecr.ap-south-1.amazonaws.com/nov25-class5:2.0 .
```

**For Intel/AMD processors:**
```bash
docker build -t 879381241087.dkr.ecr.ap-south-1.amazonaws.com/nov25-class5:2.0 .
```

### Step 6: Push Image to ECR

```bash
# Login to ECR
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin 879381241087.dkr.ecr.ap-south-1.amazonaws.com

# Push image
docker push 879381241087.dkr.ecr.ap-south-1.amazonaws.com/nov25-class5:2.0

# Verify in AWS Console → ECR → Repository
```

---

## PART 3: AWS RDS Database Setup

### Step 7: Create PostgreSQL Database

1. **AWS Console → RDS → Create Database**
2. **Engine:** PostgreSQL
3. **Templates:** Free tier
4. **Settings:**
   - DB instance identifier: `nov25-class5`
   - Master username: `postgres`
   - Master password: `Admin123`
5. **Instance configuration:** db.t3.micro
6. **Storage:** 20 GB
7. **Connectivity:**
   - VPC: Default VPC
   - Public access: **No**
   - VPC security group: Create new → `rds-postgres-sg`
8. **Additional configuration:**
   - Initial database name: `postgres`
9. **Create database** (takes 5-10 minutes)

### Step 8: Note Database Details
```
Host: nov25-class5.cvik8accw2tk.ap-south-1.rds.amazonaws.com
Port: 5432
Username: postgres
Password: Admin123
Database: postgres
```

**Connection String:**
```
postgresql://postgres:Admin123@nov25-class5.cvik8accw2tk.ap-south-1.rds.amazonaws.com:5432/postgres
```

### Step 9: Configure RDS Security Group

1. Go to RDS → Databases → nov25-class5 → Connectivity & Security
2. Click on VPC security group
3. Edit inbound rules:
   - Type: PostgreSQL
   - Port: 5432
   - Source: Custom → (will add EC2 security group later)

---

## PART 4: EC2 Instance Setup

### Step 10: Launch EC2 Instance

1. **AWS Console → EC2 → Launch Instance**
2. **Name:** `student-portal-server`
3. **AMI:** Amazon Linux 2023
4. **Instance type:** t2.micro
5. **Key pair:** Create new → `nov25-class5-key` → Download .pem file
6. **Network settings:**
   - VPC: Default VPC
   - Auto-assign public IP: Enable
   - Security group name: `ec2-web-sg`
   - Inbound rules:
     - SSH (22) - My IP
     - HTTP (80) - Anywhere
     - HTTPS (443) - Anywhere
     - Custom TCP (5000) - Anywhere
7. **Launch instance**

### Step 11: Connect to EC2

```bash
# Set key permissions
chmod 400 nov25-class5-key.pem

# Connect via SSH
ssh -i nov25-class5-key.pem ec2-user@<EC2_PUBLIC_IP>
```

### Step 12: Install Docker on EC2

```bash
# Update system
sudo dnf update -y

# Install Docker
sudo dnf install -y docker

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add ec2-user to docker group
sudo usermod -aG docker ec2-user

# Exit and reconnect for changes to take effect
exit

# Reconnect
ssh -i nov25-class5-key.pem ec2-user@<EC2_PUBLIC_IP>

# Verify Docker
docker --version
docker ps
```

### Step 13: Install Docker Compose

```bash
# Create Docker CLI plugins directory
DOCKER_CONFIG=${DOCKER_CONFIG:-$HOME/.docker}
mkdir -p $DOCKER_CONFIG/cli-plugins

# Download Docker Compose
curl -SL https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-linux-x86_64 -o $DOCKER_CONFIG/cli-plugins/docker-compose

# Make executable
chmod +x $DOCKER_CONFIG/cli-plugins/docker-compose

# Verify installation
docker compose version
```

### Step 14: Create IAM Role for EC2

1. **IAM → Roles → Create role**
2. **Trusted entity:** AWS service → EC2
3. **Permissions:** `EC2InstanceProfileForImageBuilderECRContainerBuilds`
4. **Role name:** `EC2-ECR-Access-Role`
5. **Create role**

**Attach role to EC2:**
1. EC2 → Instances → Select instance
2. Actions → Security → Modify IAM role
3. Select `EC2-ECR-Access-Role`
4. Update IAM role

### Step 15: Update Security Groups

**EC2 Security Group (ec2-web-sg):**
- Add outbound rule for PostgreSQL (5432) to RDS security group

**RDS Security Group (rds-postgres-sg):**
1. Edit inbound rules
2. Add rule:
   - Type: PostgreSQL
   - Port: 5432
   - Source: Custom → Select `ec2-web-sg` (EC2 security group)

---

## PART 5: Deploy Application on EC2

### Step 16: Login to ECR from EC2

```bash
# Login to ECR
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin 879381241087.dkr.ecr.ap-south-1.amazonaws.com
```

### Step 17: Test Database Connectivity

```bash
# Pull PostgreSQL client image
docker run --rm -it postgres:16 psql -h nov25-class5.cvik8accw2tk.ap-south-1.rds.amazonaws.com -p 5432 -U postgres -d postgres

# Enter password: Admin123

# If connected successfully, you'll see:
postgres=#

# List databases
\l

# Exit
\q
```

### Step 18: Run Application Container

```bash
# Set environment variable
export DATABASE_URL=postgresql://postgres:Admin123@nov25-class5.cvik8accw2tk.ap-south-1.rds.amazonaws.com:5432/postgres

# Pull and run container
docker run -e DATABASE_URL=$DATABASE_URL -td -p 5000:5000 879381241087.dkr.ecr.ap-south-1.amazonaws.com/nov25-class5:2.0

# Check container status
docker ps

# View logs
docker logs <container-id>

# Test locally on EC2
curl http://localhost:5000
```

### Step 19: Test from Browser

```
http://<EC2_PUBLIC_IP>:5000
```

---

## PART 6: SSL Certificate & NGINX Setup

### Step 20: Create SSL Certificate in ACM

1. **AWS Console → Certificate Manager (ACM)**
2. **Request certificate** → Public certificate
3. **Fully qualified domain name:** `nov25.yourdomain.com`
4. **Validation method:** DNS validation
5. **Key algorithm:** RSA 2048
6. **Request certificate**
7. **Create record in Route 53** (click button to auto-create)
8. Wait for status: **Issued**

### Step 21: Export Certificate

1. Click on certificate
2. **Export certificate**
3. **Passphrase:** `1234` (simple for demo)
4. **Confirm passphrase:** `1234`
5. **PEM encoding**
6. Copy all three values:
   - Certificate body → save locally as `cert.pem`
   - Certificate chain → append to `cert.pem`
   - Private key → save locally as `key.pem`

### Step 22: Remove Passphrase from Key

```bash
# On your local machine
openssl rsa -in key.pem -out key-new.pem

# Enter passphrase: 1234
# This creates key-new.pem without passphrase
```

### Step 23: Create SSL Directory on EC2

```bash
# On EC2
mkdir -p ~/ssl
cd ~/ssl

# Create cert.pem
vi cert.pem
# Paste certificate body + certificate chain
# Save and exit (:wq)

# Create key.pem
vi key-new.pem
# Paste private key (without passphrase)
# Save and exit (:wq)

# Verify files
ls -la
```

### Step 24: Create nginx.conf

```bash
cd ~
vi nginx.conf
```

**Paste this configuration:**
```nginx
events {
    worker_connections 1024;
}

http {
    server {
        listen 80;
        server_name nov25.yourdomain.com;
        
        # Redirect HTTP to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl;
        server_name nov25.yourdomain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key-new.pem;

        location / {
            proxy_pass http://flask-app:5000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
```

### Step 25: Create docker-compose.yaml

```bash
vi docker-compose.yaml
```

**Paste this configuration:**
```yaml
version: '3.8'

services:
  nginx:
    image: nginx:latest
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - flask-app
    networks:
      - app-network

  flask-app:
    image: 879381241087.dkr.ecr.ap-south-1.amazonaws.com/nov25-class5:2.0
    environment:
      - DATABASE_URL=postgresql://postgres:Admin123@nov25-class5.cvik8accw2tk.ap-south-1.rds.amazonaws.com:5432/postgres
    networks:
      - app-network

networks:
  app-network:
    driver: bridge
```

### Step 26: Deploy with Docker Compose

```bash
# Stop any running containers
docker stop $(docker ps -q)

# Start services
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs

# Test
curl http://localhost
```

---

## PART 7: DNS Configuration

### Step 27: Create Hosted Zone in Route 53

1. **Route 53 → Hosted zones → Create hosted zone**
2. **Domain name:** `yourdomain.com`
3. **Type:** Public hosted zone
4. **Create**
5. **Copy the 4 nameservers**

### Step 28: Update Nameservers at Domain Registrar

1. Go to your domain registrar (GoDaddy/Namecheap)
2. Find DNS settings / Nameservers
3. Change to custom nameservers
4. Paste the 4 nameservers from Route 53
5. Save (propagation takes 5-60 minutes)

### Step 29: Create A Record

1. **Route 53 → Hosted zones → yourdomain.com**
2. **Create record**
3. **Record name:** `nov25`
4. **Record type:** A
5. **Value:** `<EC2_PUBLIC_IP>`
6. **TTL:** 300
7. **Create records**

### Step 30: Test DNS

```bash
# Wait 5-10 minutes for propagation

# Test DNS resolution
nslookup nov25.yourdomain.com

# Should return your EC2 public IP

# Test in browser
https://nov25.yourdomain.com
```

---

## PART 8: Verification & Testing

### Step 31: Complete Testing Checklist

- [ ] HTTP redirects to HTTPS
- [ ] HTTPS shows secure padlock in browser
- [ ] Application loads correctly
- [ ] Can create/view posts (database working)
- [ ] No certificate errors

### Step 32: Troubleshooting Commands

```bash
# On EC2 - Check containers
docker compose ps
docker compose logs nginx
docker compose logs flask-app

# Test database from EC2
docker exec -it <flask-container-id> bash
psql -h nov25-class5.cvik8accw2tk.ap-south-1.rds.amazonaws.com -U postgres -d postgres

# Check NGINX config
docker exec -it <nginx-container-id> nginx -t

# View NGINX logs
docker compose logs nginx | tail -50

# Restart services
docker compose restart

# Full restart
docker compose down
docker compose up -d
```

---

## PART 9: Cleanup (Important!)

### Step 33: Stop Resources to Avoid Charges

```bash
# On EC2 - Stop containers
docker compose down

# In AWS Console:
# 1. EC2 → Stop instance (don't terminate yet)
# 2. RDS → Stop database (7 days max)
```

### Step 34: When Done with Project - Delete Resources

1. **EC2:** Terminate instance
2. **RDS:** Delete database (uncheck snapshot)
3. **ECR:** Delete repository
4. **Route 53:** Delete hosted zone (if not using domain)
5. **ACM:** Delete certificate
6. **IAM:** Delete user/role if not needed

---

## Success Criteria

✅ Application accessible via HTTPS  
✅ Database storing and retrieving data  
✅ NGINX properly proxying requests  
✅ SSL certificate valid (green padlock)  
✅ Custom domain working

---

## Common Issues & Solutions

**Issue 1: Container can't connect to RDS**
- Check security groups allow EC2 → RDS on port 5432
- Verify DATABASE_URL is correct
- Test with psql from EC2

**Issue 2: Domain not resolving**
- Wait 30-60 minutes for DNS propagation
- Verify nameservers updated at registrar
- Check A record points to correct IP

**Issue 3: SSL errors**
- Verify cert.pem contains both certificate body AND chain
- Ensure key has no passphrase
- Check nginx.conf paths match volume mounts

**Issue 4: Can't pull ECR image**
- Verify IAM role attached to EC2
- Re-run ECR login command
- Check ECR repository exists in correct region

---

## Next Steps

After completing this exercise:
1. Create your own `about.yaml` file describing yourself
2. Stop all AWS resources
3. Prepare for GitHub Actions automation (next class)
