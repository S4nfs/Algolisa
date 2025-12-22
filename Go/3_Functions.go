// A function is a block of statements that can be used repeatedly in a program.
package main

import (
	"fmt"
)

func myName(name string) string {
	return name
}

// also can be written as with naked return
// func myName(name string) (n string) {
// 	n = name
// 	return
// }

func main() {
	fmt.Print(myName("Sagar Verma"))
}
