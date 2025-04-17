/** Go is a fast, statically typed, compiled language known for its simplicity and efficiency. Developed at Google by Robert Griesemer, Rob Pike, and Ken Thompson in 2007. Go's syntax is similar to C++
 */

// 🐼 Lets follow the tradition and write the hello world program

package main //package
import "fmt" //module

func main() { //entry point function (should always be main())
	fmt.Print("Hello World")
}

// To RUN: go run .hello.go
// To Initialize this new module with a specific module path.: go mod init @example/hello-world
// To BUILD: go build
