console.log("Hello Typescript");

//✔️Cheking the types
const add = (n1: number, n2: number, result: boolean, str: string) => {
  if (result) {
    let sum = n1 + n2; //avoid concatination
    console.log(str + sum);
  }
};
add(30, 5.2, true, "Result is: ");

//The key difference is: javascript uses "dynamic types" resolved at (runtime) whereas Typescript uses "static types" set during (development)

//🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞
//✔️Typescript work flawless when checking errors, repeat "flawless". Lets see other data types like touple
const person: {
  name: string;
  age: number;
  friends: any[]; //array with any type
  role: [number, string]; //touple - is a typed array with predefined length and type
} = {
  name: "Sagar Verma",
  age: 23,
  friends: [4, "pratik", "gaurav", "ritvik", "rohan"],
  role: [2, "SWE"],
};

person.role.push(22);
// person.role[1](22); //❌ will not throw error
console.log(person);

// for (let a of person.friends) {
//     console.log(a.map((element) => element ))  //❌ will not throw error in normal js in build time
// }

//🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞
//✔️An enum is a special "class" that represents a group of constants (unchangeable variables). Comes in two flavors string and numeric
enum Role {
  Enterprise,
  Admin = 44, //numeric
  Moderator,
  Client = "client", //string
}
console.log(Role.Enterprise); //0
console.log(Role.Admin); //44
console.log(Role.Moderator); //45
console.log(Role.Client); //"client"

//✔️Union type "|"
const sum = (n1: number | string, n2: number | string) => {
  let res;
  if (typeof n1 === "number" && typeof n2 === "number") {
    res = n1 + n2;
  } else {
    res = n1.toString() + n2.toString();
  }
  return res;
};
console.log(sum("30", "20"));

//✔️types in Functions🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞
let addNumbers = (n1: number, n2: number): number => {
  //ensure the return type should be number
  return n1 + n2;
};

function printResult(num: number): void {
  //void as it did not return anything
  console.log("Result in function is: ", num);
}

printResult(addNumbers(8, 8));
let iWantToUseThatFunction: (a: number, b: number) => number; //function types allow us to describe which type of functions specifically we want to use somewhere with expected value in parameters that matches
iWantToUseThatFunction = addNumbers;
console.log(iWantToUseThatFunction(8, 8));

//callbacks
function addHandle(n1: number, n2: number, cb: (num: number) => void) {
  const result = n1 + n2;
  cb(result);
}
addHandle(22, 22, (result) => {
  console.log(result);
});
