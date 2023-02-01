console.log("Hello Typescript");
//✔️Cheking the types
var add = function (n1, n2, result, str) {
    if (result) {
        var sum = n1 + n2; //avoid concatination
        console.log(str + sum);
    }
};
add(30, 5.2, true, "Result is: ");
//The key difference is: javascript uses "dynamic types" resolved at (runtime) whereas Typescript uses "static types" set during (development)
//✔️Typescript work flawless when checking errors, repeat "flawless". Lets see other data types like touple
var person = {
    name: "Sagar Verma",
    age: 23,
    friends: [4, "pratik", "gaurav", "ritvik", "rohan"],
    role: [2, "SWE"]
};
person.role.push(22);
// person.role[1](22); //❌ will not throw error
console.log(person);
// for (let a of person.friends) {
//     console.log(a.map((element) => element ))  //❌ will not throw error in normal js in build time
// }
//✔️An enum is a special "class" that represents a group of constants (unchangeable variables). Comes in two flavors string and numeric
var Role;
(function (Role) {
    Role[Role["Enterprise"] = 0] = "Enterprise";
    Role[Role["Admin"] = 44] = "Admin";
    Role[Role["Moderator"] = 45] = "Moderator";
    Role["Client"] = "client";
})(Role || (Role = {}));
console.log(Role.Enterprise); //0
console.log(Role.Admin); //44
console.log(Role.Moderator); //45
console.log(Role.Client); //"client"
