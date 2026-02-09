FROM python:3.12-slim

WORKDIR /app

# Set environment variable so app.py knows it's in a container
ENV DOCKER_CONTAINER=true

# Copy dependencies and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files
COPY . .

# Create directory for the Docker Volume mount
RUN mkdir -p /app/data

EXPOSE 5000

CMD ["python", "app.py"]