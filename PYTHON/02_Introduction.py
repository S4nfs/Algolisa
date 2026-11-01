#🍏 A variable is a container to store a value. [IS CASE-SENSITIVE]
# Keywords are reserved words in python.
# Identifiers = class/function/variable name

#Python is dynamically typed (like PHP, JS), not statically typed.
#🔹 Dynamic Typing: (like PHP) You don’t need to declare variable types explicitly. The type is determined at runtime.
#🔹 Static Typing (like in Go, Java, C, TypeScript): Variable types are declared and checked at compile time.

a = "Sagar"                                         # string        Output: "Sagar"
_b = 30                                             # numbers can be written as 3_000_000 (3 mill)        Output: 30
c_1 = 45.25                                         # float         Output: 45.25
c_2 = 1j                                            # complex       Output: 1j
D = True                                            # boolean       Output: True
e = None                                            # none          Output: None
f = ["apple", "banana", "cherry"]                   # list          Output: ["apple", "banana", "cherry"]
g = ("apple", "banana", "cherry")                   # tuple         Output: ("apple", "banana", "cherry")
i =  {"name" : "Sagar", "age" : 28}                 # dict          Output: {"name" : "Sagar", "age" : 28}
j = {"apple", "banana", "cherry"}                   # set           Output: {"apple", "banana", "cherry"}
h = range(6)                                        # range         Output: range(0, 6)
k = frozenset({"apple", "banana", "cherry"})        # frozenset     Output: frozenset({"apple", "banana", "cherry"})
l = b"Hello"	                                    # bytes         Output: b"Hello"
m = bytearray(5)	                                # bytearray     Output: bytearray(b'\x00\x00\x00\x00\x00')
n = memoryview(bytes(5))                            # memoryview    Output: <memory at 0x006F8FA0>


#Strings, Numbers and Booleans are passed by values
print(type(a)) #<class 'str'>
print(type(_b)) #<class 'int'>
print(type(c_1)) #<class 'float'>
print(type(c_2)) #<class 'complex'>
print(type(D)) #<class 'bool'>
print(type(e)) #<class 'NoneType'>
print(type(f)) #<class 'list'>
print(type(g)) #<class 'tuple'>
print(type(i)) #<class 'dict'>
print(type(j)) #<class 'set'>
print(type(h)) #<class 'range'>
print(type(k)) #<class 'frozenset'>
print(type(l)) #<class 'bytes'>
print(type(m)) #<class 'bytearray'>
print(type(n)) #<class 'memoryview'>

print("\n")
# Variables are block scope inside a function and global outside the function but you can set it globally accessed using global keyword
global name
name = "S4nfs"


print("\n")
#🍏 OPERATORS ---------------------------------------------------------------------------------------------------
''' 
1. Arithmetic Operators : +, -, *, /, %, **, //
2. Assignment Operators : =, +=, -=, *=, /=, //=, %=, **=
3. Comparison Operators : ==, !=, >, <, >=, <=
4. Logical Operators : and, or, not
5. Bitwise Operators : &, |, ^, ~, <<, >>
6. Membership Operators : in, not in
7. Identity Operators : is, is not

'''
#[1]
x = 20
y = 10
print("Addition of x and y is ", x+y)
print("Subtraction of x and y is ", x-y) 
print("Multiplication of x and y is ", x*y)
print("Division of x and y is ", x/y) #floating point 2.0
print("Modulus of x and y is ", x%y)
print("Exponent of x and y is ", x**y)# x to the power of y
print("Floor division of x and y is ", x//y)# same as division but rounds the result (to Int) down here 2

#[2]
a_1 = 10
a_1 += 5
print(a_1) #15

#[3]
p = (10 > 5)
print(p) #True

#[4]
age  = 49
print("Age", age > 30 and (age <50 or age > 40 and age is not 10000)) # true

#[7]
x = ["apple", "mangoes"]
y = ["apple", "mangoes"]
z = x

print("is :",x is z) # returns True because z is the same object as x
print("is :", x is y) # returns False because x is not the same object as y, even if they have the same content
print("Equal :", x == y) #True because x is equal to y


print("pineapple" not in x) #returns True as the value "pineapple" is not in the list


#🍏 Type Casting ---------------------------------------------------------------------------------------------------

a = "10"
print(int(a)) #convert string to integer  = 10
print(float(a))# 10.0
print(str(10)) # "10"
print(bool(a)) # True
print(bool("")) # False

