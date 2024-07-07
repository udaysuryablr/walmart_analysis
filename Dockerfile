# Use the official Python image from the Docker Hub
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port that the app runs on
EXPOSE 8080

# Define environment variable
ENV NAME MLOpsProject

# Run the gunicorn server when the container launches
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "main:server"]
