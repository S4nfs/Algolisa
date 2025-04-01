#🍏 A set is a colection of non-repetitive elements. (Characteristics: Mutatable, unordered, no duplicates, mostly of one type)
a = {1,2,3,4,5,1,"1"}
print(type(a))
print(a)    #{1, 2, 3, 4, 5, '1'}

# -----------------------------------------------------------
b = {} #This will create Empty dictionary not set
print(type(b))

# -----------------------------------------------------------
c = set() #This will create Empty set
print(type(c))
c.add(54)
c.add(9)
# c.add([1,2,5]) #u cannot add list in set
# c.add({1,2,5}) #u cannot add list or dictionary to set
c.add((1,2,5)) #u can add tuple in set
c.remove(54)
print(c)