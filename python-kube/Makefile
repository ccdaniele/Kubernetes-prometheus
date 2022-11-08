
version := $(shell echo "print(__version__)" | python -i pykube/pykube/__init__.py)

:PHONY bi
bi:
	@docker build -t aldrickdev/pykube:$(version) -f docker/Dockerfile .

:PHONY pi
pi:
	@docker push aldrickdev/pykube:$(version)

:PHONY di
di:
	@docker rmi $(shell docker images aldrickdev/pykube --format {{.ID}})

:PHONY dup
dup:
	@docker compose -f docker/compose.yaml up
