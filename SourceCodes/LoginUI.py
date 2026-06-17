import ttkbootstrap as tb
from tkinter import StringVar, messagebox, PhotoImage
from SysTheme import psatheme, titlefont, ourfont, navfont, subtitlefont
import json
import os

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = ImageTk = None

#Sets up the main window with ttkbootstrap
frame = tb.Window()
frame.style.register_theme(psatheme)
frame.style.theme_use("psa")

# setting tkinter window size
frame.geometry("%dx%d" % (600, 670))
frame.title("DTBS Login")

###########################################################################

#Frames for Log-in and Sign-up(Create Account)
login_frame = tb.Frame(frame)
signup_frame = tb.Frame(frame)

#shows the login UI
login_frame.pack(fill="both", expand=True)


#Variables in this code
    #This is use for the log-in frame
username_var = StringVar()
password_var = StringVar()
error_var = StringVar()
    #This is use for the sign-up
new_username_var = StringVar()
new_email_var = StringVar()
new_password_var = StringVar()
confirm_new_password_var = StringVar()

#Opens file or create a new one
file_name = "accounts.json"
if os.path.exists(file_name):
    with open(file_name, "r") as file:
        entries = json.load(file)
        #print("File loaded successfully")
else:
    database = {
        "Admin" : ("Admin@gmail.com", "UnlimitedDataWorks" ),
        "Michael Daitol" : ("GelSensei@gmail.com", "1mgelodesu!")
    }

###########################################################################

#This verify the username and password inputted
def verify_user_n_passcode():
    entered_username: str = input_username.get()
    entered_password: str = input_password.get()

    for username, data in database.items():
        Email = data[0]
        Password = data[1]
    
        #This checks if the username/email entered is in the list
        if entered_username == Email or entered_username == username:

            #Checks if the password stare
            if entered_password == Password:
                messagebox.showinfo("Success", "Log in successful")
            else:
                error_var.set("Wrong Password")
            return
    error_var.set("User not found")
    
#This changes the frame(or widgets) showing in the window
def show_signup():
    login_frame.pack_forget()
    signup_frame.pack(fill="both", expand=True)

def show_login():
    signup_frame.pack_forget()
    login_frame.pack(fill="both", expand=True)

def add_account():
    print("YOOOOOOOOOOOOOOOOOO~~")

def record_accounts():
    pass
########################     Log in Section       ####################################

login_card = tb.Frame(login_frame, padding=25)
login_card.place(relx=0.5, rely=0.5, anchor="center")

# Logo image
logo_path = os.path.join(os.path.dirname(__file__), "images/psa.png")
logo_image = None
logo_size = (120, 120)  # change to the desired logo size
if os.path.exists(logo_path):
    if Image is not None:
        pil_logo = Image.open(logo_path).resize(logo_size, Image.LANCZOS)
        logo_image = ImageTk.PhotoImage(pil_logo)
    else:
        logo_image = PhotoImage(file=logo_path)
        # fallback: only shrink by integer factors if Pillow is unavailable
        subsample_x = max(1, logo_image.width() // logo_size[0])
        subsample_y = max(1, logo_image.height() // logo_size[1])
        if subsample_x > 1 or subsample_y > 1:
            logo_image = logo_image.subsample(subsample_x, subsample_y)
    tb.Label(login_card, image=logo_image).pack(pady=(0, 15))

# Login title
tb.Label(login_card, text="Error Collection System", font=subtitlefont).pack(pady=(0, 14))
tb.Label(login_card, text="User Login", font=titlefont).pack(pady=(0, 16))


# Takes the username/email input
tb.Label(login_card, text="Username / Email", font=navfont).pack(anchor="w", pady=(5, 2))
input_username = tb.Entry(login_card, textvariable=username_var, font=ourfont, width=30)
input_username.pack(pady=5, fill="x")

#this takes the password input
tb.Label(login_card, text="Password", font=navfont).pack(anchor="w", pady=(10, 2))
input_password = tb.Entry(login_card, textvariable=password_var, font=ourfont, width=30, show="*")
input_password.pack(pady=5, fill="x")

# Error Messager
error_label = tb.Label(login_card, textvariable=error_var, bootstyle="danger")
error_label.pack()

#confirm button
tb.Button(login_card, text="Login", bootstyle="primary", command=verify_user_n_passcode, width=60, padding=10).pack(pady=5)

#Sign-up button
tb.Button(login_card, text="Create Account", bootstyle="secondary", command=show_signup).pack(pady=5)

##################################  Sign up Section   ###############################################

#Sign-up is still under construction
signup_card = tb.Frame(signup_frame, padding=25)
signup_card.place(relx=0.5, rely=0.5, anchor="center")

tb.Label(signup_card, text="User Sign-up", font=titlefont).pack(pady=(0, 15))

# Takes the user's username
tb.Label(signup_card, text="Enter Username", font=navfont).pack(anchor="w", pady=(5, 2))
input_username = tb.Entry(signup_card, textvariable=new_username_var, font=ourfont, width=30)
input_username.pack(pady=5, fill="x")

# Takes the user's username
tb.Label(signup_card, text="Enter Email", font=navfont).pack(anchor="w", pady=(5, 2))
input_username = tb.Entry(signup_card, textvariable=new_email_var, font=ourfont, width=30)
input_username.pack(pady=5, fill="x")

# Takes the user's username
tb.Label(signup_card, text="Enter Password", font=navfont).pack(anchor="w", pady=(5, 2))
input_username = tb.Entry(signup_card, textvariable=new_password_var, font=ourfont, width=30)
input_username.pack(pady=5, fill="x")

# Takes the user's username
tb.Label(signup_card, text="Confirm Password", font=navfont).pack(anchor="w", pady=(5, 2))
input_username = tb.Entry(signup_card, textvariable=confirm_new_password_var, font=ourfont, width=30)
input_username.pack(pady=5, fill="x")


#confirm button
tb.Button(signup_card, text="Sign-up", bootstyle="primary", command=add_account, width=60, padding=10).pack(pady=5)

#Back button
tb.Button(signup_card, text="Back", bootstyle="secondary", command=show_login).pack(pady=5)


frame.mainloop()