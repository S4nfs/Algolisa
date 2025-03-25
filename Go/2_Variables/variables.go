package main

import (
	"fmt"
	"math"
)

func main() {
	/*🌵 Variables & Variables Types
	int- stores integers (whole numbers), such as 123 or -123
	float32- stores floating point numbers, with decimals, such as 19.99 or -19.99
	string - stores text, such as "Hello World". String values are surrounded by double quotes
	bool- stores values with two states: true or false
	*/
	const inflationRate = 6.5
	var investmentAmount float64 = 1000
	var expectedReturn = 5.5
	var years = 10
	// var FirstName, lastName string = "Sagar", "Verma"

	//Pointers
	fmt.Println("Enter Investment Amt:")
	fmt.Scan(&investmentAmount)

	var futureValue float64 = investmentAmount * math.Pow((1+expectedReturn/100), float64(years))
	futureRealValue := futureValue / math.Pow(1+inflationRate/100, float64(years)) // := inferred type
	fmt.Println(futureValue, futureRealValue)
}
