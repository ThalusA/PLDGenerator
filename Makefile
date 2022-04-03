.PHONY: build release

build:
	docker build -t pld .

release: build
		mkdir -p build
		docker run --it --name pld-instance -v "$PWD/assets":/pld/assets pld
		docker cp pld-instance:/pld/build ./build
		docker rm -f pld-instance
