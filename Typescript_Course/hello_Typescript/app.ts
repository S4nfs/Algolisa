console.log("Hello Typescript");

//cheking the types
const add = (n1: number, n2: number, result: boolean, str: string) => {
  if (result) {
    let sum = n1 + n2; //avoid concatination
    console.log(str + sum);
  }
};
add(30, 5.2, true, "Result is: ");

//The key difference is: javascript uses "dynamic types" resolved at (runtime) whereas Typescript uses "static types" set during (development)
