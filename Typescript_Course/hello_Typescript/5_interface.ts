/*✅  Interface - 
In TypeScript, both abstract classes and interfaces can be used to define contracts for classes. However, there are some differences between them.

An interface is a pure contract that defines only the structure of the class without any implementation details. It can define properties, methods, and their types, but it cannot contain any implementation code but only in inheritence class.

Differences ? - 
    Classes can only inherit one abstract class but can inherit multiple interfaces.
    An interface can have only abstract methods, an abstract class can have both abstract and non-abstract methods
    An interface can only have public members, while an abstract class can have protected and public members.
    Abstract class can provide the implementation of the interface. Interface can not provide the implementation of an abstract class

*/

interface Greetable {
  name: string; //no implementation
  greet(phrase: string): void;
}

class Person implements Greetable {
  //can inherit multiple interfaces simply put after ,
  name: string;

  constructor(n: string) {
    //implementation
    this.name = n;
  }
  greet(phrase: string) {
    console.log(phrase + " " + this.name);
  }
}

const user = new Person("Jen");
user.greet("Hi there, I am");
console.log(user);
