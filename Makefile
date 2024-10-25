APP_NAME=botman

build:
	go mod tidy
	go clean
	go build -o bin/$(APP_NAME) main.go

run: build
	./bin/$(APP_NAME)

clean:
	rm -rf bin

.PHONY: build run clean
