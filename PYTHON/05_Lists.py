# 🍏 List - (Characteristics: Mutatable a.k.a \editable\, ordered, allow duplicates, mostly of one type)
a = [1, 6, 56, 3, 8]
# OR 
# you can use list() constructor to create a list
# a = list((1,6,56,3,8))
print(a[2])  # 56
# ----------------------------------------------
a[2] = 100
print(a)  # [1, 6, 100, 3, 8]

# Sort------------------------------------------
a.sort()
print("Sorted :", a)  # [1, 3, 6, 8, 100]

# Append (add to end, one elemnt at a time)-------
a.append(45) 
# a.append([88,99]) # [1, 3, 6, 8, 100, [88,99]]
print("Append : ",a)  # [1, 3, 6, 8, 100, 45]

# Insert----------------------------------------
a.insert(2, 101)
print("Inserted :",a)  # [1, 3, 101, 6, 8, 100, 45]

# POP (Delete Index)----------------------------
a.pop(2)
print("Popped :",a)  # [1, 3, 6, 8, 100, 45]

# Remove (Element)------------------------------
a.remove(45)
print("Removed :",a)  # [1, 3, 6, 8, 100]

# Extend (Add multiple elements)----------------
a.extend([7, 9])
print("Extended :",a)  # [1, 3, 6, 8, 100, 7, 9]

# Index (Find index of element)-----------------
print(a.index(8))  # 3

# Count (Occurrences of element)---------------
print(a.count(3))  # 1

# Reverse (In-place reverse)--------------------
a.reverse()
print(a)  # [9, 7, 100, 8, 6, 3, 1]

# Copy (Shallow copy of list)-------------------
b = a.copy()
print(b)  # [9, 7, 100, 8, 6, 3, 1]

# Del (Deletes element, works with only lists & dictionaries but not with tuples & sets as they are immutable )-------------------
del(a[0])
print("Del :",a)  # [ 7, 100, 8, 6, 3, 1]


# Clear (Remove all elements)-------------------
a.clear()

print(a)  # []

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


# 🍏 Duplicating list (shallow copy) -  As list values are passed by references we can't directly change value so lets duplicate  it first using colon ":"

first_list = [1,2,3,4]
second_list = first_list[:]
second_list[0] = 100
third_list = first_list[0:2] # using range selectors [start index : element]
last_list = first_list[:-1]
print("Duplicating List: ", first_list, "\n", second_list, "\n", third_list, "\n", last_list) # [1, 2,3, 4] [100, 2, 3, 4] [1, 2] [1,2,3]

# Also this works with Tuples but not with Sets &  dictionaries as those are unordered