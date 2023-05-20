console.log("Hello Typescript");
//✔️Cheking the types
var add = function (n1, n2, result, str) {
    if (result) {
        var sum_1 = n1 + n2; //avoid concatination
        console.log(str + sum_1);
    }
};
add(30, 5.2, true, "Result is: ");
//The key difference is: javascript uses "dynamic types" resolved at (runtime) whereas Typescript uses "static types" set during (development)
//🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞
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
//🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞
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
//✔️Union type "|"
var sum = function (n1, n2) {
    var res;
    if (typeof n1 === "number" && typeof n2 === "number") {
        res = n1 + n2;
    }
    else {
        res = n1.toString() + n2.toString();
    }
    return res;
};
console.log(sum("30", "20"));
//✔️types in Functions🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞🍞
// number type
var addNumbers = function (n1, n2) {
    //ensure the return type should be number
    return n1 + n2;
};
// void type
function printResult(num) {
    //void as it did not return anything
    console.log("Result in function is: ", num);
}
/* unknown type
Note:
You can assign anything to unknown type but you have to do a type check or type assertion to operate on unknown
You can assign anything to any type and you can perform any operation on any
*/
var iDontCare;
var example;
iDontCare = 5;
iDontCare = "Max";
if (typeof iDontCare === "string")
    example = iDontCare; //without typechecking throw error
/* never type
void is used whenever a function does not return anything explicitly (usually that means it returns undefined implicitly) and never whenever a function never returns at all.
*/
var generateError = function (message, code) {
    throw { message: message, errorCode: code };
};
generateError("An error occured!", 500);
var iWantToUseThatFunction; //function types allow us to describe which type of functions specifically we want to use somewhere with expected value in parameters that matches
iWantToUseThatFunction = addNumbers;
console.log(iWantToUseThatFunction(8, 8));
//callbacks
function addHandle(n1, n2, cb) {
    var result = n1 + n2;
    cb(result);
}
addHandle(22, 22, function (result) {
    console.log(result);
});
