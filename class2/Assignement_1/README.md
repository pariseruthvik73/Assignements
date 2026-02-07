# Assignment 1: Build a Web App

## Overview
A simple Flask web application containerized with Docker that displays personal information and favorite movies.

## Docker Concepts Covered
- **Docker Image**: Read-only template with application and dependencies
- **Dockerfile**: Instructions to build the Docker image
- **Docker Container**: Running instance of the image
- **Docker Build**: Process of creating an image
- **Docker Hub**: Registry for storing and sharing Docker images
- **Port Mapping**: Exposing container services to host machine

## Project Structure
```
assignment-1/
 ├── app.py              # Flask application
├── requirements.txt    # Python dependencies
 ├── Dockerfile          # Docker build instructions
├── .dockerignore       # Files to exclude from Docker build
 └── README.md          # This file

```

## Prerequisites
- Docker Desktop for Mac (Apple Silicon)
- Docker Hub account
- Python 3.9+ (for local testing only)
- substitute your docker hub username in places of 'yourusername'

## Building the Image

```bash
# Build the Docker image
docker build -t yourusername/flask-webapp:v1.0 .

# Verify image creation
docker images | grep flask-webapp
```

## Running the Container

```bash
# Run the container
docker run -d -p 8080:5000 --name flask-app yourusername/flask-webapp:v1.0

# Check container status
docker ps

# View application logs
docker logs flask-app

# Access the application at: http://localhost:8080
```

## Pushing to Docker Hub

```bash
# Login to Docker Hub
docker login

# Push the image
docker push yourusername/flask-webapp:v1.0

# Tag as latest and push
docker tag yourusername/flask-webapp:v1.0 yourusername/flask-webapp:latest
docker push yourusername/flask-webapp:latest
```

## Docker Hub Link
`https://hub.docker.com/r/yourusername/flask-webapp`

## Useful Commands

```bash
# Stop the container
docker stop flask-app

# Remove the container
docker rm flask-app

# Remove the image
docker rmi yourusername/flask-webapp:v1.0

# View container logs in real-time
docker logs -f flask-app

# Execute commands inside running container
docker exec -it flask-app /bin/bash
```

## How It Works

1. **Dockerfile** defines the build process:
   - Starts with Python 3.9 slim base image
   - Sets /app as working directory
   - Installs Flask from requirements.txt
   - Copies application code
   - Exposes port 5000
   - Runs the Flask application

2. **Docker builds** the image layer by layer, creating an immutable snapshot

3. **Docker runs** a container from the image, mapping port 8080 (host) to 5000 (container)

4. **Flask serves** the web application inside the container, accessible from host machine

## Testing

After running the container, visit `http://localhost:8080` to see:
- Your name
- Current date and time
- List of favorite movies

## Screenshots
<img width="800" alt="Docker Success" src="Screenshots/Screenshot 2026-02-06 232447.png" />
<img width="800" alt="App Dashboard" src="Screenshots/image.png" />


## Author
[Ruthvik]

## Date Completed
December 18, 2025




