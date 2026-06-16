from tkinter import *
from tkinter import messagebox

frame = Tk()

# getting screen width and height of display
width = 400
height = 200

# setting tkinter window size
frame.geometry("%dx%d" % (width, height))
frame.title("DTBS Login")

username_var = StringVar(value="Enter username")
password_var = StringVar(value="Enter password")
error_var = StringVar()

database = {
    1 : ("Admin@gmail.com", "Admin", "2UnlimitedDataWorks" ),
    2 : ("YuushAris@gmail.com", "Arisu Tendou", "HerofTalesaga1"),
    3 : ("GelSensei@gmail.com", "Michael Daitol", "1mgelodesu!")
}

#This verify the username and password inputted
def verify_user_n_passcode():
    entered_username: str = input_username.get()
    entered_password: str = input_password.get()

    for user in database.values():
        Email = user[0]
        Username = user[1]
        Password = user[2]
    
        #This checks if the username/email entered is in the list
        if entered_username == Email or entered_username == Username:

            #Checks if the password stare
            if entered_password == Password:
                messagebox.showinfo("Success", "Log in successful")
            else:
                error_var.set("Wrong Password")
            return
    error_var.set("User not found")
    
    
#Main UI layout
label = Label(frame, text="User login", font=("sans-serif", 24))
label.pack()


# Takes the username/email input
input_username = Entry(frame, textvariable=username_var, font=("sans-serif", 14), fg="gray")
input_username.pack()

#This handle the display of 'Enter username' to show or not
def on_focus_in(event):
    if username_var.get() == "Enter username":
        username_var.set("")
        input_username.config(fg="black")

def on_focus_out(event):
    if username_var.get() == "":
        username_var.set("Enter username")
        input_username.config(fg="gray")

input_username.bind("<FocusIn>", on_focus_in)
input_username.bind("<FocusOut>", on_focus_out)



#this takes the password input
input_password = Entry(frame, textvariable=password_var, font=("sans-serif", 14), fg="gray")
input_password.pack()

#This handle the display of 'Enter password' to show or not
def passkey_focus_in(event):
    if password_var.get() == "Enter password":
        password_var.set("")
        input_password.config(show="*", fg="black")

def passkey_focus_out(event):
    if password_var.get() == "":
        input_password.config(show="", fg="gray")
        password_var.set("Enter password")

input_password.bind("<FocusIn>", passkey_focus_in)
input_password.bind("<FocusOut>", passkey_focus_out)



#confirm button
Button(frame, text="    Sign in    ", command=verify_user_n_passcode).pack()

#Error message or something
label = Label(frame, text=" ", textvariable=error_var, fg="red")
label.pack()
frame.mainloop()