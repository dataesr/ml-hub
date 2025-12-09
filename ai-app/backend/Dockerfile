FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    unzip \
    zip \
    git \
    && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# OVHAI CLI
RUN curl https://cli.gra.ai.cloud.ovh.net/ovhai-linux.zip -o ovhai-linux.zip && \
    unzip ovhai-linux.zip && \
    mkdir -p /bin && \
    mv ovhai /bin/ovhai && \
    export PATH=$PATH:/bin/ && \
    rm -rf ovhai-linux.zip ovhai
RUN mkdir -p ~/.config/ovhai && curl -o ~/.config/ovhai/config.json https://cli.gra.ai.cloud.ovh.net/config.json


COPY ./ai-app/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./ai-core ./ai-core
RUN pip install ./ai-core

COPY ./ai-app/backend .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]