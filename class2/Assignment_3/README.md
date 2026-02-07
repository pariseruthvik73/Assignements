# Assignment 3: Multi-Container with Custom Network

## Overview
This assignment demonstrates Docker networking by creating two separate applications (backend API and frontend) that communicate with each other on a custom Docker network.

## Docker Concepts Covered

### Custom Bridge Network
- **User-Defined Bridge Network**: Custom network that allows containers to communicate using container names
- **Service Discovery**: Containers can find each other by name instead of IP addresses
- **Network Isolation**: Only containers on the same network can communicate with each other
- **DNS Resolution**: Docker provides automatic DNS resolution for container names on custom networks

### Multi-Container Architecture
- **Backend/Frontend Separation**: Splitting application into microservices
- **Inter-Container Communication**: Containers talking to each other over the network
- **Port Exposure**: Selective exposure of ports (only frontend exposed to host)

### Why Custom Networks?
Default bridge networks require IP addresses for communication, which change frequently. Custom networks allow containers to communicate using stable container names, making applications more reliable and easier to manage.

## Project Structure
```
assignment-3/
 ├── backend/ 
 │   ├── app.py              # Flask backend API (returns jokes) 
 │   ├── requirements.txt    # Python dependencies 
 │   ├── Dockerfile          # Backend Docker image 
 │   └── .dockerignore       # Exclude files 
 ├── frontend/ │   
 ├── app.py              # Flask frontend (displays jokes) 
 │   ├── requirements.txt    # Python dependencies 
 │   ├── Dockerfile          # Frontend Docker image 
 │   └── .dockerignore       # Exclude files 
 └── README.md              # This file

```

## Prerequisites
- Docker Desktop for Mac (Apple Silicon)
- Docker Hub account
- Basic understanding of APIs and HTTP requests
- Substitute docker user name in the place of yourusername in below commands 

## Application Architecture
```

+———––+         +——————+         +———––+ 
|   Browser   | ——> |  Frontend (3000) | ——> | Backend API | 
| localhost:  |  HTTP   |  joke-frontend   |  HTTP   |   (5000)    | 
|    3000     | <—— |                  | <—— | backend-api 
| +———––+         +——————+         +———––+ 
|                            | 
+––––––––––––––+ 
joke-network (custom)

```


## Step-by-Step Implementation

### Step 1: Create Project Structure

```bash
cd ~/Documents/devops-bootcamp/class2
mkdir -p assignment-3/backend assignment-3/frontend
cd assignment-3
```

### Step 2: Create Backend API

**backend/app.py**: Flask API that returns random jokes

**backend/requirements.txt**:
```
Flask==3.0.0
```

**backend/Dockerfile**:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
EXPOSE 5000
CMD ["python", "app.py"]
```

### Step 3: Create Frontend App

**frontend/app.py**: Flask app that fetches jokes from backend

**frontend/requirements.txt**:
```
Flask==3.0.0
requests==2.31.0
```

**frontend/Dockerfile**:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
EXPOSE 3000
CMD ["python", "app.py"]
```

### Step 4: Build Docker Images

```bash
# Build backend image
docker build -t yourusername/joke-backend:v1.0 ./backend

# Build frontend image
docker build -t yourusername/joke-frontend:v1.0 ./frontend

# Verify images
docker images | grep joke
```

### Step 5: Create Custom Network

```bash
# Create custom bridge network
docker network create joke-network

# List networks
docker network ls

# Inspect network details
docker network inspect joke-network
```

### Step 6: Run Backend Container

```bash
# Run backend on custom network
docker run -d \
  --name backend-api \
  --network joke-network \
  yourusername/joke-backend:v1.0

# Verify backend is running
docker ps

# Check logs
docker logs backend-api

# Test backend API
docker exec backend-api curl http://localhost:5000/joke
```

**Note**: Backend port 5000 is NOT exposed to host - only accessible within the network.

### Step 7: Run Frontend Container

```bash
# Run frontend on same network
docker run -d \
  --name frontend-app \
  --network joke-network \
  -p 3000:3000 \
  yourusername/joke-frontend:v1.0

# Verify frontend is running
docker ps

# Check logs
docker logs frontend-app
```

### Step 8: Test the Application

Open browser: `http://localhost:3000`

You should see:
- A random programming joke
- Information showing containers are communicating
- Button to get a new joke

**What's happening:**
1. Browser connects to frontend on port 3000
2. Frontend makes HTTP request to `http://backend-api:5000/joke`
3. Docker DNS resolves `backend-api` to the backend container's IP
4. Backend returns a random joke
5. Frontend displays the joke

### Step 9: Verify Network Communication

```bash
# Enter frontend container
docker exec -it frontend-app /bin/bash

# Install curl and ping
apt-get update && apt-get install -y curl iputils-ping

# Ping backend by name
ping backend-api

# Curl backend API
curl http://backend-api:5000/joke

# Exit container
exit
```

### Step 10: Inspect Network

```bash
# View all containers on the network
docker network inspect joke-network

# You'll see both containers with their IP addresses and names
```

### Step 11: Push to Docker Hub

```bash
# Login
docker login

# Push backend
docker push yourusername/joke-backend:v1.0
docker tag yourusername/joke-backend:v1.0 yourusername/joke-backend:latest
docker push yourusername/joke-backend:latest

# Push frontend
docker push yourusername/joke-frontend:v1.0
docker tag yourusername/joke-frontend:v1.0 yourusername/joke-frontend:latest
docker push yourusername/joke-frontend:latest
```

## Docker Hub Links
- Backend: `https://hub.docker.com/r/yourusername/joke-backend`
- Frontend: `https://hub.docker.com/r/yourusername/joke-frontend`

## Testing Commands

```bash
# View running containers
docker ps

# Check backend logs
docker logs backend-api

# Check frontend logs
docker logs frontend-app

# Test backend API directly
curl http://localhost:3000

# View network details
docker network inspect joke-network

# See containers on specific network
docker network inspect joke-network --format '{{range .Containers}}{{.Name}} {{end}}'
```

## How It Works

### Backend API
- Runs on port 5000 (internal only)
- Provides `/joke` endpoint that returns random jokes
- No external port exposure needed

### Frontend App
- Runs on port 3000 (exposed to host)
- Fetches jokes from backend using `http://backend-api:5000/joke`
- Uses container name `backend-api` for service discovery
- Displays jokes in a nice web interface

### Custom Network Magic
- Docker provides DNS resolution on custom networks
- Container name `backend-api` automatically resolves to its IP address
- No hardcoded IPs needed - containers can be recreated and names stay the same
- Isolated from other Docker networks

## Comparison: Default vs Custom Network

### Default Bridge Network
```bash
# Containers must use IP addresses
curl http://172.17.0.2:5000/joke  # IP changes on restart!
```

### Custom Bridge Network
```bash
# Containers use stable names
curl http://backend-api:5000/joke  # Name stays the same!
```

## Troubleshooting

### Frontend can't reach backend
```bash
# Check both containers are on same network
docker network inspect joke-network

# Verify backend is running
docker ps | grep backend

# Check backend logs for errors
docker logs backend-api
```

### Port already in use
```bash
# Use different port for frontend
docker run -d --name frontend-app --network joke-network -p 3001:3000 yourusername/joke-frontend:v1.0
# Access at: http://localhost:3001
```

### Container name conflicts
```bash
# Remove existing containers
docker rm -f backend-api frontend-app

# Then rerun the containers
```

## Cleanup Commands

```bash
# Stop containers
docker stop frontend-app backend-api

# Remove containers
docker rm frontend-app backend-api

# Remove network
docker network rm joke-network

# Remove images (optional)
docker rmi yourusername/joke-backend:v1.0
docker rmi yourusername/joke-frontend:v1.0

# Verify cleanup
docker ps -a
docker network ls
```

## Screenshots
<img width="800" alt="Created networks" src="Screenshots/Networks created.png" />

<img width="800" alt="Created Containers" src="Screenshots/Built_container.png" />

<img width="800" alt="Observing Behaviour" src="Screenshots/pinging.png" />




## Key Takeaways

1. **Custom networks enable name-based communication** - Containers can use friendly names instead of IP addresses
2. **Network isolation** - Only containers on the same network can communicate
3. **Automatic DNS resolution** - Docker handles name-to-IP mapping automatically
4. **Selective port exposure** - Backend doesn't need external port, only frontend does
5. **Microservices architecture** - Separating concerns into independent services

## Real-World Applications

- **Microservices**: Backend API, frontend UI, database all on same network
- **Development environments**: Multiple services communicating locally
- **Service isolation**: Different projects on different networks
- **Load balancing**: Multiple backend containers, one frontend

## Author
Ruthvik

## Date Completed
feb 7, 2025

