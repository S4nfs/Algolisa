console.log("Hello Typescript");
//cheking the types
var add = function (n1, n2, result, str) {
    if (result) {
        var sum = n1 + n2; //avoid concatination
        console.log(str + sum);
    }
};
add(30, 5.2, true, "Result is: ");
//The key difference is: javascript uses "dynamic types" resolved at (runtime) whereas Typescript uses "static types" set during (development)
