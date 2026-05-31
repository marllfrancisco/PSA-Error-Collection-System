from tkinter import *
frame = Tk()

# getting screen width and height of display
width = frame.winfo_screenwidth()
height = frame.winfo_screenheight()

# setting tnnnnnnkinter window size
frame.geometry("%dx%d" % (width, height))
frame.title("Titlee Here")
label = Label(frame, text="Hello World")
label.pack()

frame.mainloop()