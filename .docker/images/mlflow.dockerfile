# official MLflow image
FROM ghcr.io/mlflow/mlflow:v3.6.0

# Install git
RUN apt-get update && \
  apt-get install -y --no-install-recommends \
  git && \
  rm -rf /var/lib/apt/lists/*

# Install mlflow dependencies
RUN pip install --no-cache-dir "mlflow[extras]==3.6.0"