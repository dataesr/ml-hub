# =============================================================================
# Configuration
# =============================================================================
CURRENT_VERSION=$(shell cat backend/app/version.py | cut -d \" -f 2)
DOCKER_IMAGE_NAME=dataesr/ml-hub
GHCR_IMAGE_NAME=ghcr.io/$(DOCKER_IMAGE_NAME)

# Docker images directory
IMAGES_DIR=docker/images
ALL_IMAGES=$(shell ls $(IMAGES_DIR)/*.dockerfile 2>/dev/null | xargs -n1 basename | sed 's/.dockerfile//')

# =============================================================================
# Single Image Targets (use: make build img=cuda-base)
# =============================================================================
build:
ifndef img
	$(error Usage: make build img=<image-name>. Available images: $(ALL_IMAGES))
endif
	@echo "Building image: $(img)"
	docker build -f $(IMAGES_DIR)/$(img).dockerfile -t $(GHCR_IMAGE_NAME)/$(img):latest .
	@echo "Image $(img) built successfully"

push:
ifndef img
	$(error Usage: make push img=<image-name>. Available images: $(ALL_IMAGES))
endif
	@echo "Pushing image: $(img)"
	docker push $(GHCR_IMAGE_NAME)/$(img):latest
	@echo "Image $(img) pushed successfully"

build-push:
ifndef img
	$(error Usage: make build-push img=<image-name>. Available images: $(ALL_IMAGES))
endif
	@"$(MAKE)" build img=$(img)
	@"$(MAKE)" push img=$(img)

# =============================================================================
# All Images Targets
# =============================================================================
build-all:
	@echo "Building all images: $(ALL_IMAGES)"
	@for image in $(ALL_IMAGES); do \
		"$(MAKE)" build img=$$image || exit 1; \
	done
	@echo "All images built successfully"

push-all:
	@echo "Pushing all images: $(ALL_IMAGES)"
	@for image in $(ALL_IMAGES); do \
		"$(MAKE)" push img=$$image || exit 1; \
	done
	@echo "All images pushed successfully"

build-push-all:
	@echo "Building and pushing all images: $(ALL_IMAGES)"
	@for image in $(ALL_IMAGES); do \
		"$(MAKE)" build-push img=$$image || exit 1; \
	done
	@echo "All images built and pushed successfully"

# =============================================================================
# Main App Targets
# =============================================================================
build-app-staging:
	@echo "Building app staging image"
	docker build -f app/dockerfile -t $(GHCR_IMAGE_NAME):staging .
	@echo "App image built"

build-app-prod:
	@echo "Building app prod image"
	docker build -f app/dockerfile -t $(GHCR_IMAGE_NAME):$(CURRENT_VERSION) -t $(GHCR_IMAGE_NAME):latest .
	@echo "App image built"

push-app:
	@echo "Pushing app image"
	docker push -a $(GHCR_IMAGE_NAME)
	@echo "App image pushed"

build-push-app-staging:
	@"$(MAKE)" build-app-staging
	@"$(MAKE)" push-app

build-push-app-prod:
	@"$(MAKE)" build-app-prod
	@"$(MAKE)" push-app

# =============================================================================
# Release
# =============================================================================
release:
	echo 'VERSION = "$(VERSION)"' > backend/app/version.py
	cd frontend && npm version $(VERSION)
	git commit -am '[release] version $(VERSION)'
	git tag v$(VERSION)
	@echo "If everything is OK, you can push with tags i.e. git push origin main --tags"

# =============================================================================
# Development
# =============================================================================
dev:
	@./scripts/bootstrap.sh

typecheck:
	@source .venv/bin/activate && ty check
