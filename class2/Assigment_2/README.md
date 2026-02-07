# Assignment 2: Database with Volume

## Overview
This assignment demonstrates Docker volume persistence by running a PostgreSQL database container. You'll create data, delete the container, start a new one, and verify the data still exists.

## Docker Concepts Covered

### Docker Volumes
- **Volume**: Persistent storage managed by Docker that exists independently of containers
- **Data Persistence**: Data stored in volumes survives container deletion and recreation
- **Volume Mounting**: Attaching a volume to a specific path inside the container
- **Stateful Containers**: Running databases that need to persist data across container lifecycles

### Why Volumes?
Without volumes, data stored inside a container is lost when the container is removed. Volumes solve this by storing data on the host machine in a Docker-managed location.

## Project Structure
```
assignment-2/
README.md          # This file (documentation only, no code)

```

## Prerequisites
- Docker Desktop for Mac (Apple Silicon)
- Basic understanding of SQL (optional)

## Step-by-Step Implementation

### Step 1: Create Project Folder

```bash
# Navigate to your class2 directory
cd ~/Documents/devops-bootcamp/class2

# Create assignment-2 folder
mkdir assignment-2
cd assignment-2
```

### Step 2: Create a Named Volume

```bash
# Create a volume named 'pgdata'
docker volume create pgdata

# Verify the volume was created
docker volume ls

# Inspect the volume (see where Docker stores it)
docker volume inspect pgdata
```

**What happened?**
Docker created a persistent storage location on your Mac. This volume will store PostgreSQL data files.

### Step 3: Run PostgreSQL Container with Volume

```bash
# Run PostgreSQL container with volume mounted
docker run -d \
  --name postgres-container \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=admin123 \
  -e POSTGRES_DB=testdb \
  -v pgdata:/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:16-alpine

# Check if container is running
docker ps

# View container logs
docker logs postgres-container
```

**Command Breakdown:**
- `-d`: Run in detached mode (background)
- `--name postgres-container`: Give container a friendly name
- `-e POSTGRES_USER=admin`: Set PostgreSQL username
- `-e POSTGRES_PASSWORD=admin123`: Set PostgreSQL password
- `-e POSTGRES_DB=testdb`: Create initial database
- `-v pgdata:/var/lib/postgresql/data`: Mount volume to PostgreSQL data directory
- `-p 5432:5432`: Map port 5432 on host to 5432 in container
- `postgres:16-alpine`: Use PostgreSQL 16 Alpine image (smaller size)

### Step 4: Connect to PostgreSQL and Create Data

```bash
# Connect to PostgreSQL using psql inside the container
docker exec -it postgres-container psql -U admin -d testdb
```

You'll see a `testdb=#` prompt. Now run these SQL commands:

```sql
-- Create a table
CREATE TABLE favorite_movies (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    year INT,
    rating DECIMAL(3,1)
);

-- Insert data
INSERT INTO favorite_movies (title, year, rating) VALUES
('Inception', 2010, 8.8),
('Interstellar', 2014, 8.7),
('The Dark Knight', 2008, 9.0),
('The Matrix', 1999, 8.7),
('Pulp Fiction', 1994, 8.9);

-- Verify data was inserted
SELECT * FROM favorite_movies;

-- Check row count
SELECT COUNT(*) FROM favorite_movies;

-- Exit psql
\q
```

**What you should see:**
A table showing 5 movies with their details.

### Step 5: Delete the Container

```bash
# Stop the container
docker stop postgres-container

# Remove the container completely
docker rm postgres-container

# Verify container is gone
docker ps -a

# Verify volume still exists
docker volume ls
```

**Important:** The container is deleted, but the volume `pgdata` remains!

### Step 6: Start New Container with Same Volume

```bash
# Run a NEW PostgreSQL container with the SAME volume
docker run -d \
  --name postgres-container-new \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=admin123 \
  -e POSTGRES_DB=testdb \
  -v pgdata:/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:16-alpine

# Check new container is running
docker ps
```

**Note:** This is a completely NEW container, but it's using the SAME volume.

### Step 7: Verify Data Still Exists

```bash
# Connect to the NEW container
docker exec -it postgres-container-new psql -U admin -d testdb
```

In psql, run:

```sql
-- Check if table exists
\dt

-- Query the data
SELECT * FROM favorite_movies;

-- Verify count
SELECT COUNT(*) FROM favorite_movies;

-- Exit
\q
```

**Success!** ðŸŽ‰ If you see all 5 movies, volume persistence works!

## What Just Happened?

1. **Volume Created**: Docker created persistent storage separate from containers
2. **First Container**: PostgreSQL stored data in the volume
3. **Container Deleted**: Container removed, but volume remained intact
4. **Second Container**: New container attached to same volume
5. **Data Persisted**: New container could read data written by old container

## Key Takeaways

- Containers are **ephemeral** (temporary), but volumes are **persistent**
- Multiple containers can use the same volume (not simultaneously for databases)
- Volumes are stored on the host machine, managed by Docker
- Perfect for databases, configuration files, and any data that needs to survive container restarts

## Cleanup Commands

```bash
# Stop and remove container
docker stop postgres-container-new
docker rm postgres-container-new

# Remove the volume (WARNING: deletes all data)
docker volume rm pgdata

# Verify everything is cleaned up
docker ps -a
docker volume ls
```

## Useful Commands Reference

```bash
# List all volumes
docker volume ls

# Inspect a volume
docker volume inspect pgdata

# Remove unused volumes
docker volume prune

# View volume usage
docker system df -v

# Connect to PostgreSQL from host (if you have psql installed)
psql -h localhost -p 5432 -U admin -d testdb

# Execute SQL from command line
docker exec -it postgres-container-new psql -U admin -d testdb -c "SELECT * FROM favorite_movies;"

# View PostgreSQL logs
docker logs postgres-container-new

# Follow logs in real-time
docker logs -f postgres-container-new
```

## Troubleshooting

## Screenshots
<img width="800" alt="Created DB with data" src="Screenshots/Screenshot 2026-02-07 005607.png" />
<img width="800" alt="Viewing DB with data" src="Screenshots/Screenshot after png" />


### Container won't start
```bash
# Check if port 5432 is already in use
lsof -i :5432

# Use different port
docker run -d ... -p 5433:5432 ...
```

### Can't connect to database
```bash
# Check container logs
docker logs postgres-container-new

# Verify container is running
docker ps
```

### Data not persisting
```bash
# Verify volume is mounted correctly
docker inspect postgres-container-new | grep -A 10 Mounts

# Check volume exists
docker volume ls
```

## Comparison: With vs Without Volume

### Without Volume (Bad)
```bash
docker run -d --name pg-temp postgres:16-alpine
# Data stored inside container â†’ Lost when container is removed
```

### With Volume (Good)
```bash
docker run -d --name pg-persist -v pgdata:/var/lib/postgresql/data postgres:16-alpine
# Data stored in volume â†’ Persists even after container removal
```

## Real-World Use Cases

- **Development databases**: Keep data between Docker restarts
- **Database backups**: Volume data can be backed up separately
- **Container updates**: Upgrade PostgreSQL version without losing data
- **Disaster recovery**: Restore data by mounting volume to new container

## Author
Ruthvik

## Date Completed
December 18, 2025

