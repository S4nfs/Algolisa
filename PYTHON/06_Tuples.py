# 🍏 A touple is an immmutable datatype in python (Characteristics: Immutatable, ordered, allow duplicates, mixed type)
# Creating a tuple using (). The difrenece b/w tuple and list is that you can't change the value (immutable) in tuple

t = (1, 25, 4, 8, 9, 4, 12)
print(t[2])

# Methods()------------------------------------------
print(t.count(4))  # count the number of times the element is present in the tuple
print(t.index(12))  # index of the element

#-----------------------------------------------------
t1 = (1)  # ❌ way to declare single tuple
t2 = (1,)  # ✅
print(t1)
print(t2)
