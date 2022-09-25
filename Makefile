.PHONY: build release

build:
	docker build -t pld .

release: build
		mkdir -p build
		docker rm -f pld-instance
		docker run --name pld-instance --volume ${PWD}/assets:/pld/assets:Z pld
		docker cp pld-instance:/pld/build ./
		docker rm -f pld-instance
