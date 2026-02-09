# Flask API with Docker - SRE Best Practices

## 1. Project Overview

This project demonstrates a containerized Flask API using SQLite. The core objective was to implement SRE Best Practices, specifically:

* **Persistence**: Ensuring data survives container deletion.
* **Networking**: Using custom bridge networks for service discovery.
* **Automation**: Creating shell scripts for consistent integration testing.
* **Hybrid Logic**: Allowing the same code to run locally in Codespaces or inside Docker.

---

## 2. The Application Setup

### `app.py` (Hybrid logic version)

We modified the code to detect the environment so it wouldn't crash due to root-level permission issues in Codespaces.
```python
# Hybrid logic to avoid PermissionError: [Errno 13]
if os.environ.get('DOCKER_CONTAINER') == 'true':
    db_dir = '/app/data'
else:
    db_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

os.makedirs(db_dir, exist_ok=True)
```

### `Dockerfile`

We added an environment variable (`ENV`) so the Python script knows when it is inside the container.
```dockerfile
FROM python:3.12-slim
WORKDIR /app
ENV DOCKER_CONTAINER=true
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p /app/data
EXPOSE 5000
CMD ["python", "app.py"]
```

---

## 3. Infrastructure & Network Setup

Before running the containers, we manually created the isolated environment.
```bash
# Create custom network for DNS pinging
docker network create blog-network

# Create persistent volume for SQLite
docker volume create blog-data
```

---

## 4. Building and Pushing Images

We used a Docker Personal Access Token (PAT) to log in and push the verified image to the registry.
```bash
# Login using PAT
echo "dckr_pat_..." | docker login -u pariseruthvik73 --password-stdin

# Build the image
docker build -t blog-app .

# Tag and Push
docker tag blog-app pariseruthvik73/blog-app:v1
docker push pariseruthvik73/blog-app:v1
```

---

## 5. Deployment & Debugging (The "Conflict" Phase)

We encountered a `Conflict` error because port 5000 was taken. We solved this by mapping to Port 5001.
```bash
# Stop conflicting containers
docker rm -f blog-container

# Run the persistent service on a new port
docker run -d \
  --name blog-service \
  --network blog-network \
  -v blog-data:/app/data \
  -p 5001:5000 \
  pariseruthvik73/blog-app:v1
```

---

## 6. Verification & Behavior Analysis

### Automated Testing (`test_api.sh`)

We changed user permissions to make our testing script executable.
```bash
chmod +x test_api.sh
./test_api.sh
```

### Direct Database Inspection

Since the `slim` image lacks `sqlite3`, we used Python-in-container to verify the data was actually in the volume.
```bash
docker exec -it blog-service python -c "import sqlite3; conn = sqlite3.connect('/app/data/blog.db'); cursor = conn.cursor(); cursor.execute('SELECT * FROM post'); print(cursor.fetchall()); conn.close()"
```

**Result**: `[(1, 'SRE Persistence Test', ...)]` — Success!

### DNS Pinging (Service Discovery)

We verified that containers on the `blog-network` can communicate via their Names instead of IP addresses.
```bash
docker exec -it blog-service python -c "import urllib.request; print(urllib.request.urlopen('http://blog-container:5000/health').read())"
```

**Result**: `b'{"status": "healthy"}'` — Internal DNS works!

---

## 7. Conclusion

By the end of this assignment, we successfully:

1. Resolved PermissionError [Errno 13] using absolute path logic.
2. Resolved Port Allocation conflicts using host-port mapping.
3. Proved Data Persistence across different containers using shared volumes.
4. Demonstrated Microservice Connectivity via Docker DNS.