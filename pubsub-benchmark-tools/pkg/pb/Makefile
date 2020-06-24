all: compile

compile: clean
	@protoc -I publisher/ publisher.proto --go_out=plugins=grpc:publisher

clean:
	@rm -f ./publisher/*.pb.go
	@rm -f ./publisher/*.go
