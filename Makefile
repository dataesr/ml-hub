CURRENT_VERSION=$(shell cat backend/app/version.py | cut -d \" -f 2)
DOCKER_IMAGE_NAME=dataesr/ml-hub
GHCR_IMAGE_NAME=ghcr.io/$(DOCKER_IMAGE_NAME)


install:
	@echo Installing dependencies...
	pip install -r backend/requirements.txt
	@echo End of dependencies installation

docker-build:
	@echo Building a new docker image
	docker build -t $(GHCR_IMAGE_NAME):$(CURRENT_VERSION) -t $(GHCR_IMAGE_NAME):latest .
	@echo Docker image built

docker-push:
	@echo Pushing a new docker image
	docker push -a $(GHCR_IMAGE_NAME)
	@echo Docker image pushed

release:
	echo 'VERSION = "$(VERSION)"' > backend/app/version.py
	cd frontend && npm version $(VERSION)
	git commit -am '[release] version $(VERSION)'
	git tag v$(VERSION)
	@echo If everything is OK, you can push with tags i.e. git push origin main --tags
