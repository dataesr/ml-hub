CURRENT_VERSION=$(shell cat backend/app/version.py | cut -d \" -f 2)
DOCKER_FILE_MLFLOW=Dockerfile_mlflow
DOCKER_IMAGE_NAME=dataesr/ml-hub
DOCKER_IMAGE_NAME_MLFLOW=dataesr/mlflow
GHCR_IMAGE_NAME=ghcr.io/$(DOCKER_IMAGE_NAME)
GHCR_IMAGE_NAME_MLFLOW=ghcr.io/$(DOCKER_IMAGE_NAME_MLFLOW)

install:
	@echo Installing dependencies...
	pip install -r backend/requirements.txt
	@echo End of dependencies installation

docker-build:
	@echo Building a new docker image
	docker build -t $(GHCR_IMAGE_NAME):staging .
	@echo Docker image built

docker-build-prod:
	@echo Building a new docker image
	docker build -t $(GHCR_IMAGE_NAME):$(CURRENT_VERSION) -t $(GHCR_IMAGE_NAME):latest .
	@echo Docker image built

docker-push:
	@echo Pushing a new docker image
	docker push -a $(GHCR_IMAGE_NAME)
	@echo Docker image pushed


docker-build-mlflow:
	@echo Building a new docker image
	docker build -f $(DOCKER_FILE_MLFLOW) -t $(GHCR_IMAGE_NAME_MLFLOW):latest .
	@echo Docker image built

docker-push-mlflow:
	@echo Pushin a new docker image
	docker push $(GHCR_IMAGE_NAME_MLFLOW):latest
	@echo Docker image pushed

release:
	echo 'VERSION = "$(VERSION)"' > backend/app/version.py
	cd frontend && npm version $(VERSION)
	git commit -am '[release] version $(VERSION)'
	git tag v$(VERSION)
	@echo If everything is OK, you can push with tags i.e. git push origin main --tags
