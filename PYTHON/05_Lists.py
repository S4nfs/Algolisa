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