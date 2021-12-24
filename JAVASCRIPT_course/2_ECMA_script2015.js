/* LET,CONST,VAR

✔️ let 
-is block scoped, means it lives in curly braces {}. 
-can be updated but not re-declared
👍  can be updated
    let greeting = "say Hi";
    greeting = "say Hello instead";

👎  can not be re-declared
    let greeting = "say Hi";
    let greeting = "say Hello instead";
-However, if the same variable is defined in different scopes, there will be no error:
    let greeting = "say Hi";
    if (true) {
        let greeting = "say Hello instead";
        console.log(greeting); // "say Hello instead"
    }
    console.log(greeting); // "say Hi"



✔️ const 
-is block scoped
-cannot be updated or re-declared



✔️ var 
-is function scoped if used within a function and global scoped if used outside a function
-can be re-declared and updated

*/
// -----------------------------------------------------------------------------------------------------------------------------
// var myname = "Sagar Verma";
// myname = "S4nfs";
// console.log(myname);                       //output: S4nfs                     

// let myname1 = "Sagar Verma";
// myname1 = "S4nfs";
// console.log(myname1);                      //output: S4nfs                     

// const myname2 = "Sagar Verma";             //error: const variable can't be changed
// myname2 = "S4nfs";
// console.log(myname2);


// ✔️ Var => Function Scope  | let and const => Block Scope--------------------------------------------------------------------
// function biodata(){
// var myFirstName = "Sagar";                   //with var
// console.log(myFirstName);

// if(true){
//     var myLastName = "Verma";
//     console.log('inner ' + myLastName);
//     console.log('inner ' + myFirstName);
// }
// console.log('innerouter ' + myLastName);

// }
// biodata();

// function biodata(){
//     let myFirstName = "Sagar";                  //with let
//     console.log(myFirstName);
    
//     if(true){
//         let myLastName = "Verma";
//         console.log('inner ' + myLastName);
//         console.log('inner ' + myFirstName);
//     }
//     console.log('innerouter ' + myLastName);    //error: you can't use let variables outside function block
    
//     }
//     biodata();


// ✔️ Fat Arrow function ⟹ --------------------------------------------------------------------------------------------------------
//normal function
// function sum(){
//     let a = 5, b =10;
//     let sum = a + b;
//     return (`The sum of two numbers is ${sum}`)
// }
// console.log(sum());

// //with fat arrow
// const sum  = () => {
//     let a = 5, b =10;
//     let sum = a + b;
//     return (`The sum of two numbers is ${sum}`)
// }
// console.log(sum());
