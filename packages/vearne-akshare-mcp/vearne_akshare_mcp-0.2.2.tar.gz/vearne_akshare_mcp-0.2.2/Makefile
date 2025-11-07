VERSION := v0.2.1

COMMAND_NAME = akshare-mcp

BUILD_COMMIT ?= $(shell git rev-parse --short=4 HEAD)
BUILD_TIME ?= $(shell date +%Y%m%d%H%M%S)

DOCKER_TAG := $(VERSION)-$(BUILD_TIME)-$(BUILD_COMMIT)
IMAGE_NAME = woshiaotian/$(COMMAND_NAME):$(DOCKER_TAG)


.PHONY: clean
clean:
	rm -rf ./dist

.PHONY: build
build: clean
	python3 -m build

.PHONY: upload
upload: build
	#python3 -m twine upload --repository testpypi dist/*
	python3 -m twine upload dist/*

.PHONY: image
image:
	docker build --rm \
		-f ./Dockerfile  \
		-t $(IMAGE_NAME) .
	docker push $(IMAGE_NAME)