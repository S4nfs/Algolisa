# 🍏  A Dictionary (sort of a brother of JSON) is a collection of key-value pairs. (Characteristics: Mutatable, unordered, no duplicates, mixed type)

from re import A


myDict = {
    "fast": "In a  quick manner",
    "Sagar": "A coder",
    "Marks": [52, 99, 100],
    "skills": {
        "skill1": "LAMP",
        "skill2": "MERN",
         },
    1:2
}
print(myDict["fast"])
print(myDict["skills"]["skill1"])

myDict["Marks"] = [25, 44, 10]      # Change the values
print(myDict["Marks"])

print(myDict.keys())                # Print all keys with class
print(type(myDict.keys()))          # Type
print(list(myDict.keys()))          # Print all keys[in list by type-casting into list]
print(list(myDict.values()))        # Print all values
print(myDict.items())               # Returns all data in tuple

myDictadd = {                       # Append key:value in Dictionary
    "friends": "Ajay"
}
myDict.update(myDictadd)
print(myDict)

print(myDict.get("Sagar"))           #Both give same result but
print(myDict["Sagar"])               # .get returns [none] if not found and later returns [error: blah blah]


# 🍏 Program that return english word from dictionary-------------------------------------------------------------------------------
myDictionary = {
    "kutta": "Dog",
    "Billi": "Cat",
    "Chuha": "Rat",
    "Hathi" : "Elephant"
}
a = input("Enter the Hindi word: \n")
print(myDictionary.get(a))  #OR
# print(myDictionary[a])    #but it will give error if not found

#🍏 Create an empty Dictionary. Allow 4 frinds to entertheir favourite language as values and use keys as their names.--------------
favLang = {}
a = input("Enter your favourite Language Ajay: \n")
b = input("Enter your favourite Language Vivek: \n")
c = input("Enter your favourite Language Jatin: \n")
d = input("Enter your favourite Language Prateek: \n")
favLang["ajay"] = a
favLang["vivek"] = b
favLang["jatin"] = c
favLang["prateek"] = d
print(favLang)
