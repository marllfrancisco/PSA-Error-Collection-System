import ttkbootstrap as tb
from tkinter import StringVar, messagebox, PhotoImage
from SysTheme import psatheme, titlefont, ourfont, navfont, subtitlefont
import json
import csv
import os
from datetime import datetime

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = ImageTk = None

############################### Main Frame ##############################
#Sets up the main window with ttkbootstrap
frame = tb.Window()
frame.style.register_theme(psatheme)
frame.style.theme_use("psa")

# setting tkinter window size CENTERED
# 1. Set the window size
app_width = 600
app_height = 670

# 2. Calculate screen coordinates
screen_width = frame.winfo_screenwidth()
screen_height = frame.winfo_screenheight()

# 3. Calculate window coordinates
x = (screen_width / 2) - (app_width / 2)
y = (screen_height / 2) - (app_height / 2)

# 4. Apply geometry with the calculated position
frame.geometry(f"{app_width}x{app_height}+{int(x)}+{int(y)}")

frame.title("PSA Error Collection")

###########################################################################

#Frames for Log-in and Sign-up(Create Account) and forget_frame
login_frame = tb.Frame(frame)
signup_frame = tb.Frame(frame)
forget_frame = tb.Frame(frame)

#shows the login UI
login_frame.pack(fill="both", expand=True)


#Variables in this code
ADMIN_PASSWORD = "UnlimitedDataWorks" #I am the bones of my code. keys is my body, 0 and 1s is my blood
    #This is use for the log-in frame
username_var = StringVar()
password_var = StringVar()
login_error_var = StringVar()
    #This is use for the sign-up
new_email_var = StringVar()
new_password_var = StringVar()
confirm_new_password_var = StringVar()
signup_error_var = StringVar()
    #this is use for forgetting password
forget_username_var = StringVar()
forget_new_password_var = StringVar()
admin_password_var = StringVar()
forget_error_var = StringVar()
    #I dunno.... ahahaha
file_name = "employee_data.csv"
database = {}

###########################################################################

def load_accounts():

    accounts = {}

    try:
        with open(file_name, newline="", encoding="utf-8") as file:

            reader = csv.DictReader(file)

            for row in reader:

                employee_id = row["employee_id"]

                accounts[employee_id] = {
                    "person_id": row["person_id"],
                    "email": row["email"],
                    "password": row["password"],
                    "created_id": row["created_id"],
                    "modified_id": row["modified_id"]
                }

    except FileNotFoundError:
        print("employee_data.csv not found")

    return accounts

#This verify the username and password inputted
def verify_user_n_passcode():
    login_error_var.set("")

    entered_username: str = input_username.get()
    entered_password: str = input_password.get()

    for employee_id, data in database.items():
        if entered_username == data["email"]:
            if entered_password == data["password"]:

                messagebox.showinfo(
                    "Success",
                    "Log in successful"
                )
            else:
                login_error_var.set("Wrong Password")
            return
    login_error_var.set("User not found")    

def add_account():
    signup_error_var.set("")

    new_email: str = new_email_var.get()
    new_password: str = new_password_var.get()
    confirm_password = confirm_new_password_var.get()
    

    if new_email == "" or new_password == "":
        signup_error_var.set("Some fields are blank. please fill them all")
        return
    
    if not new_email.endswith("@psa.gov.ph"):
        signup_error_var.set("Only @psa.gov.ph emails are allowed.")
        return

    if new_password != confirm_password:
        signup_error_var.set("Mismatched Passwords, try again")
        return
    
    for data in database.values():
        if new_email == data["email"]:
            signup_error_var.set(
                "Email already exists."
            )
            return
        
        
    confirm = messagebox.askyesno("Create Account", "Do you want to create this account?")

    if confirm:
        employee_id = generate_employee_id()
        person_id = generate_person_id()
        created_date = get_current_date()

        database[employee_id] = {
            "person_id": person_id,
            "email": new_email,
            "password": new_password,
            "created_id": created_date,
            "modified_id": created_date
        }

        record_accounts()

        messagebox.showinfo(
            "Success",
            f"Account created.\nEmployee ID: {employee_id}"
        )

        show_login()

def change_password():
    forget_error_var.set("")

    forgotten_email = forget_username_var.get()
    new_user_password = forget_new_password_var.get()
    admin_passkey = admin_password_var.get()

    if admin_passkey != ADMIN_PASSWORD:
        forget_error_var.set(
            "Wrong Admin Password"
        )
        return
    
    for employee_id, data in database.items():

        if forgotten_email == data["email"]:

            confirm = messagebox.askyesno(
                "Change Password",
                f"Change password for '{employee_id}'?"
            )

            if confirm:

                data["password"] = new_user_password
                data["modified_id"] = get_current_date()

                record_accounts()

                messagebox.showinfo(
                    "Success",
                    "Password changed successfully!"
                )

                show_login()

            return

    forget_error_var.set("User not found")
    
def generate_employee_id():
    if not database:
        return "EMP-001"

    last_id = max(
        int(emp_id.split("-")[1])
        for emp_id in database
    )

    return f"EMP-{last_id + 1:03d}"

def generate_person_id():

    if not database:
        return "P-10001"

    last_id = max(
        int(data["person_id"].split("-")[1])
        for data in database.values()
    )

    return f"P-{last_id + 1}"

def get_current_date():

    return datetime.now().strftime("%m/%d/%Y")

def record_accounts():
    with open(file_name, "w", newline="", encoding="utf-8") as file:

        fieldnames = [
            "employee_id",
            "person_id",
            "email",
            "password",
            "created_id",
            "modified_id"
        ]

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()

        for employee_id, data in database.items():

            writer.writerow({
                "employee_id": employee_id,
                "person_id": data["person_id"],
                "email": data["email"],
                "password": data["password"],
                "created_id": data["created_id"],
                "modified_id": data["modified_id"]
            })


################This changes the frame(or widgets) showing in the window#####################

#First, let's load the file
database = load_accounts()

def show_signup():
    login_frame.pack_forget()
    forget_frame.pack_forget()
    signup_frame.pack(fill="both", expand=True)

def show_login():
    signup_frame.pack_forget()
    forget_frame.pack_forget()
    login_frame.pack(fill="both", expand=True)

def show_forget():
    login_frame.pack_forget()
    signup_frame.pack_forget()
    forget_frame.pack(fill="both", expand=True)

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
tb.Label(login_card, text="Email", font=navfont).pack(anchor="w", pady=(5, 2))
input_username = tb.Entry(login_card, textvariable=username_var, font=ourfont, width=30)
input_username.pack(pady=5, fill="x")

#this takes the password input
tb.Label(login_card, text="Password", font=navfont).pack(anchor="w", pady=(10, 2))
input_password = tb.Entry(login_card, textvariable=password_var, font=ourfont, width=30, show="*")
input_password.pack(pady=5, fill="x")

# Error Messager
error_label = tb.Label(login_card, textvariable=login_error_var, bootstyle="danger")
error_label.pack()

#confirm button
tb.Button(login_card, text="Login", bootstyle="primary", command=verify_user_n_passcode, width=60, padding=10).pack(pady=5)
#Sign-up button
tb.Button(login_card, text="Create Account", bootstyle="link", command=show_signup).pack(pady=5)
#Forget button
tb.Button(login_card, text="Forget Password?", bootstyle="link", command=show_forget).pack(pady=5)


##################################  Sign up Section   ###############################################

signup_card = tb.Frame(signup_frame, padding=25)
signup_card.place(relx=0.5, rely=0.5, anchor="center")

tb.Label(signup_card, text="User Sign-up", font=titlefont).pack(pady=(0, 15))

# Takes the user's email
tb.Label(signup_card, text="Enter Email", font=navfont).pack(anchor="w", pady=(5, 2))
input_new_email = tb.Entry(signup_card, textvariable=new_email_var, font=ourfont, width=30)
input_new_email.pack(pady=5, fill="x")

# Takes the user's password
tb.Label(signup_card, text="Enter Password", font=navfont).pack(anchor="w", pady=(5, 2))
input_new_password = tb.Entry(signup_card, textvariable=new_password_var, font=ourfont, width=30, show="*")
input_new_password.pack(pady=5, fill="x")

# reconfirm password
tb.Label(signup_card, text="Confirm Password", font=navfont).pack(anchor="w", pady=(5, 2))
input_confirm_password = tb.Entry(signup_card, textvariable=confirm_new_password_var, font=ourfont, width=30, show="*")
input_confirm_password.pack(pady=5, fill="x")

# Error Messager
error_label = tb.Label(signup_card, textvariable=signup_error_var, bootstyle="danger")
error_label.pack()

#confirm button
tb.Button(signup_card, text="Sign-up", bootstyle="primary", command=add_account, width=60, padding=10).pack(pady=5)

#Back button
tb.Button(signup_card, text="Back", bootstyle="secondary", command=show_login).pack(pady=5)


#################################### Forget Password Page ############################
forget_card = tb.Frame(forget_frame, padding=25)
forget_card.place(relx=0.5, rely=0.5, anchor="center")

tb.Label(forget_card, text="Forget Password", font=titlefont).pack(pady=(0, 15))

tb.Label(forget_card, text="Enter Email", font=navfont).pack(anchor="w", pady=(5, 2))
input_forget_username = tb.Entry(forget_card, textvariable=forget_username_var, font=ourfont, width=30)
input_forget_username.pack(pady=5, fill="x")

tb.Label(forget_card, text="Enter new password", font=navfont).pack(anchor="w", pady=(5, 2))
input_forget_username = tb.Entry(forget_card, textvariable=forget_new_password_var, font=ourfont, width=30, show="*")
input_forget_username.pack(pady=5, fill="x")

# Error Messager
forget_error_label = tb.Label(forget_card, textvariable=forget_error_var, bootstyle="danger")
forget_error_label.pack()


# Takes the user's username
tb.Label(forget_card, text="Enter Admin's Password", font=navfont).pack(anchor="w", pady=(5, 2))
input_forget_admin_password = tb.Entry(forget_card, textvariable=admin_password_var, font=ourfont, width=30, show="*")
input_forget_admin_password.pack(pady=5, fill="x")

#confirm button
tb.Button(forget_card, text="Change Password", bootstyle="primary", command=change_password, width=60, padding=10).pack(pady=5)

#Back button
tb.Button(forget_card, text="Back", bootstyle="secondary", command=show_login).pack(pady=5)


frame.mainloop()