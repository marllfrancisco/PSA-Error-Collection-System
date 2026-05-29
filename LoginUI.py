from tkinter import *
frame = Tk()

# getting screen width and height of display
width = frame.winfo_screenwidth()
height = frame.winfo_screenheight()

# setting tkinter window size
frame.geometry("%dx%d" % (width, height))
frame.title("Title Here")
label = Label(frame, text="Hello World")
label.pack()

frame.mainloop()