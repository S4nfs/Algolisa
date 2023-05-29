class Department {
  name: string; //access everywhere default-public
  private employees: string[] = []; //within the same class, not in private methods
  protected employeez: string[] = []; //can access in inheritance class

  //✅ static methods and properties can be accessed without instantiating the class, like Math.pow()
  static fiscalYear = 2023;

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
  private lastReport: string;

  constructor(id: number, public rootUser: string[], private report: string[]) {
    super(id, "QA"); //calls the constructor of base class
    this.admins = rootUser;
    this.lastReport = report[0];
  }

  addEmployee(employeezName: string) {
    this.employeez.push(employeezName);
    console.log(this.employeez);
  }

  addReport(text: string) {
    this.report.push(text);
    this.lastReport = text;
  }

  private showReport() {
    //❌ only public method can  be used to access/update private variables else use getters/setters
    return this.lastReport;
  }

  //✅ Getters and setters are used to provide an interface for accessing and modifying private properties of a class
  get mostRecentReport() {
    if (this.lastReport) return this.lastReport;
    throw new Error("No reports found");
  }

  set updateRecentReport(value: string) {
    this.addReport(value);
  }

  static createFiscalYear(num: number) {
    console.log(num);
  }
}
const obj = new Department(1, "ABC");
obj.describe();

// const objCopy = { name: "DevOps", describe: obj.describe };
// objCopy.describe();

obj.addEmployee("Sagar");
obj.employees[1] = "Jass Manak"; //⚠️ can't add as employees is private modifier
obj.printEmployeesInfo();

const newObj2 = new QADepartment(2, ["Guri", "Sonu"], []);
newObj2.addEmployee("Goku");
newObj2.addReport("A BCA graduate from BITS Pilani");
newObj2.updateRecentReport = "An MCA post-graduate from Chitkara";
console.log(newObj2.mostRecentReport);
console.log(Department.fiscalYear);
console.log(QADepartment.createFiscalYear(2024));
