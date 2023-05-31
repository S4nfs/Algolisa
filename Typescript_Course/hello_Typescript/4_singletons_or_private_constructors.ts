//✅ a singleton is an object that can only be instantiated once. This pattern is often used to ensure that there is only one instance of an object that needs to be accessed globally throughout an application and can be achieved through private constructor & static [Not in regular use]

class Department3 {
  name: string;
  private static instance: Department3;

  private constructor(private readonly id: number, n: string) {
    this.name = n;
  }

  static getInstanceOnce() {
    if (Department3.instance) return this.instance;
    this.instance = new Department3(1, "ABC");
    return this.instance;
  }
}

const obj1 = Department3.getInstanceOnce();
const obj2 = Department3.getInstanceOnce();

console.log(obj1, obj2);
