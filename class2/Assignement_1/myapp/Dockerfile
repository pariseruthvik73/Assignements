# Start with Python already installed
FROM python:3.8-slim

# Make a folder for our app
WORKDIR /app

# Copy our files
COPY requirements.txt .
COPY app.py .

# Install Flask
RUN pip install -r requirements.txt

# Tell Docker our app uses port 5000
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]