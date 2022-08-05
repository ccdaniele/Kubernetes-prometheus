version := $(shell echo "print(__version__)" | python -i pykube/__init__.py)

:PHONY build-image
build-image:
	@docker build -t aldrickdev/pykube:$(version) .

:PHONY push-image
push-image:
	@docker push aldrickdev/pykube:$(version)
