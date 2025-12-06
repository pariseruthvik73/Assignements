# Docker Network and Volume Hands-On Lab

## Prerequisites
- Docker Desktop installed on your machine (Windows/Mac/Linux)
- Basic command line knowledge

---

## Part 1: Docker Networks

### 1.1 View Available Networks
```bash
docker network ls
```

You'll see default networks: `bridge`, `host`, and `none`.

### 1.2 Inspect a Container's Network
```bash
# Run a container
docker run -d --name test-container nginx

# Inspect its network configuration
docker inspect test-container

# Look for the "Networks" section - it shows bridge network by default
```

### 1.3 Run Container with Host Network
```bash
# Remove previous container
docker rm -f test-container

# Run with host network (no port mapping needed)
docker run -d --network host --name nginx-host nginx
```

### 1.4 Create Two Containers on Default Bridge Network
```bash
# Create container 1
docker run -d --name con1 busybox sleep 3600

# Create container 2
docker run -d --name con2 busybox sleep 3600

# Get IP addresses
docker inspect con1 | grep IPAddress
docker inspect con2 | grep IPAddress

# Login to con1 and try to ping con2 by IP (this works)
docker exec -it con1 sh
# Inside container: ping <con2-IP>
# Inside container: ping con2  (this will FAIL - cannot resolve by name)
exit
```

**Key Learning**: Default bridge network allows IP-based communication but NOT name-based.

### 1.5 Create Custom Network
```bash
# Create a custom network
docker network create demo-network

# Verify it was created
docker network ls

# Remove old containers
docker rm -f con1 con2

# Create containers using custom network
docker run -d --name c1 --network demo-network busybox sleep 3600
docker run -d --name c2 --network demo-network busybox sleep 3600

# Login to c1 and ping c2 by NAME (this works!)
docker exec -it c1 sh
# Inside container: ping c2  (SUCCESS!)
# Inside container: nslookup c2  (DNS resolution works!)
exit
```

**Key Learning**: Custom networks provide automatic DNS resolution between containers.

### 1.6 Test Network Isolation
```bash
# Create a second network
docker network create network-two

# Create containers on different networks
docker run -d --name app1 --network demo-network busybox sleep 3600
docker run -d --name app2 --network network-two busybox sleep 3600

# Try to ping app2 from app1 (this will FAIL - network isolation)
docker exec -it app1 sh
# Inside container: ping app2  (FAILS - different networks)
exit
```

**Key Learning**: Containers on different networks cannot communicate (isolation).

---

## Part 2: Docker Volumes

### 2.1 Container Without Volume (Data Loss Demo)
```bash
# Run a container
docker run -d --name c1 busybox sleep 3600

# Create a log file inside
docker exec -it c1 sh
# Inside container:
touch log.txt
echo "log line one" > log.txt
cat log.txt
exit

# Remove the container
docker rm -f c1

# Create new container with same name
docker run -d --name c1 busybox sleep 3600

# Try to find the log file (it's GONE!)
docker exec -it c1 sh
# Inside container:
ls
cat log.txt  # File does not exist
exit
```

**Key Learning**: Data inside containers is lost when containers are deleted.

### 2.2 Using Bind Mount (Host Path)
```bash
# Create a directory on your host
mkdir docker-data
cd docker-data
echo "some config data" > config1.txt

# Run container with bind mount
docker run -d --name c1 -v $(pwd):/app busybox sleep 3600

# Verify the mount
docker exec -it c1 sh
# Inside container:
cd /app
ls  # You'll see config1.txt
cat config1.txt
# Create a log file
echo "logs from C1" > log-c1.txt
exit

# Create another container with same mount
docker run -d --name c2 -v $(pwd):/app busybox sleep 3600

# Both containers share the same data
docker exec -it c2 sh
# Inside container:
cd /app
ls  # You'll see both config1.txt and log-c1.txt
echo "logs from C2" >> log-c1.txt
cat log-c1.txt  # See logs from both containers
exit

# Delete both containers
docker rm -f c1 c2

# Data persists on host
ls  # Files still exist in your docker-data directory
```

### 2.3 Using Docker Volumes
```bash
# Create a named volume
docker volume create vol1

# List volumes
docker volume ls

# Create container using the volume
docker run -d --name c3 -v vol1:/app-data busybox sleep 3600

# Add data to the volume
docker exec -it c3 sh
# Inside container:
cd /app-data
echo "data in volume" > data.txt
exit

# Remove container
docker rm -f c3

# Create new container with same volume
docker run -d --name c4 -v vol1:/app-data busybox sleep 3600

# Data persists!
docker exec -it c4 sh
# Inside container:
cd /app-data
ls
cat data.txt  # Data is still there!
exit
```

### 2.4 Remove Volume (Data Loss)
```bash
# Stop and remove container
docker rm -f c4

# Remove the volume
docker volume rm vol1

# Create new container with same volume name
docker volume create vol1
docker run -d --name c5 -v vol1:/app-data busybox sleep 3600

# Data is gone
docker exec -it c5 sh
# Inside container:
cd /app-data
ls  # Empty directory
exit
```

---

## Part 3: Cleanup Commands

```bash
# Remove all containers
docker rm -f $(docker ps -aq)

# Remove all custom networks
docker network prune

# Remove all volumes
docker volume prune

# Remove all images (optional)
docker rmi $(docker images -q)
```

---

## Troubleshooting Tips

### Check which process is using a port:
```bash
# On Mac/Linux
lsof -i :5000

# Kill the process
kill -9 <PID>
```

### View container logs:
```bash
docker logs <container-name>
```

### Check container details:
```bash
docker inspect <container-name>
```

---

## Key Takeaways

1. **Default Bridge Network**: Containers can communicate by IP only, not by name
2. **Custom Networks**: Enable DNS resolution - containers can ping each other by name
3. **Network Isolation**: Containers on different networks cannot communicate
4. **Volumes**: Persist data even when containers are deleted
5. **Bind Mounts**: Share host directories with containers
6. **Always create custom networks** in real-world scenarios for proper DNS resolution

---

## Real-World Use Case

In production:
- Create separate networks for different applications (isolation)
- Use volumes to persist database data
- Mount configuration files using bind mounts
- Never use default bridge network for multi-container apps
