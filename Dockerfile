# Docker image for sandbox execution
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /workspace

# Install common Python tools for testing
RUN pip install pytest black ruff mypy

# Copy requirements and install dependencies
COPY requirements-sandbox.txt .
RUN pip install -r requirements-sandbox.txt

# Set up git config (required for some operations)
RUN git config --global user.name "DevAgent Sandbox" && \
    git config --global user.email "devagent@localhost"

# Entry point for sandbox execution
CMD ["python", "-c", "print('DevAgent sandbox ready')"]