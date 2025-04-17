from tkinter import *
from tkinter import ttk

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
listbox = Listbox(top, height=10,
                  width=15,
                  bg="grey",
                  activestyle='dotbox',
                  font="Helvetica",
                  fg="yellow")

# Define the size of the window.
# top.geometry("300x250")

# Define a label for the list.
label = Label(top, text=" FOOD ITEMS")

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

# Create a frame to hold the Treeview and scrollbar
tree_frame = Frame(top)
tree_frame.place(x=10, y=150, width=400, height=100)  # Set fixed size and position

# Create a Treeview widget with 3 columns
tree = ttk.Treeview(tree_frame, columns=("Column1", "Column2", "Column3"), show="headings", height=4)

# Define column headings
tree.heading("Column1", text="Food Item")
tree.heading("Column2", text="Category")
tree.heading("Column3", text="Price")

# Define column widths
tree.column("Column1", width=100)
tree.column("Column2", width=100)
tree.column("Column3", width=100)

# Insert data into the Treeview
tree.insert("", "end", values=("Nachos", "Snack", "$5"))
tree.insert("", "end", values=("Sandwich", "Snack", "$4"))
tree.insert("", "end", values=("Burger", "Fast Food", "$6"))
tree.insert("", "end", values=("Pizza", "Fast Food", "$8"))
tree.insert("", "end", values=("Burrito", "Mexican", "$7"))

# Create a vertical scrollbar
scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)

# Pack the Treeview and scrollbar inside the frame
tree.pack(side=LEFT, fill=BOTH, expand=True)
scrollbar.pack(side=RIGHT, fill=Y)

# Display until User exits themselves.
top.mainloop()
