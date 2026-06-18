import re
import os
import json
import mysql.connector
from mysql.connector import Error
import ttkbootstrap as tb  
from ttkbootstrap.constants import *
from ttkbootstrap.widgets.tableview import Tableview  
from tkinter import messagebox, StringVar
from datetime import datetime

# ==========================================
# DATABASE & FILE STORAGE SETUP
# ==========================================
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',          
    'password': 'Youaremypassword123',          
    'database': 'ecorrectdb'
}

ACCOUNTS_FILE = "accounts.json"
ACTIVE_EMPLOYEE_ID = 1 

if os.path.exists(ACCOUNTS_FILE):
    with open(ACCOUNTS_FILE, "r") as file:
        account_database = json.load(file)
else:
    account_database = {
        "Admin": ["Admin@gmail.com", "UnlimitedDataWorks"],
        "Michael Daitol": ["GelSensei@gmail.com", "1mgelodesu!"]
    }

c_dis_entry_audit = [
    {"text": "Report ID", "stretch": True},
    {"text": "Cert Type", "stretch": True},
    {"text": "Error Field", "stretch": True},
    {"text": "Original Value", "stretch": True},
    {"text": "Revised Value", "stretch": True},
    {"text": "Modified By", "stretch": True}
]

current_active_page_ref = None
all_fetched_audit_rows = []  
accessibility_labels = []  

def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            return connection
    except Error as e:
        messagebox.showerror("Database Error", f"Could not connect to MySQL Database:\n{e}")
        return None

def fetch_latest_audit_rows():
    conn = get_db_connection()
    if not conn:
        return []
    cursor = conn.cursor()
    try:
        query = """
            SELECT report_id, cert_type, error_field, original_value, revised_value, modified_by 
            FROM discrepancy_entries 
            ORDER BY report_id DESC
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        return rows
    except Error as e:
        messagebox.showerror("Database Query Error", f"Failed to retrieve audit log metrics:\n{e}")
        return []
    finally:
        cursor.close()
        conn.close()

# ==========================================
# GUI MAIN APPLICATION INITIALIZATION
# ==========================================
root = tb.Window(themename="flatly")
width = root.winfo_screenwidth() 
height = root.winfo_screenheight()
root.geometry("%dx%d" % (width, height))
root.title("PSA Error Collection System")
root.state('zoomed') 

# COLOR SCHEME CONFIGURATION
PSA_BLUE = "#4d73ff"
PSA_HEADER_BLUE = "#0066cc"

DEFAULT_TITLE_SIZE = 25
DEFAULT_BODY_SIZE = 11
MAX_IMAGE_TABLE_SIZE = 11  

font_size_title = DEFAULT_TITLE_SIZE
font_size_default = DEFAULT_BODY_SIZE
font_size_table = MAX_IMAGE_TABLE_SIZE  

certType = None
cert_choice = ""

# Authentication global variables
username_var = StringVar()
password_var = StringVar()
login_error_var = StringVar()

new_username_var = StringVar()
new_email_var = StringVar()
new_password_var = StringVar()
confirm_new_password_var = StringVar()
signup_error_var = StringVar()

forget_username_var = StringVar()
forget_new_password_var = StringVar()
admin_password_var = StringVar()
forget_error_var = StringVar()

# Form entries
death_regEntry = None
death_nameEntry = None
death_errorType = None
origEntry = None
newEntry = None
explain = None

birth_regEntry = None
youEntry = None
momEntry = None
dadEntry = None
birth_errorType = None
borigEntry = None
bnewEntry = None
bexplain = None

marriage_regEntry = None
marriage_errorType = None
applicantEntry = None  
morigEntry = None
mnewEntry = None
mexplainEntry = None

# =====================================================================
# CUSTOM LIFTED ROUNDED CARD BUTTON COMPONENT (FIXED CLIPPING BUGS)
# =====================================================================
class LiftedRoundedButton(tb.Canvas):
    def __init__(self, parent, text, image, command, compound="top", variant="default", text_size=16, bg_override=None, **kwargs):
        current_theme_bg = bg_override if bg_override else (tb.Style().lookup("TFrame", "background") or "#f8f9fa")
        super().__init__(parent, highlightthickness=0, borderwidth=0, bg=current_theme_bg, **kwargs)
        self.text = text
        self.image = image
        self.command = command
        self.compound = compound
        self.variant = variant  
        self.text_size = text_size
        self._disabled = False
        self.bg_override = bg_override
        
        self.bind("<Configure>", self.draw_card)
        self.bind("<ButtonPress-1>", self.on_press)
        self.bind("<ButtonRelease-1>", self.on_release)
        self.bind("<Enter>", self.on_hover)
        self.bind("<Leave>", self.on_leave)
        
        self.pressed = False
        self.hovered = False

    def set_disabled(self, disabled=True):
        self._disabled = disabled
        self.draw_card()

    def draw_card(self, event=None):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        if w < 10 or h < 10:
            return

        radius = 35  
        
        if self._disabled:
            face_normal = "#e9ecef" if not self.bg_override else "#0052a3"
            face_hover = face_normal
            text_color = "#adb5bd" if not self.bg_override else "#66b2ff"
            border_color = "#dee2e6" if not self.bg_override else ""
        elif self.variant == "accent":
            face_normal = "#343a40"
            face_hover = "#212529"
            text_color = "#ffffff"
            border_color = ""
        elif self.variant == "primary":
            face_normal = "#0066cc"
            face_hover = "#0052a3"
            text_color = "#ffffff"
            border_color = ""
        elif self.variant == "danger":
            face_normal = "#dc3545"
            face_hover = "#bd2130"
            text_color = "#ffffff"
            border_color = ""
        elif self.variant == "muted_danger":
            face_normal = "#d9534f"
            face_hover = "#c9302c"
            text_color = "#ffffff"
            border_color = ""
        elif self.variant == "grey_button":
            face_normal = "#6c757d"
            face_hover = "#5a6268"
            text_color = "#ffffff"
            border_color = ""
        elif self.variant == "nav_active":
            face_normal = "#0052a3"  
            face_hover = "#0052a3"
            text_color = "#ffffff"
            border_color = ""
        elif self.variant == "navbar_item":
            face_normal = "#0066cc"  
            face_hover = "#0052a3"
            text_color = "#ffffff"
            border_color = ""
        else: 
            face_normal = "#ffffff"
            face_hover = "#f1f3f5"
            text_color = "#212529"
            border_color = "#ced4da"
        
        current_theme_bg = self.bg_override if self.bg_override else (tb.Style().lookup("TFrame", "background") or "#f8f9fa")
        self.configure(bg=current_theme_bg)
        
        cx1, cy1 = 2, 2
        cx2, cy2 = w - 2, h - 2
        face_fill = face_hover if (self.hovered and not self._disabled) else face_normal
        
        if self.variant in ["navbar_item", "nav_active"]:
            outline_color = face_fill
            radius = 0 
        else:
            outline_color = border_color if border_color else face_fill

        self.create_rounded_rect(cx1, cy1, cx2, cy2, radius, fill=face_fill, outline=outline_color, width=1)
        center_x = (cx1 + cx2) / 2
        center_y = (cy1 + cy2) / 2

        if self.image:
            if self.compound == "top":
                self.create_image(center_x, center_y - 22, image=self.image)
                self.create_text(center_x, center_y + 35, text=self.text, font=("Helvetica", self.text_size, "bold"), fill=text_color, justify=CENTER, width=w - 15)
            else:
                img_w = self.image.width() if hasattr(self.image, 'width') else 24
                offset_x = (w - (img_w + 10 + (len(self.text) * (self.text_size * 0.55)))) / 2
                start_x = max(15, offset_x if offset_x > 15 else 20)
                
                self.create_image(start_x + (img_w / 2), center_y, image=self.image)
                self.create_text(start_x + img_w + 12, center_y, text=self.text, font=("Helvetica", self.text_size, "bold"), fill=text_color, anchor="w", justify=LEFT, width=w - (start_x + img_w + 20))
        else:
            self.create_text(center_x, center_y, text=self.text, font=("Helvetica", self.text_size, "bold"), fill=text_color, justify=CENTER, width=w - 20)

    def create_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        if r == 0:
            return self.create_rectangle(x1, y1, x2, y2, **kwargs)
        points = [
            x1+r, y1, x1+r, y1, x2-r, y1, x2-r, y1, x2, y1+r, x2, y1+r,
            x2, y2-r, x2, y2-r, x2, y2, x2-r, y2, x2-r, y2, x1+r, y2, x1+r, y2,
            x1, y2, x1, y2-r, x1, y2-r, x1, y1+r, x1, y1+r, x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)

    def on_press(self, event):
        if self._disabled: return
        self.pressed = True
        self.draw_card()

    def on_release(self, event):
        if self._disabled: return
        if self.pressed:
            self.pressed = False
            self.draw_card()
            if 0 <= event.x <= self.winfo_width() and 0 <= event.y <= self.winfo_height():
                if self.command:
                    self.command()

    def on_hover(self, event):
        if self._disabled: return
        self.hovered = True
        self.draw_card()

    def on_leave(self, event):
        if self._disabled: return
        self.hovered = False
        self.pressed = False
        self.draw_card()


def apply_font_sizes():
    global current_active_page_ref, font_size_default, font_size_table
    Title.config(font=("Times New Roman", font_size_title)) 
    
    style = tb.Style()
    style.configure('.', font=("Helvetica", font_size_default))          
    style.configure('TLabel', font=("Helvetica", font_size_default))     
    style.configure('TEntry', font=("Helvetica", font_size_default))     
    style.configure('TCombobox', font=("Helvetica", font_size_default))  
    
    calculated_rowheight = int(font_size_table * 2.8)
    style.configure('Treeview', font=("Helvetica", font_size_table), rowheight=calculated_rowheight)
    style.configure('Treeview.Heading', font=("Helvetica", font_size_table, "bold"))

    if current_active_page_ref and hasattr(current_active_page_ref, 'dv'):
        try:
            current_active_page_ref.dv.view.configure(font=("Helvetica", font_size_table))
            current_active_page_ref.dv.update_idletasks()
            current_active_page_ref.dv.autofit_columns()
            current_active_page_ref.dv.autoalign_columns()
        except:
            pass

def increase_font():
    global font_size_title, font_size_default
    if font_size_default < 24:  
        font_size_title += 2
        font_size_default += 2
        apply_font_sizes()
    else:
        messagebox.showinfo("Font Limit", "Maximum text font size reached.")

def decrease_font():
    global font_size_default, font_size_title
    if font_size_default > 8:  
        font_size_title -= 2
        font_size_default -= 2
        apply_font_sizes()
    else:
        messagebox.showinfo("Font Limit", "Minimum text font size reached.")

def increase_table_font():
    global font_size_table
    if font_size_table < MAX_IMAGE_TABLE_SIZE:
        font_size_table += 1
        apply_font_sizes()
    else:
        messagebox.showinfo("Font Limit", "Maximum allowed table font size reached.")

def decrease_table_font():
    global font_size_table
    if font_size_table > 7:
        font_size_table -= 1
        apply_font_sizes()
    else:
        messagebox.showinfo("Font Limit", "Minimum table font size reached.")

def reset_settings():
    confirm = messagebox.askyesno("Confirmation", "Are you sure? All settings will be restored to default.")
    if not confirm:
        return
        
    global font_size_title, font_size_default, font_size_table
    font_size_title = DEFAULT_TITLE_SIZE
    font_size_default = DEFAULT_BODY_SIZE
    font_size_table = MAX_IMAGE_TABLE_SIZE
    root.style.theme_use("flatly")
    apply_font_sizes()
    sync_navbar_theme()
    for lbl in accessibility_labels:
        if lbl.winfo_exists():
            lbl.config(foreground=PSA_HEADER_BLUE)
    messagebox.showinfo("Reset Successful", "Accessibility changes have been restored to default values.")

# --- FIXED FILE ESCAPE STRINGS HERE ---
try:
    raw_logo = tb.PhotoImage(file=r"C:\Users\Kiel\Desktop\Sophomore\PSA-Error-Collection-System\SourceCodes\images\psa.png")
    logo_image = raw_logo.subsample(8, 8) 
except Exception as e:
    print(f"Warning: Main header logo image could not be loaded. Details: {e}")
    logo_image = None

# Header Banner
Title = tb.Label(
    root, 
    text="  REPUBLIC OF THE PHILIPPINES\n  PHILIPPINE STATISTICS AUTHORITY", 
    font=("Times New Roman", font_size_title), 
    background=PSA_HEADER_BLUE,
    foreground="white",
    anchor="w",
    image=logo_image,
    compound="left",        
    padding=(30, 20),
    borderwidth=0
)
Title.pack(fill="x")

# Global Navigation Bar Setup
root.style.configure("NavFrame.TFrame", background=PSA_HEADER_BLUE, borderwidth=0, relief=FLAT)
nav_frame = tb.Frame(root, style="NavFrame.TFrame", height=45, borderwidth=0, relief=FLAT)

nav_home = LiftedRoundedButton(nav_frame, text="Home Menu", image=None, command=lambda: navigate_to(main_menu_screen), variant="navbar_item", width=160, height=45, text_size=11, bg_override=PSA_HEADER_BLUE)
nav_home.pack(side=LEFT)

nav_logs = LiftedRoundedButton(nav_frame, text="View Audit Logs", image=None, command=lambda: navigate_to(call_audit_logs_view, show_enter_new=False), variant="navbar_item", width=160, height=45, text_size=11, bg_override=PSA_HEADER_BLUE)
nav_logs.pack(side=LEFT)

nav_settings = LiftedRoundedButton(nav_frame, text="Accessibility Settings", image=None, command=lambda: navigate_to(accessibility_screen), variant="navbar_item", width=180, height=45, text_size=11, bg_override=PSA_HEADER_BLUE)
nav_settings.pack(side=LEFT)

nav_logout = LiftedRoundedButton(nav_frame, text="Logout", image=None, command=lambda: confirm_logout(), variant="navbar_item", width=120, height=45, text_size=11, bg_override=PSA_HEADER_BLUE)
nav_logout.pack(side=RIGHT)

def confirm_logout():
    if messagebox.askyesno("Logout", "Are you sure you want to log out of the system?"):
        nav_frame.pack_forget()
        navigate_to(login_screen)

def sync_navbar_theme():
    root.style.configure("NavFrame.TFrame", background=PSA_HEADER_BLUE, borderwidth=0, relief=FLAT)
    nav_frame.configure(style="NavFrame.TFrame")
    nav_home.draw_card()
    nav_logs.draw_card()
    nav_settings.draw_card()
    nav_logout.draw_card()

def update_navbar_state(current_screen):
    if current_screen in [login_screen, signup_screen, forget_screen]:
        nav_frame.pack_forget()
        return
        
    if not nav_frame.winfo_manager():
        nav_frame.pack(fill="x", before=content_frame)

    entry_screens = [entry_system_screen, birth_cert_screen, death_cert_screen, marriage_cert_screen]
    is_entry_mode = current_screen in entry_screens
    
    nav_home.set_disabled(is_entry_mode)
    nav_logs.set_disabled(is_entry_mode)
    nav_settings.set_disabled(is_entry_mode)
    nav_logout.set_disabled(False)
    
    if not is_entry_mode:
        nav_home.variant = "nav_active" if current_screen == main_menu_screen else "navbar_item"
        nav_logs.variant = "nav_active" if current_screen == call_audit_logs_view else "navbar_item"
        nav_settings.variant = "nav_active" if current_screen == accessibility_screen else "navbar_item"
        nav_home.draw_card()
        nav_logs.draw_card()
        nav_settings.draw_card()
        nav_logout.draw_card()

content_frame = tb.Frame(root, padding=20)
content_frame.pack(expand=True, fill="both")

def update_entry(event):
    global cert_choice
    cert_choice = certType.get()

def darkmode():
    root.style.theme_use("darkly")
    apply_font_sizes() 
    sync_navbar_theme()
    for lbl in accessibility_labels:
        if lbl.winfo_exists():
            lbl.config(foreground="white")

def lightmode():
    root.style.theme_use("flatly")
    apply_font_sizes()
    sync_navbar_theme()
    for lbl in accessibility_labels:
        if lbl.winfo_exists():
            lbl.config(foreground=PSA_HEADER_BLUE)

def greymode():
    root.style.theme_use("superhero")
    apply_font_sizes()
    sync_navbar_theme()
    for lbl in accessibility_labels:
        if lbl.winfo_exists():
            lbl.config(foreground="white")

# ==========================================
# TRANSITION ANIMATION ENGINE
# ==========================================
def navigate_to(screen_drawing_function, *args, **kwargs):
    global current_active_page_ref, accessibility_labels
    current_active_page_ref = None  
    accessibility_labels = [] 
    
    update_navbar_state(screen_drawing_function)
    
    for widget in content_frame.winfo_children():
        widget.destroy()
        
    loading_lbl = tb.Label(content_frame, text="Loading interface context...", font=("Helvetica", 12, "italic"), bootstyle="secondary")
    loading_lbl.pack(expand=True)
    
    root.after(250, lambda: execution_wrap(loading_lbl, screen_drawing_function, *args, **kwargs))

def execution_wrap(loader_widget, target_function, *args, **kwargs):
    loader_widget.destroy()
    target_function(*args, **kwargs)

# =====================================================================
# AUTHENTICATION BUSINESS LOGIC
# =====================================================================
def verify_user_n_passcode():
    entered_username = username_var.get().strip()
    entered_password = password_var.get().strip()

    if not entered_username or not entered_password:
        login_error_var.set("Fields cannot be empty")
        return

    for username, data in account_database.items():
        email = data[0]
        password = data[1]
    
        if entered_username == email or entered_username == username:
            if entered_password == password:
                login_error_var.set("")
                username_var.set("")
                password_var.set("")
                messagebox.showinfo("Success", f"Welcome back, {username}!")
                navigate_to(main_menu_screen)
                return
            else:
                login_error_var.set("Wrong Password")
                return
    login_error_var.set("User not found")
    
def add_account():
    new_username = new_username_var.get().strip()
    new_email = new_email_var.get().strip()
    new_password = new_password_var.get().strip()
    confirm_password = confirm_new_password_var.get().strip()

    if new_username == "" or new_email == "" or new_password == "":
        signup_error_var.set("Some fields are blank. please fill them all")
        return
    
    if new_password != confirm_password:
        signup_error_var.set("Mismatched Passwords, try again")
        return
    
    for username, data in account_database.items():
        if new_email == data[0]:
            signup_error_var.set("Email is already used in another account")
            return
        
    confirm = messagebox.askyesno("Create Account", "Do you want to create this account?")
    if confirm:
        account_database[new_username] = [new_email, new_password]
        record_accounts()
        messagebox.showinfo("Success", "Account created successfully!")
        
        new_username_var.set("")
        new_email_var.set("")
        new_password_var.set("")
        confirm_new_password_var.set("")
        signup_error_var.set("")
        
        navigate_to(login_screen)

def change_password():
    forgotten_username = forget_username_var.get().strip()
    new_user_password = forget_new_password_var.get().strip()
    admin_passkey = admin_password_var.get().strip()

    if not forgotten_username or not new_user_password or not admin_passkey:
        forget_error_var.set("Please populate all input targets.")
        return

    for username, data in account_database.items():
        email = data[0]

        if forgotten_username == username or forgotten_username == email:
            if admin_passkey != account_database["Admin"][1]:
                forget_error_var.set("Wrong Admin Password")
                return

            confirm = messagebox.askyesno("Change Password", f"Change password for '{username}'?")
            if confirm:
                account_database[username] = [email, new_user_password]
                record_accounts()
                messagebox.showinfo("Success", "Password changed successfully!")
                
                forget_username_var.set("")
                forget_new_password_var.set("")
                admin_password_var.set("")
                forget_error_var.set("")
                
                navigate_to(login_screen)
            return
    forget_error_var.set("User not found")
    
def record_accounts():
    with open(ACCOUNTS_FILE, "w") as file:
        json.dump(account_database, file, indent=4)

# ==========================================
# AUTHENTICATION VISUAL INTERFACES
# ==========================================
def login_screen():
    container = tb.Frame(content_frame, padding=30)
    container.pack(expand=True)

    current_theme = root.style.theme.name
    heading_fg = "white" if current_theme in ["darkly", "superhero"] else PSA_HEADER_BLUE

    tb.Label(container, text="Error Collection System", font=("Helvetica", 14, "italic"), foreground="grey").pack(pady=(0, 5))
    tb.Label(container, text="User Login Portal", font=("Helvetica", 22, "bold"), foreground=heading_fg).pack(pady=(0, 25))

    tb.Label(container, text="Username / Email: ", font=("Helvetica", 11)).pack(anchor="w", pady=(5, 2))
    ent_user = tb.Entry(container, textvariable=username_var, width=42)
    ent_user.pack(pady=5, fill="x")

    tb.Label(container, text="Password: ", font=("Helvetica", 11)).pack(anchor="w", pady=(5, 2))
    ent_pass = tb.Entry(container, textvariable=password_var, show="*", width=42)
    ent_pass.pack(pady=5, fill="x")

    err_lbl = tb.Label(container, textvariable=login_error_var, bootstyle="danger", font=("Helvetica", 10, "bold"))
    err_lbl.pack(pady=5)

    btn_row = tb.Frame(container)
    btn_row.pack(fill="x", pady=15)

    login_btn = LiftedRoundedButton(btn_row, text="Sign In", image=None, command=verify_user_n_passcode, variant="primary", width=350, height=45)
    login_btn.pack(pady=5, fill="x")

    links_row = tb.Frame(container)
    links_row.pack(fill="x", pady=5)
    tb.Button(links_row, text="Create Account", bootstyle="link", command=lambda: navigate_to(signup_screen)).pack(side=LEFT)
    tb.Button(links_row, text="Forgot Password?", bootstyle="link", command=lambda: navigate_to(forget_screen)).pack(side=RIGHT)

def signup_screen():
    container = tb.Frame(content_frame, padding=30)
    container.pack(expand=True)

    current_theme = root.style.theme.name
    heading_fg = "white" if current_theme in ["darkly", "superhero"] else PSA_HEADER_BLUE

    tb.Label(container, text="User Registration", font=("Helvetica", 22, "bold"), foreground=heading_fg).pack(pady=(0, 25))

    tb.Label(container, text="Enter Username", font=("Helvetica", 11)).pack(anchor="w", pady=(5, 2))
    tb.Entry(container, textvariable=new_username_var, width=42).pack(pady=5, fill="x")

    tb.Label(container, text="Enter Email Address", font=("Helvetica", 11)).pack(anchor="w", pady=(5, 2))
    tb.Entry(container, textvariable=new_email_var, width=42).pack(pady=5, fill="x")

    tb.Label(container, text="Enter Password", font=("Helvetica", 11)).pack(anchor="w", pady=(5, 2))
    tb.Entry(container, textvariable=new_password_var, show="*", width=42).pack(pady=5, fill="x")

    tb.Label(container, text="Confirm Password", font=("Helvetica", 11)).pack(anchor="w", pady=(5, 2))
    tb.Entry(container, textvariable=confirm_new_password_var, show="*", width=42).pack(pady=5, fill="x")

    tb.Label(container, textvariable=signup_error_var, bootstyle="danger", font=("Helvetica", 10, "bold")).pack(pady=5)

    btn_signup = LiftedRoundedButton(container, text="Register Account", image=None, command=add_account, variant="primary", width=350, height=45)
    btn_signup.pack(pady=10, fill="x")

    tb.Button(container, text="Back to Login Screen", bootstyle="secondary-link", command=lambda: navigate_to(login_screen)).pack()

def forget_screen():
    container = tb.Frame(content_frame, padding=30)
    container.pack(expand=True)

    current_theme = root.style.theme.name
    heading_fg = "white" if current_theme in ["darkly", "superhero"] else PSA_HEADER_BLUE

    tb.Label(container, text="Account Password Reset", font=("Helvetica", 22, "bold"), foreground=heading_fg).pack(pady=(0, 25))

    tb.Label(container, text="Target Account Username/Email", font=("Helvetica", 11)).pack(anchor="w", pady=(5, 2))
    tb.Entry(container, textvariable=forget_username_var, width=42).pack(pady=5, fill="x")

    tb.Label(container, text="Target New Password", font=("Helvetica", 11)).pack(anchor="w", pady=(5, 2))
    tb.Entry(container, textvariable=forget_new_password_var, show="*", width=42).pack(pady=5, fill="x")

    tb.Label(container, text="Admin Approval Credentials Key", font=("Helvetica", 11)).pack(anchor="w", pady=(5, 2))
    tb.Entry(container, textvariable=admin_password_var, show="*", width=42).pack(pady=5, fill="x")

    tb.Label(container, textvariable=forget_error_var, bootstyle="danger", font=("Helvetica", 10, "bold")).pack(pady=5)

    btn_reset = LiftedRoundedButton(container, text="Override Password", image=None, command=change_password, variant="primary", width=350, height=45)
    btn_reset.pack(pady=10, fill="x")

    tb.Button(container, text="Back to Login Screen", bootstyle="secondary-link", command=lambda: navigate_to(login_screen)).pack()

# ==========================================
# FIXED SQL LOGIC (RACE CONDITION RESOLVED)
# ==========================================
def save_discrepancy_to_db(registry_num, error_type, explanation, field_name, original_val, revised_val):
    conn = get_db_connection()
    if not conn:
        return False
    
    cursor = conn.cursor(buffered=True)
    try:
        # 1. GENERATE THE FORMATTED REPORT ID (YY-MM-#####)
        now = datetime.now()
        prefix = now.strftime("%y-%m-") # Yields "26-06-" for June 2026
        
        # Check the highest sequence number for the current month
        seq_query = "SELECT report_id FROM discrepancy_report WHERE report_id LIKE %s ORDER BY report_id DESC LIMIT 1"
        cursor.execute(seq_query, (prefix + '%',))
        last_row = cursor.fetchone()
        
        if last_row:
            # Extract the last 5 digits, convert to integer, and increment
            last_seq = int(last_row[0].split('-')[-1])
            new_seq = last_seq + 1
        else:
            new_seq = 1
            
        # Pad sequence with leading zeros to match 5 characters (e.g., '26-06-00001')
        generated_report_id = f"{prefix}{new_seq:05d}"

        global cert_choice
        current_cert_type = cert_choice if cert_choice else "Birth Certificate"

        # 2. INSERT INTO DISCREPANCY REPORT WITH THE EXPLICIT STR ID
        report_query = """
            INSERT INTO discrepancy_report (report_id, employee_id, registry_number, cert_type, status, created_date) 
            VALUES (%s, %s, %s, %s, 'PENDING', NOW())
        """
        cursor.execute(report_query, (generated_report_id, ACTIVE_EMPLOYEE_ID, registry_num, current_cert_type))
        
        # 3. INSERT INTO DISCREPANCY ENTRIES USING THE SAME GENERATED STR ID
        entry_query = """
            INSERT INTO discrepancy_entries (report_id, person_name, cert_type, explanation, error_field, original_value, revised_value, modified_by, modified_date)
            VALUES (%s, NULL, %s, %s, %s, %s, %s, %s, NOW())
        """
        cursor.execute(entry_query, (generated_report_id, current_cert_type, explanation, field_name, original_val, revised_val, ACTIVE_EMPLOYEE_ID))
        
        conn.commit()
        return True
    except Error as e:
        conn.rollback()
        messagebox.showerror("SQL Execution Error", f"Transaction rolled back. Details:\n{e}")
        return False
    finally:
        cursor.close()
        conn.close()
# ==========================================
# FORM SUBMISSIONS & VALIDATIONS
# ==========================================
def death_confirm():
    global death_regEntry, death_nameEntry, death_errorType, origEntry, newEntry, explain, cert_choice
    reg_pattern = r"^\d{4}-\d{7}$"
    if death_regEntry.get() == "":
        messagebox.showerror("Error", "Please input the proper Registration Number (ex. YYYY-XXXXXXX).")
        return
    elif not re.match(reg_pattern, death_regEntry.get()):
        messagebox.showerror("Error", "Invalid format! Registration Number must follow YYYY-XXXXXXX (e.g., 2026-1234567).")
        return
    elif death_nameEntry.get() == "":
        messagebox.showerror("Error", "Please specify the deceased individual's Name.")
        return
    elif death_errorType.get().strip() == "":
        messagebox.showerror("Error", "Please specify an error type.")
        return
    elif origEntry.get() == "":
        messagebox.showerror("Error", "Please specify the erroneous value.")
        return
    elif newEntry.get() == "":
        messagebox.showerror("Error", "Please specify the new value.")
        return
    elif explain.get() == "":
        messagebox.showerror("Error", "Please indicate the reason for this change")
        return
    
    final = messagebox.askyesno("Confirmation", "Are you sure with the information inputted?")
    if final:
        success = save_discrepancy_to_db(
            registry_num=death_regEntry.get(),
            error_type=death_errorType.get(),
            explanation=explain.get(),
            field_name=death_errorType.get(), 
            original_val=origEntry.get(),
            revised_val=newEntry.get()
        )
        if success:
            cert_choice = "" # Global variable reset safety step
            messagebox.showinfo("Success", "Data successfully saved to MySQL database!")
            navigate_to(call_audit_logs_view, show_enter_new=True)
    else:
        messagebox.showinfo("Cancelled Input", "Your Entry has been Cancelled.")

def birth_confirm():
    global birth_regEntry, birth_errorType, youEntry, momEntry, dadEntry, borigEntry, bnewEntry, bexplain, cert_choice
    reg_pattern = r"^\d{4}-\d{7}$"
    if birth_regEntry.get() == "":
        messagebox.showerror("Error", "Please input the proper Registration Number (ex. YYYY-XXXXXXX).")
        return
    elif not re.match(reg_pattern, birth_regEntry.get()):
        messagebox.showerror("Error", "Invalid format! Registration Number must follow YYYY-XXXXXXX (e.g., 2026-1234567).")
        return
    elif birth_errorType.get().strip() == "":
        messagebox.showerror("Error", "Please specify an error type.")
        return
    elif youEntry.get() == "":
        messagebox.showerror("Error", "Please Specify the Document owner's Name")
        return
    elif momEntry.get() == "":
        messagebox.showerror("Error", "Please Specify the Mother's Name")
        return
    elif dadEntry.get() == "":
        messagebox.showerror("Error", "Please Specify the Father's Name")
        return
    elif borigEntry.get() == "":
        messagebox.showerror("Error", "Please specify the erroneous value.")
        return
    elif bnewEntry.get() == "":
        messagebox.showerror("Error", "Please specify the new value.")
        return
    elif bexplain.get() == "":
        messagebox.showerror("Error", "Please indicate the reason for this change")
        return
    
    final = messagebox.askyesno("Confirmation", "Are you sure with the information inputted?")
    if final:
        success = save_discrepancy_to_db(
            registry_num=birth_regEntry.get(),
            error_type=birth_errorType.get(),
            explanation=bexplain.get(),
            field_name=birth_errorType.get(),
            original_val=borigEntry.get(),
            revised_val=bnewEntry.get()
        )
        if success:
            cert_choice = "" # Global variable reset safety step
            messagebox.showinfo("Success", "Data successfully saved to MySQL database!")
            navigate_to(call_audit_logs_view, show_enter_new=True)
    else:
        messagebox.showinfo("Cancelled Input", "Your Entry has been Cancelled.")

def marriage_confirm():
    global marriage_regEntry, marriage_errorType, applicantEntry, morigEntry, mnewEntry, mexplainEntry, cert_choice
    reg_pattern = r"^\d{4}-\d{7}$"
    if marriage_regEntry.get() == "":
        messagebox.showerror("Error", "Please input the proper Registration Number (ex. YYYY-XXXXXXX).")
        return
    elif not re.match(reg_pattern, marriage_regEntry.get()):
        messagebox.showerror("Error", "Invalid format! Registration Number must follow YYYY-XXXXXXX (e.g., 2026-1234567).")
        return
    elif marriage_errorType.get().strip() == "":
        messagebox.showerror("Error", "Please specify an error type.")
        return
    elif applicantEntry.get() == "":  
        messagebox.showerror("Error", "Please specify the applicant's name.")
        return
    elif morigEntry.get() == "":
        messagebox.showerror("Error", "Please specify the erroneous value.")
        return
    elif mnewEntry.get() == "":
        messagebox.showerror("Error", "Please specify the new value.")
        return
    elif mexplainEntry.get() == "": 
        messagebox.showerror("Error", "Please indicate the reason for this change")
        return
    
    final = messagebox.askyesno("Confirmation", "Are you sure with the information inputted?")
    if final:
        success = save_discrepancy_to_db(
            registry_num=marriage_regEntry.get(),
            error_type=marriage_errorType.get(),
            explanation=mexplainEntry.get(),
            field_name=marriage_errorType.get(),
            original_val=morigEntry.get(),
            revised_val=mnewEntry.get()
        )
        if success:
            cert_choice = "" # Global variable reset safety step
            messagebox.showinfo("Success", "Data successfully saved to MySQL database!")
            navigate_to(call_audit_logs_view, show_enter_new=True)
    else:
        messagebox.showinfo("Cancelled Input", "Your Entry has been Cancelled.")

# =====================================================================
# CENTRALIZED SCREEN DRAWING CONTROLLERS
# =====================================================================
def birth_cert_screen():
    global birth_regEntry, youEntry, momEntry, dadEntry, birth_errorType, borigEntry, bnewEntry, bexplain
    container = tb.Frame(content_frame, padding=30)
    container.pack(expand=True, fill="both")
    container.columnconfigure(1, weight=1)

    tb.Label(container, text="Registry Number: ", anchor="w").grid(row=0, column=0, sticky="w", pady=8, padx=10)
    birth_regEntry = tb.Entry(container)
    birth_regEntry.grid(row=0, column=1, sticky="ew", pady=8, padx=10)

    tb.Label(container, text="Name: ", anchor="w").grid(row=1, column=0, sticky="w", pady=8, padx=10)
    youEntry = tb.Entry(container)
    youEntry.grid(row=1, column=1, sticky="ew", pady=8, padx=10)

    tb.Label(container, text="Mother's Maiden Name: ", anchor="w").grid(row=2, column=0, sticky="w", pady=8, padx=10)
    momEntry = tb.Entry(container)
    momEntry.grid(row=2, column=1, sticky="ew", pady=8, padx=10)

    tb.Label(container, text="Father's Name: ", anchor="w").grid(row=3, column=0, sticky="w", pady=8, padx=10)
    dadEntry = tb.Entry(container)
    dadEntry.grid(row=3, column=1, sticky="ew", pady=8, padx=10)
   
    tb.Label(container, text="Select an Error: ", anchor="w").grid(row=4, column=0, sticky="w", pady=8, padx=10)
    bErrors = ["Date of Birth", "Sex", "Place of Birth", "Father Details", "Mother Details", "Birth Order", "Type of Birth"]
    birth_errorType = tb.Combobox(container, values=bErrors, state='readonly')
    birth_errorType.set(" ")
    birth_errorType.grid(row=4, column=1, sticky="ew", pady=8, padx=10)
    
    tb.Label(container, text="Erroneous Value: ", anchor="w").grid(row=5, column=0, sticky="w", pady=8, padx=10)
    borigEntry = tb.Entry(container)
    borigEntry.grid(row=5, column=1, sticky="ew", pady=8, padx=10)
    
    tb.Label(container, text="New Value: ", anchor="w").grid(row=6, column=0, sticky="w", pady=8, padx=10)
    bnewEntry = tb.Entry(container)
    bnewEntry.grid(row=6, column=1, sticky="ew", pady=8, padx=10)

    tb.Label(container, text="Explanation for the Change: ", anchor="w").grid(row=7, column=0, sticky="w", pady=8, padx=10)
    bexplain = tb.Entry(container)
    bexplain.grid(row=7, column=1, sticky="ew", pady=8, padx=10)

    row_btn = tb.Frame(container)
    row_btn.grid(row=8, column=0, columnspan=2, pady=30)
    
    close_but = LiftedRoundedButton(row_btn, text="Cancel", image=None, command=lambda: navigate_to(entry_system_screen), variant="default", width=180, height=45)
    close_but.pack(side=LEFT, padx=10)
    
    test_but = LiftedRoundedButton(row_btn, text="Confirm", image=None, command=birth_confirm, variant="primary", width=180, height=45)
    test_but.pack(side=LEFT, padx=10)

def death_cert_screen():
    global death_regEntry, death_nameEntry, death_errorType, origEntry, newEntry, explain
    container = tb.Frame(content_frame, padding=30)
    container.pack(expand=True, fill="both")
    container.columnconfigure(1, weight=1)

    tb.Label(container, text="Registry Number: ", anchor="w").grid(row=0, column=0, sticky="w", pady=8, padx=10)
    death_regEntry = tb.Entry(container)
    death_regEntry.grid(row=0, column=1, sticky="ew", pady=8, padx=10)

    tb.Label(container, text="Name: ", anchor="w").grid(row=1, column=0, sticky="w", pady=8, padx=10)
    death_nameEntry = tb.Entry(container)
    death_nameEntry.grid(row=1, column=1, sticky="ew", pady=8, padx=10)
   
    tb.Label(container, text="Select an Error: ", anchor="w").grid(row=2, column=0, sticky="w", pady=8, padx=10)
    bErrors = ["Name", "Date of death", "Sex", "Age at Time of death", "Place of death", "Registration of death (Date)", "Certification of death (Date)"]
    death_errorType = tb.Combobox(container, values=bErrors, state='readonly')
    death_errorType.set(" ")
    death_errorType.grid(row=2, column=1, sticky="ew", pady=8, padx=10)
    
    tb.Label(container, text="Erroneous Value: ", anchor="w").grid(row=3, column=0, sticky="w", pady=8, padx=10)
    origEntry = tb.Entry(container)
    origEntry.grid(row=3, column=1, sticky="ew", pady=8, padx=10)
    
    tb.Label(container, text="New Value: ", anchor="w").grid(row=4, column=0, sticky="w", pady=8, padx=10)
    newEntry = tb.Entry(container)
    newEntry.grid(row=4, column=1, sticky="ew", pady=8, padx=10)

    tb.Label(container, text="Explanation for the Change: ", anchor="w").grid(row=5, column=0, sticky="w", pady=8, padx=10)
    explain = tb.Entry(container)
    explain.grid(row=5, column=1, sticky="ew", pady=8, padx=10)

    row_btn = tb.Frame(container)
    row_btn.grid(row=6, column=0, columnspan=2, pady=30)
    
    close_but = LiftedRoundedButton(row_btn, text="Cancel", image=None, command=lambda: navigate_to(entry_system_screen), variant="default", width=180, height=45)
    close_but.pack(side=LEFT, padx=10)
    
    test_but = LiftedRoundedButton(row_btn, text="Confirm", image=None, command=death_confirm, variant="primary", width=180, height=45)
    test_but.pack(side=LEFT, padx=10)

def marriage_cert_screen():
    global marriage_regEntry, marriage_errorType, applicantEntry, morigEntry, mnewEntry, mexplainEntry
    container = tb.Frame(content_frame, padding=30)
    container.pack(expand=True, fill="both")
    container.columnconfigure(1, weight=1)

    tb.Label(container, text="Registry Number: ", anchor="w").grid(row=0, column=0, sticky="w", pady=8, padx=10)
    marriage_regEntry = tb.Entry(container)
    marriage_regEntry.grid(row=0, column=1, sticky="ew", pady=8, padx=10)
   
    tb.Label(container, text="Select an Error: ", anchor="w").grid(row=1, column=0, sticky="w", pady=8, padx=10)
    bErrors = ["Name of Husband", "Name of Spouse", "Date of Marriage", "Sex", "Age at Time of Marriage", "Place of Marriage", "Registration of Marriage (Date)", "Certification of Marriage (Date)"]
    marriage_errorType = tb.Combobox(container, values=bErrors, state='readonly')
    marriage_errorType.set(" ")
    marriage_errorType.grid(row=1, column=1, sticky="ew", pady=8, padx=10)
    
    tb.Label(container, text="Applicant Name: ", anchor="w").grid(row=2, column=0, sticky="w", pady=8, padx=10)
    applicantEntry = tb.Entry(container)
    applicantEntry.grid(row=2, column=1, sticky="ew", pady=8, padx=10)

    tb.Label(container, text="Erroneous Value: ", anchor="w").grid(row=3, column=0, sticky="w", pady=8, padx=10)
    morigEntry = tb.Entry(container)
    morigEntry.grid(row=3, column=1, sticky="ew", pady=8, padx=10)

    tb.Label(container, text="New Value: ", anchor="w").grid(row=4, column=0, sticky="w", pady=8, padx=10)
    mnewEntry = tb.Entry(container)
    mnewEntry.grid(row=4, column=1, sticky="ew", pady=8, padx=10)

    tb.Label(container, text="Explanation for the Change: ", anchor="w").grid(row=5, column=0, sticky="w", pady=8, padx=10)
    mexplainEntry = tb.Entry(container)
    mexplainEntry.grid(row=5, column=1, sticky="ew", pady=8, padx=10)

    row_btn = tb.Frame(container)
    row_btn.grid(row=6, column=0, columnspan=2, pady=30)
    
    close_but = LiftedRoundedButton(row_btn, text="Cancel", image=None, command=lambda: navigate_to(entry_system_screen), variant="default", width=180, height=45)
    close_but.pack(side=LEFT, padx=10)
    
    test_but = LiftedRoundedButton(row_btn, text="Confirm", image=None, command=marriage_confirm, variant="primary", width=180, height=45)
    test_but.pack(side=LEFT, padx=10)

def dispatch_choice():   
    if cert_choice == "Death Certificate":
        navigate_to(death_cert_screen)
    elif cert_choice == "Birth Certificate":
        navigate_to(birth_cert_screen)
    elif cert_choice == "Marriage Certificate":
        navigate_to(marriage_cert_screen)
    elif cert_choice == "":
        messagebox.showwarning("Warning", "Please select a Certificate Type first.")

# ==========================================
# ACCESSIBILITY CONFIGURATION MENU
# ==========================================
def accessibility_screen():
    global accessibility_labels
    container = tb.Frame(content_frame, padding=30)
    container.pack(expand=True, fill="both")

    BTN_W = 260
    BTN_H = 50
    current_theme = root.style.theme.name
    heading_fg = "white" if current_theme in ["darkly", "superhero"] else PSA_HEADER_BLUE

    # --- ROW 1: MAIN BACKGROUND ---
    lbl1 = tb.Label(container, text="Main Background", font=("Helvetica", 16, "bold"), foreground=heading_fg)
    lbl1.pack(anchor="w", pady=(10, 5), padx=40)
    accessibility_labels.append(lbl1)
    
    row1 = tb.Frame(container)
    row1.pack(fill="x", pady=(0, 20), padx=40)

    LiftedRoundedButton(row1, text="Light Mode", image=None, command=lightmode, variant="default", width=BTN_W, height=BTN_H).pack(side=LEFT, padx=10)
    LiftedRoundedButton(row1, text="Dark Mode", image=None, command=darkmode, variant="default", width=BTN_W, height=BTN_H).pack(side=LEFT, padx=10)
    LiftedRoundedButton(row1, text="Gray Mode", image=None, command=greymode, variant="default", width=BTN_W, height=BTN_H).pack(side=LEFT, padx=10)

    # --- ROW 2: GENERAL TEXT SIZE ---
    lbl2 = tb.Label(container, text="General Text Size", font=("Helvetica", 16, "bold"), foreground=heading_fg)
    lbl2.pack(anchor="w", pady=(10, 5), padx=40)
    accessibility_labels.append(lbl2)
    
    row2 = tb.Frame(container)
    row2.pack(fill="x", pady=(0, 20), padx=40)

    LiftedRoundedButton(row2, text="Increase Font Size (+)", image=None, command=increase_font, variant="default", width=BTN_W, height=BTN_H).pack(side=LEFT, padx=10)
    LiftedRoundedButton(row2, text="Decrease Font Size (-)", image=None, command=decrease_font, variant="default", width=BTN_W, height=BTN_H).pack(side=LEFT, padx=10)

    # --- ROW 3: AUDIT LOG TEXT SIZE ---
    lbl3 = tb.Label(container, text="Audit Log Text Size", font=("Helvetica", 16, "bold"), foreground=heading_fg)
    lbl3.pack(anchor="w", pady=(10, 5), padx=40)
    accessibility_labels.append(lbl3)
    
    row3 = tb.Frame(container)
    row3.pack(fill="x", pady=(0, 20), padx=40)

    LiftedRoundedButton(row3, text="Increase Table Font (+)", image=None, command=increase_table_font, variant="default", width=BTN_W, height=BTN_H).pack(side=LEFT, padx=10)
    LiftedRoundedButton(row3, text="Decrease Table Font (-)", image=None, command=decrease_table_font, variant="default", width=BTN_W, height=BTN_H).pack(side=LEFT, padx=10)

    # --- ROW 4: SYSTEM COMMAND ACTIONS ---
    row4 = tb.Frame(container)
    row4.pack(fill="x", pady=(30, 0), padx=40)

    LiftedRoundedButton(row4, text="Reset Settings", image=None, command=reset_settings, variant="primary", width=BTN_W, height=BTN_H).pack(side=LEFT, padx=10)
    LiftedRoundedButton(row4, text="Back to Main Menu", image=None, command=lambda: navigate_to(main_menu_screen), variant="muted_danger", width=BTN_W, height=BTN_H).pack(side=LEFT, padx=10)

# =====================================================================
# ENTRY SYSTEM CONTAINER MAIN WINDOW
# =====================================================================
def entry_system_screen():
    global certType, cert_choice
    container = tb.Frame(content_frame, padding=30)
    container.pack(expand=True, fill="both")
    container.columnconfigure(1, weight=1)

    tb.Label(container, text="Certificate Type: ", anchor="w").grid(row=0, column=0, sticky="w", pady=25, padx=10)
    
    certificates = ["Birth Certificate", "Death Certificate", "Marriage Certificate"]
    certType = tb.Combobox(container, values=certificates, state='readonly')
    certType.bind("<<ComboboxSelected>>", update_entry)  
    certType.set(cert_choice if cert_choice else "")
    certType.grid(row=0, column=1, sticky="ew", pady=25, padx=10)

    row_btn = tb.Frame(container)
    row_btn.grid(row=1, column=0, columnspan=2, pady=40)

    # Clean cert state on explicit exit
    def exit_workflow():
        global cert_choice
        cert_choice = ""
        navigate_to(main_menu_screen)

    LiftedRoundedButton(row_btn, text="Cancel Workflow", image=None, command=exit_workflow, variant="default", width=220, height=45).pack(side=LEFT, padx=15)
    LiftedRoundedButton(row_btn, text="Next", image=None, command=dispatch_choice, variant="primary", width=220, height=45).pack(side=LEFT, padx=15)

# ==========================================
# OBJECT-ORIENTED AUDIT LOGS IMPLEMENTATION
# ==========================================
class AuditLogPage(tb.Frame):
    def __init__(self, parent, controller, show_enter_new=False):
        super().__init__(parent)
        titlefont = ("Helvetica", 18, "bold")
        ourfont = ("Helvetica", 12)

        mainframe = tb.Frame(self)
        mainframe.pack(fill="both", expand=True)

        headerframe = tb.Frame(mainframe)
        headerframe.pack(fill="x", padx=20, pady=10)

        tb.Label(headerframe, text="Audit Logs", font=titlefont).pack(anchor="w")
        tb.Label(headerframe, text="Modifications made by employees", font=ourfont).pack(anchor="w")
        
        utility_frame = tb.Frame(headerframe)
        utility_frame.pack(fill="x", pady=(10, 0))

        tb.Button(utility_frame, text="Refresh View", bootstyle="outline-secondary", command=self.refresh_table).pack(side=LEFT, padx=(0, 20))
        
        tb.Label(utility_frame, text="🔍 Search: ", font=("Helvetica", 11)).pack(side=LEFT)
        self.search_var = tb.StringVar()
        self.search_var.trace_add("write", self.execute_live_filter)
        
        self.search_entry = tb.Entry(utility_frame, textvariable=self.search_var, width=35, bootstyle="info")
        self.search_entry.pack(side=LEFT, padx=5)
        
        tableframe = tb.Frame(mainframe)
        tableframe.pack(fill="both", expand=True, padx=20, pady=10)
        tableframe.grid_rowconfigure(0, weight=1)
        tableframe.grid_columnconfigure(0, weight=1)

        self.dv = tb.widgets.tableview.Tableview(
            master=tableframe,
            paginated=True,
            searchable=False,  
            bootstyle=SUCCESS,
            pagesize=10,
        )
        self.dv.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        self.btn_row = tb.Frame(mainframe)
        self.btn_row.pack(fill="x", padx=20, pady=(0, 15))

        self.back_menu_cnv = LiftedRoundedButton(
            self.btn_row, text="Back to Main Menu", image=None, command=lambda: navigate_to(main_menu_screen),
            variant="muted_danger", width=200, height=40, text_size=11
        )
        self.back_menu_cnv.pack(side=LEFT)

        if show_enter_new:
            tb.Button(self.btn_row, text="➕ Enter New Record", bootstyle="primary", command=lambda: navigate_to(entry_system_screen)).pack(side=RIGHT)
        self.refresh_table()

    def refresh_table(self):
        global all_fetched_audit_rows
        all_fetched_audit_rows = fetch_latest_audit_rows()
        self.search_var.set("")
        self.render_table_rows(all_fetched_audit_rows)

    def render_table_rows(self, dataset):
        focused_widget = self.focus_get()
        has_focus = (focused_widget == self.search_entry)

        self.dv.delete_rows()
        self.dv.build_table_data(c_dis_entry_audit, dataset)  
        self.dv.load_table_data()   
        self.dv.autofit_columns()   
        self.dv.autoalign_columns()

        if has_focus:
            self.search_entry.focus_set()
            self.search_entry.icursor(END)

    def execute_live_filter(self, *args):
        global all_fetched_audit_rows
        query = self.search_var.get().strip().lower()
        if not query:
            self.render_table_rows(all_fetched_audit_rows)
            return

        filtered_results = []
        for row in all_fetched_audit_rows:
            row_as_strings = [str(cell).lower() for cell in row]
            if any(query in cell_str for cell_str in row_as_strings):
                filtered_results.append(row)
        self.render_table_rows(filtered_results)


def call_audit_logs_view(show_enter_new=False):
    global current_active_page_ref
    page_instance = AuditLogPage(content_frame, root, show_enter_new=show_enter_new)
    page_instance.pack(fill="both", expand=True)
    current_active_page_ref = page_instance  
    apply_font_sizes()                       

# ==========================================
# MODERN FLAT TWO-COLUMN MAIN MENU GRID
# ==========================================
def main_menu_screen():
    username = "Kiel"  
    # --- FIXED FILE ESCAPE STRINGS HERE ---
    base_path = rf"C:\Users\{username}\Desktop\Sophomore\PSA-Error-Collection-System\SourceCodes\images"

    try:
        raw_plus = tb.PhotoImage(file=f"{base_path}/1.png")
        plus_icon = raw_plus.subsample(13, 13) 
    except Exception as e:
        print(f"Could not load plus image: {e}")
        plus_icon = None  

    try:
        raw_paper = tb.PhotoImage(file=f"{base_path}/2.png")
        paper_icon = raw_paper.subsample(10, 10) 
    except Exception as e:
        print(f"Could not load paper image: {e}")
        paper_icon = None

    try:
        raw_gear = tb.PhotoImage(file=f"{base_path}/3.png")
        gear_icon = raw_gear.subsample(10, 10)
    except Exception as e:
        print(f"Could not load gear image: {e}")
        gear_icon = None

    main_container = tb.Frame(content_frame, padding=50)
    main_container.pack(expand=True, fill="both")
    
    main_container.columnconfigure(0, weight=1, uniform="group1")
    main_container.columnconfigure(1, weight=1, uniform="group1")
    main_container.rowconfigure(0, weight=1)

    btn_create = LiftedRoundedButton(
        main_container, text="\nNew Entry", image=plus_icon, compound="top",
        command=lambda: navigate_to(entry_system_screen), width=320, height=200, variant="default", text_size=20
    )
    btn_create.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

    right_sub_container = tb.Frame(main_container)
    right_sub_container.grid(row=0, column=1, sticky="nsew")
    right_sub_container.columnconfigure(0, weight=1)
    right_sub_container.rowconfigure(0, weight=1, uniform="right_rows")
    right_sub_container.rowconfigure(1, weight=1, uniform="right_rows")

    btn_logs = LiftedRoundedButton(
        right_sub_container, text="     View Logs", image=paper_icon, compound="left",
        command=lambda: navigate_to(call_audit_logs_view, show_enter_new=False), width=320, height=90, variant="default", text_size=18
    )
    btn_logs.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

    btn_settings = LiftedRoundedButton(
        right_sub_container, text="         Settings and\n         Accessibility", image=gear_icon, compound="left",
        command=lambda: navigate_to(accessibility_screen), width=320, height=90, variant="default", text_size=18
    )
    btn_settings.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)

    main_container.img_ref1 = plus_icon
    main_container.img_ref2 = paper_icon
    main_container.img_ref3 = gear_icon

# Application Entry Point Redirect
navigate_to(login_screen)
apply_font_sizes()

root.mainloop()