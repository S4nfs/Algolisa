
# Class attribute (attached to class) || Instance attribute (attached to instance/object)
class Employee:
    company = "Google"
    salary = "500"


sagar = Employee()
print(sagar.company)
Employee.company = "Chatnaut"           # changing class attribute
print(sagar.company)

sagar.salary = 1000
# changing instance attribute [limited to instance only]
print(sagar.salary)


class Benefits:

    health_benefits = []

    def __init__(self):
        self.health_benefits = ["Health Insurance",
                                "Dental Insurance", "Vision Insurance", "401(k)"]


class Employee2:
    company = "Google"
    CTC = 0

    # constructor aka dunder (double underscore) method in python
    def __init__(self, whatsTheCTC, name):  # Self (similar to "this" keyword in Javascript)
        self.CTC = whatsTheCTC
        self.name = name
        self.benefits = []
        # private attributes denoted by __ must be accessible withing the class
        self.__employeeID = 544445554545

    def getSalary(self):
        print(f"My salary at {self.company} is {self.salary}")

    # The __str__() method controls what should be returned when the class object is represented as a string
    def __str__(self):
        return f"return as string {self.company} {self.salary}"

    def getEmplooyeeID(self):
        return self.__employeeID


employee2 = Employee2(8000000, "Sagar")
employee2.salary = 10000000
print("Name", employee2.name)
employee2.getSalary()                       # same as Employee.getSalary(employee2)
print(employee2)
# if you want to see whats the instance looks like
# The __str__() method convert the output of class to dictionary
print("How it looks!", employee2.__dict__)
print(employee2.CTC)
employee2.benefits.append("401(k) Plan")
print(employee2.benefits)
print("Employee ID is: ", employee2.getEmplooyeeID())

# Static Method - When we don't want to use self parameter


class Employee3(Benefits):  # Inheriting the class Benefits
    company = "Facebook"

    def __init__(self, name):
        super().__init__()  # calling parent constructor
        self.name = name

    def getSalary(self):
        print(f"My salary at {self.company} is {self.salary}")

    @staticmethod
    def greet():
        print("Good Morning Sir")


employee3 = Employee3("Rishabh")

employee3.salary = 10000
employee3.getSalary()
employee3.greet()
print(employee3.name, "'s benefits at",
      employee3.company, "are", employee3.health_benefits)
