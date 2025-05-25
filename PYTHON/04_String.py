greeting = "Good Morning, "
group = "to all of you"
print(greeting + group) #concatenation

# 🍏 String Slicing---------------------------------------------------------

name = "JohnIsAGoodBoy"
print(name[0])  #J
print(name[0:3]) #Joh
print(name[0:]) #John
print(name[:]) #John
print(name[-1]) #n
print(name[-4]) #J
print(name[0::2]) #Skip character every 2
print(len(name)) #Length of string

# 🍏 Escape Sequencing- \n(newline), \t(tab), \'(single quote), \\(backslash)

school = "\'I studied \tcommerce from \nST.Judes College\'"
print(school)

# 🍏 A program to replace string---------------------------------------------
letter = '''Dear  <|Name|>,
Greetings from ABC coding house.

You are Selected for the next round of the coding challenge.
thanks and regards,
Team ABC
Date: <|Date|>'''

name = input("Enter your name: \n")
date = input("Enter the date: \n")
letter = letter.replace("<|Name|>", name)
letter = letter.replace("<|Date|>", date)
print(letter)

# 🍏 String Methods
"""
upper()      - returns a copy of the string with all characters in uppercase
lower()      - returns a copy of the string with all characters in lowercase
capitalize() - returns a copy of the string with the first character capitalized
title()      - returns a string with the first letter of each word capitalized
strip()      - removes leading and trailing whitespaces (or characters)
replace()    - replaces all occurrences of a substring with another
find()       - returns the index of the first occurrence of a substring, -1 if not found
split()      - splits the string into a list using a delimiter (default is space)
join()       - joins elements of a list into a single string with a delimiter
startswith() - returns True if the string starts with the specified substring
endswith()   - returns True if the string ends with the specified substring
count()      - returns the number of occurrences of a substring

isalpha()      - Returns True if all characters are alphabetic
isdigit()      - Returns True if all characters are digits
isalnum()      - Returns True if all characters are alphanumeric
isspace()      - Returns True if all characters are whitespace
islower()      - Returns True if all characters are lowercase
isupper()      - Returns True if all characters are uppercase

format()       - Returns a formatted string using placeholders

zfill(width)   - Pads string on the left with zeros to fill width
center(width)  - Centers the string in a field of given width
ljust(width)   - Left-justifies string in a field of given width
rjust(width)   - Right-justifies string in a field of given width
"""

s = "  hello world  "

# Upper------------------------------------------
print("Upper:", s.upper())  # '  HELLO WORLD  '

# Lower------------------------------------------
print("Lower:", s.lower())  # '  hello world  '

# Capitalize-------------------------------------
print("Capitalize:", s.capitalize())  # '  hello world  ' → '  hello world  ' (only first non-space char)

# Title------------------------------------------
print("Title:", s.title())  # '  Hello World  '

# Strip------------------------------------------
print("Strip:", s.strip())  # 'hello world'

# Replace----------------------------------------
print("Replace:", s.replace("world", "Python"))  # '  hello Python  '

# Find-------------------------------------------
print("Find:", s.find("world"))  # 8

# Split------------------------------------------
print("Split:", s.split())  # ['hello', 'world']

# Join-------------------------------------------
words = ['hello', 'world']
print("Join:", "-".join(words))  # 'hello-world'

# Startswith-------------------------------------
print("Startswith '  he':", s.startswith("  he"))  # True

# Endswith---------------------------------------
print("Endswith 'ld  ':", s.endswith("ld  "))  # True

# Count------------------------------------------
print("Count 'l':", s.count("l"))  # 3


# Character type checks
print("isalpha:", "hello".isalpha())    # True
print("isdigit:", "123".isdigit())      # True
print("isalnum:", "abc123".isalnum())   # True
print("isspace:", "   ".isspace())      # True
print("islower:", "hello".islower())    # True
print("isupper:", "HELLO".isupper())    # True

# Formatting methods
print("format:", "My name is {} {}".format("Austin", "Powers"))  # 'My name is Austin Powers'
print("format with index:", "{1} {0}".format("world", "Hello"))  # 'Hello world'

# Padding and alignment, Yep Python can do CSS tricks
print("zfill:", "42".zfill(5))         # '00042'
print("center:", "hi".center(10, "-")) # '----hi----'
print("ljust:", "hi".ljust(10, "."))   # 'hi........'
print("rjust:", "hi".rjust(10, "."))   # '........hi'