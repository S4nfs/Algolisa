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
