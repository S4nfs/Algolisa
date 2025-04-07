# 🍏 List - (Characteristics: Mutatable a.k.a \editable\, ordered, allow duplicates, mostly of one type)
a = [1, 6, 56, 3, 8]
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
uppercased = [word.upper() for word in words]
print('uppercased: ', uppercased)
