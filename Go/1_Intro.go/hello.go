package main	//package

import "fmt"	//module

func main(){	//entry point function (should always be main())
	fmt.Print("Hello World")
}

// To RUN: go run .hello.go
// To Initialize this new module with a specific module path.: go mod init @example/hello-world
// To BUILD: go build