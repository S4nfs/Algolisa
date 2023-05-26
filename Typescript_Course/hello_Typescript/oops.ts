class Department {
  name: string;
  private employees: string[] = [];

  constructor(private readonly id: number, n: string) {
    //u can also use shorthand initialization here, id + readonly property (can't change)
    this.name = n;
  }
  describe(this: Department) {
    console.log("ID: ", this.id, " | Department name: ", this.name); //this should refer to instance of Department
  }

  addEmployee(employee: string) {
    this.employees.push(employee);
    this.id = 2; //❌ read-only
  }

  printEmployeesInfo() {
    console.log(this.employees.length);
  }
}

//✅ Inheritance
class QADepartment extends Department {
  admins: string[];
  constructor(id: number, public rootUser: string[]) {
    super(id, "QA"); //calls the constructor of base class
    this.admins = rootUser;
  }
}
const obj = new Department(1, "ABC");
obj.describe();

// const objCopy = { name: "DevOps", describe: obj.describe };
// objCopy.describe();

obj.addEmployee("Sagar");
obj.employees[1] = "Jass Manak"; //⚠️ can't add as employees is private modifier
obj.printEmployeesInfo();

const newObj2 = new QADepartment(2, ["Guri", "Sonu"]);
console.log(newObj2);
