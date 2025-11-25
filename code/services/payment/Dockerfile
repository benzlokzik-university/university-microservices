FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    protobuf-compiler \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml ./

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Copy application code
COPY . .

# Generate gRPC code from proto files (if needed)
# RUN python -m grpc_tools.protoc -I./proto --python_out=. --grpc_python_out=. ./proto/payment.proto

# Expose ports (HTTP and gRPC)
EXPOSE 8004 50051

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8004"]

