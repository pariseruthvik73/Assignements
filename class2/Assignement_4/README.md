# Assignment 4: Network Comparison

## Overview
This assignment compares three different Docker networking modes by running the same application on each network type and documenting the differences in behavior, access patterns, and performance.

## Docker Concepts Covered

### Network Types
- **Default Bridge Network**: Docker's default network where containers get isolated IPs but no automatic DNS resolution
- **Host Network**: Container shares the host's network stack directly (limited on macOS)
- **Custom Bridge Network**: User-defined network with automatic DNS resolution and better isolation

### Key Concepts
- **Network Isolation**: How containers are separated from each other and the host
- **DNS Resolution**: Automatic name-to-IP resolution on custom networks
- **Port Mapping**: Differences in how ports are exposed across network modes
- **Performance**: Network overhead and latency differences
- **Container Communication**: How containers find and talk to each other

## Project Structure
```
assignment-4/
  app.py              # Flask app showing network info
  requirements.txt    # Python dependencies
  Dockerfile          # Docker image definition
  .dockerignore       # Exclude files
  README.md          # This file
```

## Prerequisites
- Docker Desktop for Mac (Apple Silicon)
- Docker Hub account
- Basic understanding of networking concepts
- Replace yourusername with docker account name

## Application Overview

The test application is a simple Flask web app that displays:
- Container hostname
- Container IP address
- Network mode it's running on
- Visual interface to compare networking modes

## Step-by-Step Implementation

### Step 1: Create Project Structure

```bash
cd ~/Documents/devops-bootcamp/class2
mkdir assignment-4
cd assignment-4
```

### Step 2: Create Test Application Files

**app.py**: Flask application that displays network information

**requirements.txt**:
```
Flask==3.0.0
```

**Dockerfile**:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
EXPOSE 5000
CMD ["python", "app.py"]
```

**`.dockerignore`**:
```
__pycache__
*.pyc
*.pyo
*.pyd
.Python
```

### Step 3: Build Docker Image

```bash
# Build the image
docker build -t yourusername/network-test:v1.0 .

# Verify
docker images | grep network-test
```

---

## Test 1: Default Bridge Network

### Step 4: Run on Default Bridge

```bash
# Run container on default bridge network
docker run -d \
  --name test-bridge-default \
  -e NETWORK_MODE="Default Bridge" \
  -p 8081:5000 \
  yourusername/network-test:v1.0

# Verify running
docker ps

# Check logs
docker logs test-bridge-default
```

### Step 5: Test Default Bridge Access

```bash
# Access the application
open http://localhost:8081

# Get container IP
docker inspect test-bridge-default --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}'

# Get full network info
docker inspect test-bridge-default | grep -A 20 NetworkSettings
```

### Observations - Default Bridge

**Access Method:**
- URL: `http://localhost:8081`
- Port mapping: Required (`-p 8081:5000`)
- Direct IP access: Not available from host on Mac

**Characteristics:**
- Container gets IP in Docker's default bridge subnet (usually 172.17.0.x)
- No automatic DNS resolution between containers
- Containers must use IP addresses to communicate
- Port mapping required for external access

### Step 6: Test Container-to-Container (Default Bridge)

```bash
# Run second container
docker run -d \
  --name test-bridge-default-2 \
  -p 8082:5000 \
  yourusername/network-test:v1.0

# Try to ping by name (FAILS - no DNS)
docker exec test-bridge-default ping -c 2 test-bridge-default-2

# Get IP of second container
CONTAINER2_IP=$(docker inspect test-bridge-default-2 --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}')
echo $CONTAINER2_IP

# Ping by IP (WORKS)
docker exec test-bridge-default ping -c 2 $CONTAINER2_IP
```

**Key Finding:** Default bridge requires IP addresses for communication, not names.

### Step 7: Cleanup Default Bridge

```bash
docker stop test-bridge-default test-bridge-default-2
docker rm test-bridge-default test-bridge-default-2
```

---

## Test 2: Host Network

### Step 8: Run on Host Network

**Important Note for Mac Users:**
Docker on macOS runs in a VM, so host networking doesn't work the same as on Linux. On Linux, `--network host` means the container uses the host's network directly. On Mac, it still runs in the Docker VM's network namespace.

```bash
# Run container with host network
docker run -d \
  --name test-host \
  --network host \
  -e NETWORK_MODE="Host Network" \
  yourusername/network-test:v1.0

# Check status
docker ps

# View logs
docker logs test-host
```

### Step 9: Test Host Network Access

```bash
# On Linux: Access directly at port 5000
# On Mac: Behavior differs due to Docker VM

# Try to access
curl http://localhost:5000

# Check network configuration
docker exec test-host hostname
docker exec test-host hostname -i
```

### Observations - Host Network

**On Linux:**
- No port mapping needed
- Container shares host's network stack
- Fastest performance (no network overhead)
- Less isolation (security consideration)
- Port conflicts possible with host services

**On macOS:**
- Host networking is not fully supported
- Container still isolated in Docker VM
- Behavior similar to bridge mode
- Limited usefulness for development on Mac

### Step 10: Cleanup Host Network

```bash
docker stop test-host
docker rm test-host
```

---

## Test 3: Custom Bridge Network

### Step 11: Create Custom Network

```bash
# Create custom bridge network
docker network create test-network

# Verify creation
docker network ls

# Inspect network details
docker network inspect test-network
```

### Step 12: Run on Custom Bridge

```bash
# Run container on custom network
docker run -d \
  --name test-custom-bridge \
  --network test-network \
  -e NETWORK_MODE="Custom Bridge" \
  -p 8083:5000 \
  yourusername/network-test:v1.0

# Verify running
docker ps

# Check logs
docker logs test-custom-bridge
```

### Step 13: Test Custom Bridge Access

```bash
# Access the application
open http://localhost:8083

# Get container IP on custom network
docker inspect test-custom-bridge --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}'

# Inspect network to see connected containers
docker network inspect test-network
```

### Step 14: Test DNS Resolution (Custom Bridge)

```bash
# Run second container on same custom network
docker run -d \
  --name test-custom-bridge-2 \
  --network test-network \
  -e NETWORK_MODE="Custom Bridge 2" \
  -p 8084:5000 \
  yourusername/network-test:v1.0

# Ping by NAME (WORKS - DNS enabled!)
docker exec test-custom-bridge ping -c 3 test-custom-bridge-2

# Install curl and test HTTP by name
docker exec test-custom-bridge sh -c "apt-get update -qq && apt-get install -y -qq curl"
docker exec test-custom-bridge curl http://test-custom-bridge-2:5000/info
```

### Observations - Custom Bridge

**Access Method:**
- URL: `http://localhost:8083`
- Port mapping: Required (`-p 8083:5000`)
- Container-to-container: Use container names (DNS enabled)

**Characteristics:**
- Automatic DNS resolution between containers
- Better isolation than default bridge
- Containers on different custom networks cannot communicate
- Recommended for multi-container applications
- No IP address management needed

### Step 15: Cleanup Custom Bridge

```bash
docker stop test-custom-bridge test-custom-bridge-2
docker rm test-custom-bridge test-custom-bridge-2
docker network rm test-network
```

---

## Network Comparison Table

| Feature | Default Bridge | Host Network | Custom Bridge |
|---------|---------------|--------------|---------------|
| **DNS Resolution** | No (use IPs) | N/A | Yes (use names) |
| **Port Mapping** | Required | Not needed (Linux) | Required |
| **Isolation** | Medium | None | High |
| **Performance** | Good | Best (Linux) | Good |
| **Container Communication** | By IP only | N/A | By name or IP |
| **Use Case** | Simple single containers | High performance (Linux) | Multi-container apps |
| **Security** | Moderate | Low (shares host) | High (isolated) |
| **macOS Support** | Full | Limited | Full |
| **Recommended** | No (use custom) | Only for special cases | Yes |

## Access Pattern Differences

### Default Bridge
```bash
# Must use port mapping
docker run -p 8080:5000 myapp
# Access: http://localhost:8080

# Container-to-container: Must use IP
docker exec container1 curl http://172.17.0.3:5000
```

### Host Network (Linux)
```bash
# No port mapping needed
docker run --network host myapp
# Access: http://localhost:5000

# Note: Only one container can use a port
```

### Custom Bridge
```bash
# Must use port mapping
docker run --network mynet -p 8080:5000 myapp
# Access: http://localhost:8080

# Container-to-container: Use names
docker exec container1 curl http://container2:5000
```

## Performance Testing (Optional)

```bash
# Create custom network
docker network create perf-network

# Run on default bridge
docker run -d --name perf-default -p 9001:5000 yourusername/network-test:v1.0

# Run on custom bridge
docker run -d --name perf-custom --network perf-network -p 9002:5000 yourusername/network-test:v1.0

# Test response times (run 10 times)
for i in {1..10}; do time curl -s http://localhost:9001/info > /dev/null; done
for i in {1..10}; do time curl -s http://localhost:9002/info > /dev/null; done

# Cleanup
docker stop perf-default perf-custom
docker rm perf-default perf-custom
docker network rm perf-network
```

**Expected Results:**
- Performance difference is minimal for most applications
- Host network (on Linux) has lowest latency
- Custom and default bridge have similar performance

## Push to Docker Hub

```bash
# Login
docker login

# Push image
docker push yourusername/network-test:v1.0

# Tag as latest
docker tag yourusername/network-test:v1.0 yourusername/network-test:latest
docker push yourusername/network-test:latest
```

## Docker Hub Link
`https://hub.docker.com/r/yourusername/network-test`

## Useful Commands

```bash
# List all networks
docker network ls

# Inspect a network
docker network inspect <network-name>

# See which containers are on a network
docker network inspect <network-name> --format '{{range .Containers}}{{.Name}} {{end}}'

# Connect running container to a network
docker network connect <network-name> <container-name>

# Disconnect container from network
docker network disconnect <network-name> <container-name>

# Remove all unused networks
docker network prune

# Check container's network settings
docker inspect <container> | grep -A 30 NetworkSettings
```

## Troubleshooting

### Port Already in Use
```bash
# Check what's using the port
lsof -i :8081

# Use a different port
docker run -p 8085:5000 myapp
```

### Cannot Reach Container by Name
```bash
# Verify both containers are on the same custom network
docker network inspect <network-name>

# Default bridge doesn't support DNS - use custom network instead
```

### Host Network Not Working on Mac
```bash
# This is expected - host networking has limited support on macOS
# Use bridge networks instead for Mac development
```

## Key Takeaways

1. **Default Bridge**: Legacy mode, requires IPs for communication, not recommended
2. **Host Network**: Best performance on Linux but no isolation, limited on Mac
3. **Custom Bridge**: Recommended for all multi-container apps, automatic DNS, good isolation
4. **DNS Resolution**: Only works on custom networks, huge advantage
5. **Port Mapping**: Required for bridge networks, not needed for host (on Linux)
6. **Security**: Custom networks provide best balance of isolation and functionality

## Real-World Applications

- **Development**: Custom networks for local multi-container apps
- **Microservices**: Each service on same custom network, communicate by name
- **Production**: Custom networks with proper isolation between services
- **Performance-critical**: Host networking on Linux for minimal overhead
- **Security**: Use custom networks to isolate different application stacks

## Best Practices

1. Use **custom bridge networks** for multi-container applications
2. Avoid default bridge - it lacks DNS resolution
3. Use host network only when performance is critical (Linux only)
4. Name your networks descriptively (e.g., `myapp-network`, `db-network`)
5. Use network isolation to separate different environments
6. Document which containers need to communicate

## Cleanup All Resources

```bash
# Stop all test containers
docker stop $(docker ps -aq --filter "name=test-")

# Remove all test containers
docker rm $(docker ps -aq --filter "name=test-")

# Remove test networks
docker network prune

# Remove test images (optional)
docker rmi yourusername/network-test:v1.0
```

## Author
Ruthvik

## Date Completed
Feb 7, 2026

