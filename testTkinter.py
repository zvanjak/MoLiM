from  tkinter import *


# create a root window.
top = Tk()

top.title("Tk Example")
top.minsize(200, 200)  # width, height
top.geometry("300x300+50+50")

# Create Label in our window
text = Label(top, text="Nothing will work unless you do.")
text.pack()
text2 = Label(top, text="- Maya Angelou")
text2.pack()

# create listbox object
listbox = Listbox(top, height = 10, 
                  width = 15, 
                  bg = "grey",
                  activestyle = 'dotbox', 
                  font = "Helvetica",
                  fg = "yellow")
 
# Define the size of the window.
#top.geometry("300x250")  
 
# Define a label for the list.  
label = Label(top, text = " FOOD ITEMS") 
 
# insert elements by their
# index and names.
listbox.insert(1, "Nachos")
listbox.insert(2, "Sandwich")
listbox.insert(3, "Burger")
listbox.insert(4, "Pizza")
listbox.insert(5, "Burrito")
 
# pack the widgets
label.pack()
listbox.pack()
 
 
# Display until User 
# exits themselves.
top.mainloop()