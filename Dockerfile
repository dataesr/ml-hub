### Frontend
FROM node:20-alpine AS frontend-build
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build --omit:dev

### Backend
FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    unzip \
    zip \
    && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# OVH cli
RUN curl https://cli.gra.ai.cloud.ovh.net/ovhai-linux.zip -o ovhai-linux.zip && \
    unzip ovhai-linux.zip && \
    mkdir -p /bin && \
    mv ovhai /bin/ovhai && \
    export PATH=$PATH:/bin/ && \
    rm -rf ovhai-linux.zip ovhai
RUN mkdir -p ~/.config/ovhai && curl -o ~/.config/ovhai/config.json https://cli.gra.ai.cloud.ovh.net/config.json

COPY backend/requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
COPY backend/ .

# Copy built frontend into /app/static
COPY --from=frontend-build /frontend/dist /app/static

ENV STATIC_DIR=/app/static

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]


