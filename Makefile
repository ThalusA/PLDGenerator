.PHONY: build release

build:
	docker build -t pld .

release: build
		mkdir -p build
		docker run -it --name pld-instance --volume ${PWD}/assets:/pld/assets:Z pld
		docker cp pld-instance:/pld/build ./build
		docker rm -f pld-instance
