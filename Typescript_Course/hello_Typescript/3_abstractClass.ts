/*✅ Abstraction means showing the essential features and hiding the background details. U can achieve abstraction by using:
-Abstract Classes
-Interfaces
-Generics
-Type Aliases


Abstract Class - is a class that contains empty methods as well as non-empty methods, have constructor and variables, but instanciation is not possible (meaning u cant create an object of that class which is helpful when u want that class to be untouched).
*/
abstract class Department2 {
  abstract describe2(this: Department2): void;
}

class QADepartment2 extends Department2 {
  describe2(this: Department2) {
    console.log("Hello from Abstract method");
  }
}
// const obj = new Department2(1, "ABC"); //❌ can't instantiate an abstract class

const newObj2 = new QADepartment2();
newObj2.describe2();
