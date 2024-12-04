# Use an official Python image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    g++ \
    build-essential \
    python3-dev \
    libffi-dev

ENV FLASK_ENV=production
ENV FLASK_DEBUG=0

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project files
COPY . .

# Expose the application port
EXPOSE 5000

# Command to run the application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "run:app"]
