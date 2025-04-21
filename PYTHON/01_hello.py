# Dev Note: Before we start, I (S4nfs) want to mention that Python is a very easy language. If you're already comfortable with any programming language, you can pick it up within a week or two. It has dynamic typing like PHP and shares similarities with Go.

# Learn more about the Pythons' best practise here: https://peps.python.org/pep-0008/


from winsound import PlaySound

print("Hello World")

#🐍 REPL- stands for Read-Eval-Print Loop. It's an interactive environment where you can enter code, execute it immediately, and see the results—perfect for quick testing and debugging. Write python to access Repl in command line

#🐍 print in single line
print("Another", end=" ")
print("Way", end=" ")
print("of printing", end=" ")
print("HELLO WORLD")

#🐍 Print multiline
print(''' lorem ipsum dolor sit amet, consectetur adipiscing elit.
    Donec euismod, nisi vel consectetur ornare, nisl nunc
    consectetur nisl, sed egestas nisi nisl eu nisi.
    Donec euismod, nisi vel consectetur ornare, nisl nunc''')

#🐍 Import Internal module
import os
print(os.listdir())

#Import External modules : pip install <module>
# from playsound import playsound
# playsound("C:\\xampp\\htdocs\\MyCourses\\PYTHON_course\\1.mp3")




