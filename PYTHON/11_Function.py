# 🍏 A Python Function
def greet(name):
    print("Hello, I am " + name)
greet("Sagar Verma")

# 🍏 Lambda or Anonymous function,  SYNTAX: lambda arguments : expression

bmw = [1,2,3,4]
print(list(map(lambda car: car*2, bmw)))


def myfunc(n):
  return lambda a : a * n

mydoubler = myfunc(2)
print(mydoubler(11))

# 🍏 Reduce function

# 🍏 Unpacking function arguments (Like Rest or Spread operators in Javascript). Python doesn't call them "rest" and "spread", but it does the same thing using: 
# "Rest" equivalent → *args and **kwargs
# "Spread" equivalent → Unpacking using * and **

"""
Concept                     | JavaScript    | Python

Gather positional           | ...args       | *args
Gather named values         | ...object     | **kwargs
Spread list                 | [...array]    | [*list]
Spread dict                 | {...obj}      | {**dict}
"""

def unlimited_arguments(*args2, **keyword_args):
    # for argument in args:
    #     print(argument)

    for argument in args2:
      print(argument)

    for k, dict_argument in keyword_args.items():
      print(k,dict_argument)
    
unlimited_arguments( "-------", "With normal values/tuples", (1,2,3,4), "-------", "With Lists", *[1,2,3,4], "-------", "With Dicts like data", name = "McLaren", HP = "530KW")