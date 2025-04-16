# 🍏 List - (Characteristics: Mutatable a.k.a \editable\, ordered, allow duplicates, mostly of one type)
a = [1, 6, 56, 3, 8]
# OR 
# you can use list() constructor to create a list
# a = list((1,6,56,3,8))
print(a[2])
# ----------------------------------------------
a[2] = 100
print(a)

# Sort------------------------------------------
a.sort()
print(a)

# Append(add to end)---------------------------
a.append(45)
print(a)

# Insert---------------------------------------
a.insert(2, 101)
print(a)

# POP(Delete Index)-----------------------------
a.pop(2)
print(a)

# Remove(Element)-------------------------------
a.remove(45)
print(a)

# 🍏 List comprehensions in Python are a super clean and efficient way to create lists in one liner - improves readability

squares = []
for i in range(5):
    squares.append(i * i)

squaresWithMoreReadability = [i * i for i in range(5)]
print('squaresWithMoreReadability: ', squaresWithMoreReadability)

# Flatten a 2D list:

matrix = [[1, 2], [3, 4]]
flat = [num for row in matrix for num in row]
print('flat: ', flat)

# Convert list of strings to uppercase:
words = ["hello", "world"]
uppercased = [el.upper() if el != "world" else '-'.join(el.upper()) for el in words]
print('uppercased: ', uppercased) #['HELLO', 'W-O-R-L-D']


# 🍏 Duplicating list -  As list values are passed by references we can't directly change value so lets duplicate it first using colon ":"

first_list = [1,2,3,4]
second_list = first_list[:]
second_list[0] = 100
third_list = first_list[0:2] # using range selectors [start index : element]
last_list = first_list[:-1]
print("Duplicating List: ", first_list, "\n", second_list, "\n", third_list, "\n", last_list) # [1, 2,3, 4] [100, 2, 3, 4] [1, 2] [1,2,3]

# Also this works with Tuples but not with Sets &  dictionaries as those are unordered