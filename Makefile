.PHONY: clean build run

clean:
	rm -rf ./build

build: clean
	briefcase build android

run: build
	briefcase run android -d 346911ae
