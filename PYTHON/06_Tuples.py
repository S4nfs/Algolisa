# 🍏 A tuple is an immmutable datatype in python. (Characteristics: Immutatable, ordered, allow duplicates, mixed type)
# Creating a tuple using (), u can remember easily as it sounds like turtle which is oval in shape. The difrenece b/w tuple and list is that you can't change the value (immutable) in tuple

t = (1, 25, 4, 8, 9, 4, 12)
print(t[2])

# 🍏 Methods()------------------------------------------
print(t.count(4))  # count the number of times the element is present in the tuple
print(t.index(12)) # index of the element

#-----------------------------------------------------
t1 = (1)  # ❌ way to declare single tuple
t2 = (1,) # ✅
print(t1)
print(t2)

tuple1 = (1, 2, 3)
tuple2 = (4, 5)

# Length-------------------------------------------
print("Length:", len(tuple1))  # 3

# Concatenation------------------------------------
print("Concatenation:", tuple1 + tuple2)  # (1, 2, 3, 4, 5)

# Repetition---------------------------------------
print("Repetition:", tuple1 * 2)  # (1, 2, 3, 1, 2, 3)

# Membership---------------------------------------
print("Is 2 in tuple1?", 2 in tuple1)  # True

# Looping------------------------------------------
for item in tuple1:
    print("Item:", item)

# Tuple Unpacking----------------------------------
a, b, c = tuple1
print("Unpacked:", a, b, c)  # 1 2 3