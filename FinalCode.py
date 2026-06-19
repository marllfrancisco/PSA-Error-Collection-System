import re
import os
import json
import random
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
    'password': '',          
    'database': 'ecorrectdb'
}

ACCOUNTS_FILE = "accounts.json"
EMPLOYEE_LOGS_FILE = "employee_logs.json"

# State Tracking Engine Cache
CURRENT_LOGGED_IN_USER = "Guest"
otp_requests_database = {} # Format: { "username": {"otp": "123456", "timestamp": datetime} }

if os.path.exists(ACCOUNTS_FILE):
    with open(ACCOUNTS_FILE, "r") as file:
        account_database = json.load(file)
else:
    account_database = {
        "Admin": ["Admin@gmail.com", "123"],
        "Michael Daitol": ["GelSensei@gmail.com", "1mgelodesu!"]
    }

def log_employee_action(username, action):
    """Logs security lifecycle parameters cleanly into local JSON audit maps"""
    logs = []
    if os.path.exists(EMPLOYEE_LOGS_FILE):
        try:
            with open(EMPLOYEE_LOGS_FILE, "r") as file:
                logs = json.load(file)
        except:
            logs = []
            
    now = datetime.now()
    new_log = {
        "Username": username,
        "Action": action,
        "Date": now.strftime("%Y-%m-%d"),
        "Time": now.strftime("%H:%M:%S")
    }
    logs.append(new_log)
    with open(EMPLOYEE_LOGS_FILE, "w") as file:
        json.dump(logs, file, indent=4)

c_dis_entry_audit = [
    {"text": "Report ID", "stretch": True},
    {"text": "Cert Type", "stretch": True},
    {"text": "Error Field", "stretch": True},
    {"text": "Original Value", "stretch": True},
    {"text": "Revised Value", "stretch": True},
    {"text": "Modified By", "stretch": True}
]

c_employee_logs_headers = [
    {"text": "Username", "stretch": True},
    {"text": "Action", "stretch": True},
    {"text": "Date", "stretch": True},
    {"text": "Time", "stretch": True}
]

c_requests_headers = [
    {"text": "Target Username", "stretch": True},
    {"text": "Generated OTP Code", "stretch": True},
    {"text": "Request Timestamp", "stretch": True}
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
            ORDER BY modified_date DESC
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

# IMAGE CONFIGURATION SCALE FACTOR
icon_scale_factor = 20

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
entered_otp_var = StringVar()
reset_new_password_var = StringVar()
reset_confirm_password_var = StringVar()
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
# CUSTOM LIFTED ROUNDED CARD BUTTON COMPONENT
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
        
        # Pull the correct parent container background dynamically based on active theme
        current_theme_bg = self.bg_override if self.bg_override else (tb.Style().lookup("TFrame", "background") or "#f8f9fa")
        self.configure(bg=current_theme_bg)
        
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
            face_normal = "#dc3545"
            face_hover = "#c82333"
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
            # =========================================================
            # DYNAMIC THEME COLOR SAMPLER (FOR 'variant="default"')
            # =========================================================
            current_theme = tb.Style().theme.name
            
            if current_theme == "darkly":      # Dark Mode Style Profile
                face_normal = "#3a3a3a"
                face_hover = "#4a4a4a"
                text_color = "#ffffff"
                border_color = "#444444"
            elif current_theme == "superhero":  # Grey Mode Style Profile
                face_normal = "#2b3e50"
                face_hover = "#34495e"
                text_color = "#ffffff"
                border_color = "#4e5d6c"
            else:                              # Light Mode Profile (flatly)
                face_normal = "#ffffff"
                face_hover = "#f1f3f5"
                text_color = "#212529"
                border_color = "#ced4da"
        
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
                spacing = 10
                
                approx_text_width = len(self.text) * (self.text_size * 0.6)
                total_content_width = img_w + spacing + approx_text_width
                
                start_x = max(20, center_x - (total_content_width / 2))
                
                self.create_image(start_x + (img_w / 2), center_y, image=self.image)
                self.create_text(start_x + img_w + spacing, center_y, text=self.text, font=("Helvetica", self.text_size, "bold"), fill=text_color, anchor="w", justify=LEFT, width=w - (start_x + img_w + 10))
        else:
            self.create_text(center_x, center_y, text=self.text, font=("Helvetica", self.text_size, "bold"), fill=text_color, justify=CENTER, width=w - 20)

    def create_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        if r == 0:
            return self.create_rectangle(x1, y1, x2, y2, **kwargs)
        points = [
            x1+r, y1, x1+r, y1, 
            x2-r, y1, x2-r, y1, 
            x2, y1,               
            x2, y1+r, x2, y1+r, 
            x2, y2-r, x2, y2-r, 
            x2, y2, 
            x2-r, y2, x2-r, y2, 
            x1+r, y2, x1+r, y2, 
            x1, y2, 
            x1, y2-r, x1, y2-r, 
            x1, y1+r, x1, y1+r, 
            x1, y1
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

try:
    raw_logo = tb.PhotoImage(file=r"/Users/mac/Desktop/system_image/psa.png")
    logo_image = raw_logo.subsample(8, 8) 
except Exception as e:
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

nav_home = LiftedRoundedButton(nav_frame, text="Home Menu", image=None, command=lambda: navigate_to(main_menu_screen), variant="navbar_item", width=140, height=45, text_size=11, bg_override=PSA_HEADER_BLUE)
nav_home.pack(side=LEFT)

nav_logs = LiftedRoundedButton(nav_frame, text="View Audit Logs", image=None, command=lambda: navigate_to(call_audit_logs_view, show_enter_new=False), variant="navbar_item", width=140, height=45, text_size=11, bg_override=PSA_HEADER_BLUE)
nav_logs.pack(side=LEFT)

# Admin Unique Navigation Item Stubs
nav_emp_logs = LiftedRoundedButton(nav_frame, text="Employee Logs", image=None, command=lambda: navigate_to(call_employee_logs_view), variant="navbar_item", width=140, height=45, text_size=11, bg_override=PSA_HEADER_BLUE)
nav_create_acc = LiftedRoundedButton(nav_frame, text="Create Account", image=None, command=lambda: navigate_to(signup_screen), variant="navbar_item", width=140, height=45, text_size=11, bg_override=PSA_HEADER_BLUE)
nav_requests = LiftedRoundedButton(nav_frame, text="Requests", image=None, command=lambda: navigate_to(call_requests_view), variant="navbar_item", width=140, height=45, text_size=11, bg_override=PSA_HEADER_BLUE)

nav_settings = LiftedRoundedButton(nav_frame, text="Accessibility Settings", image=None, command=lambda: navigate_to(accessibility_screen), variant="navbar_item", width=180, height=45, text_size=11, bg_override=PSA_HEADER_BLUE)
nav_settings.pack(side=LEFT)

nav_logout = LiftedRoundedButton(nav_frame, text="Logout", image=None, command=lambda: confirm_logout(), variant="navbar_item", width=120, height=45, text_size=11, bg_override=PSA_HEADER_BLUE)
nav_logout.pack(side=RIGHT)

def confirm_logout():
    if messagebox.askyesno("Logout", "Are you sure you want to log out of the system?"):
        global CURRENT_LOGGED_IN_USER
        CURRENT_LOGGED_IN_USER = "Guest"
        nav_frame.pack_forget()
        navigate_to(login_screen)

def sync_navbar_theme():
    root.style.configure("NavFrame.TFrame", background=PSA_HEADER_BLUE, borderwidth=0, relief=FLAT)
    nav_frame.configure(style="NavFrame.TFrame")
    nav_home.draw_card()
    nav_logs.draw_card()
    nav_emp_logs.draw_card()
    nav_create_acc.draw_card()
    nav_requests.draw_card()
    nav_settings.draw_card()
    nav_logout.draw_card()

def update_navbar_state(current_screen):
    if current_screen in [login_screen, signup_screen if CURRENT_LOGGED_IN_USER != "admin" else None, forget_screen, otp_verification_screen, reset_password_entry_screen]:
        nav_frame.pack_forget()
        return
        
    if not nav_frame.winfo_manager():
        nav_frame.pack(fill="x", before=content_frame)

    if CURRENT_LOGGED_IN_USER == "admin":
        nav_emp_logs.pack(side=LEFT, after=nav_logs)
        nav_create_acc.pack(side=LEFT, after=nav_emp_logs)
        nav_requests.pack(side=LEFT, after=nav_create_acc)
    else:
        nav_emp_logs.pack_forget()
        nav_create_acc.pack_forget()
        nav_requests.pack_forget()

    entry_screens = [entry_system_screen, birth_cert_screen, death_cert_screen, marriage_cert_screen]
    is_entry_mode = current_screen in entry_screens
    
    nav_home.set_disabled(is_entry_mode)
    nav_logs.set_disabled(is_entry_mode)
    nav_emp_logs.set_disabled(is_entry_mode)
    nav_create_acc.set_disabled(is_entry_mode)
    nav_requests.set_disabled(is_entry_mode)
    nav_settings.set_disabled(is_entry_mode)
    nav_logout.set_disabled(False)
    
    if not is_entry_mode:
        nav_home.variant = "nav_active" if current_screen == main_menu_screen else "navbar_item"
        nav_logs.variant = "nav_active" if current_screen == call_audit_logs_view else "navbar_item"
        nav_emp_logs.variant = "nav_active" if current_screen == call_employee_logs_view else "navbar_item"
        nav_create_acc.variant = "nav_active" if current_screen == signup_screen else "navbar_item"
        nav_requests.variant = "nav_active" if current_screen == call_requests_view else "navbar_item"
        nav_settings.variant = "nav_active" if current_screen == accessibility_screen else "navbar_item"
        sync_navbar_theme()

content_frame = tb.Frame(root, padding=20)
content_frame.pack(expand=True, fill="both")

def update_entry(event):
    global cert_choice
    cert_choice = certType.get()

def redraw_all_custom_buttons():
    """Finds all LiftedRoundedButton instances currently on the screen and triggers a redraw"""
    # Look into the content_frame for all child elements
    for widget in content_frame.winfo_children():
        if isinstance(widget, LiftedRoundedButton):
            widget.draw_card()
        # Also look inside sub-containers (like our grid layout)
        for sub_widget in widget.winfo_children():
            if isinstance(sub_widget, LiftedRoundedButton):
                sub_widget.draw_card()

def darkmode():
    root.style.theme_use("darkly")
    apply_font_sizes() 
    sync_navbar_theme()
    redraw_all_custom_buttons() # <--- Triggers immediate button updates
    for lbl in accessibility_labels:
        if lbl.winfo_exists():
            lbl.config(foreground="white")

def lightmode():
    root.style.theme_use("flatly")
    apply_font_sizes()
    sync_navbar_theme()
    redraw_all_custom_buttons() # <--- Triggers immediate button updates
    for lbl in accessibility_labels:
        if lbl.winfo_exists():
            lbl.config(foreground=PSA_HEADER_BLUE)

def greymode():
    root.style.theme_use("superhero")
    apply_font_sizes()
    sync_navbar_theme()
    redraw_all_custom_buttons() # <--- Triggers immediate button updates
    for lbl in accessibility_labels:
        if lbl.winfo_exists():
            lbl.config(foreground="white")

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
    redraw_all_custom_buttons() # <--- Triggers immediate button updates
    for lbl in accessibility_labels:
        if lbl.winfo_exists():
            lbl.config(foreground=PSA_HEADER_BLUE)
    messagebox.showinfo("Reset Successful", "Accessibility changes have been restored to default values.")
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
    global CURRENT_LOGGED_IN_USER
    entered_username = username_var.get().strip()
    entered_password = password_var.get().strip()

    if not entered_username or not entered_password:
        login_error_var.set("Fields cannot be empty")
        return

    if entered_username == "admin" and entered_password == "admin123":
        CURRENT_LOGGED_IN_USER = "admin"
        login_error_var.set("")
        username_var.set("")
        password_var.set("")
        messagebox.showinfo("Access Approved", "Logged in as System Administrator.")
        navigate_to(main_menu_screen)
        return

    for username, data in account_database.items():
        email = data[0]
        password = data[1]
    
        if entered_username == email or entered_username == username:
            if entered_password == password:
                CURRENT_LOGGED_IN_USER = username
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
        
    if new_username.lower() == "admin":
        signup_error_var.set("Username 'admin' is reserved by the system configuration.")
        return
    
    for username, data in account_database.items():
        if new_email == data[0] or new_username.lower() == username.lower():
            signup_error_var.set("Account already exists with these identifiers.")
            return
        
    confirm = messagebox.askyesno("Create Account", f"Do you want to write account '{new_username}' to system cache?")
    if confirm:
        account_database[new_username] = [new_email, new_password]
        record_accounts()
        log_employee_action(new_username, "account created")
        messagebox.showinfo("Success", "Account created successfully!")
        
        new_username_var.set("")
        new_email_var.set("")
        new_password_var.set("")
        confirm_new_password_var.set("")
        signup_error_var.set("")
        
        navigate_to(main_menu_screen)

def initiate_forgot_password_sequence():
    target_user = forget_username_var.get().strip()
    if not target_user:
        forget_error_var.set("Please supply your account username.")
        return
        
    matched_username = None
    for username, data in account_database.items():
        if target_user.lower() == username.lower() or target_user.lower() == data[0].lower():
            matched_username = username
            break
            
    if not matched_username:
        forget_error_var.set("Target identity context not verified inside system.")
        return
        
    generated_token = f"{random.randint(100000, 999999)}"
    otp_requests_database[matched_username] = {
        "otp": generated_token,
        "timestamp": datetime.now()
    }
    
    messagebox.showinfo("DEV DEBUG LOG", f"Generated OTP for {matched_username}: {generated_token}")
    messagebox.showinfo("OTP Sent", f"An OTP modification token has been directed to the Admin side. Please coordinate to receive your token.")
    forget_error_var.set("")
    navigate_to(otp_verification_screen, matched_username)

def execute_otp_validation_check(target_username):
    user_entry = entered_otp_var.get().strip()
    if not user_entry:
        forget_error_var.set("OTP validation field cannot remain empty.")
        return
        
    if target_username not in otp_requests_database:
        forget_error_var.set("Session signature broken. Re-initiate reset pipeline workflow.")
        return
        
    correct_token = otp_requests_database[target_username]["otp"]
    if user_entry == correct_token:
        forget_error_var.set("")
        entered_otp_var.set("")
        navigate_to(reset_password_entry_screen, target_username)
    else:
        forget_error_var.set("Invalid OTP validation verification string match failure.")

def finalize_password_override(target_username):
    pwd1 = reset_new_password_var.get().strip()
    pwd2 = reset_confirm_password_var.get().strip()
    
    if not pwd1 or not pwd2:
        forget_error_var.set("Input entries must remain populated.")
        return
        
    if pwd1 != pwd2:
        forget_error_var.set("Validation parameters mismatch. Passwords must match.")
        return
        
    account_database[target_username][1] = pwd1
    record_accounts()
        
    log_employee_action(target_username, "changed password")
    messagebox.showinfo("Success", "Password updated successfully! Proceeding back to security terminal.")
    
    forget_username_var.set("")
    reset_new_password_var.set("")
    reset_confirm_password_var.set("")
    forget_error_var.set("")
    navigate_to(login_screen)

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

    login_btn = LiftedRoundedButton(btn_row, text="Sign In", image=None, command=verify_user_n_passcode, variant="primary", width=160, height=45)
    login_btn.pack(pady=5, fill="x")

    links_row = tb.Frame(container)
    links_row.pack(fill="x", pady=5)
    tb.Button(links_row, text="Forgot Password?", bootstyle="link", command=lambda: navigate_to(forget_screen)).pack(anchor="center", expand=True)

def signup_screen():
    container = tb.Frame(content_frame, padding=30)
    container.pack(expand=True)

    current_theme = root.style.theme.name
    heading_fg = "white" if current_theme in ["darkly", "superhero"] else PSA_HEADER_BLUE

    tb.Label(container, text="Register New Account", font=("Helvetica", 22, "bold"), foreground=heading_fg).pack(pady=(0, 25))

    tb.Label(container, text="Enter Username", font=("Helvetica", 11)).pack(anchor="w", pady=(5, 2))
    tb.Entry(container, textvariable=new_username_var, width=42).pack(pady=5, fill="x")

    tb.Label(container, text="Enter Email Address", font=("Helvetica", 11)).pack(anchor="w", pady=(5, 2))
    tb.Entry(container, textvariable=new_email_var, width=42).pack(pady=5, fill="x")

    tb.Label(container, text="Enter Password", font=("Helvetica", 11)).pack(anchor="w", pady=(5, 2))
    tb.Entry(container, textvariable=new_password_var, show="*", width=42).pack(pady=5, fill="x")

    tb.Label(container, text="Confirm Password", font=("Helvetica", 11)).pack(anchor="w", pady=(5, 2))
    tb.Entry(container, textvariable=confirm_new_password_var, show="*", width=42).pack(pady=5, fill="x")

    tb.Label(container, textvariable=signup_error_var, bootstyle="danger", font=("Helvetica", 10, "bold")).pack(pady=5)

    btn_signup = LiftedRoundedButton(container, text="Register Account", image=None, command=add_account, variant="primary", width=160, height=45)
    btn_signup.pack(pady=10, fill="x")

    tb.Button(container, text="Back to Dashboard", bootstyle="secondary-link", command=lambda: navigate_to(main_menu_screen)).pack()

def forget_screen():
    container = tb.Frame(content_frame, padding=30)
    container.pack(expand=True)

    current_theme = root.style.theme.name
    heading_fg = "white" if current_theme in ["darkly", "superhero"] else PSA_HEADER_BLUE

    tb.Label(container, text="Account Password Reset", font=("Helvetica", 22, "bold"), foreground=heading_fg).pack(pady=(0, 25))

    tb.Label(container, text="Target Account Username", font=("Helvetica", 11)).pack(anchor="w", pady=(5, 2))
    tb.Entry(container, textvariable=forget_username_var, width=42).pack(pady=5, fill="x")

    tb.Label(container, textvariable=forget_error_var, bootstyle="danger", font=("Helvetica", 10, "bold")).pack(pady=5)

    btn_reset = LiftedRoundedButton(container, text="Next Step", image=None, command=initiate_forgot_password_sequence, variant="primary", width=160, height=45)
    btn_reset.pack(pady=10, fill="x")

    tb.Button(container, text="Back to Login Screen", bootstyle="secondary-link", command=lambda: navigate_to(login_screen)).pack()

def otp_verification_screen(target_username):
    container = tb.Frame(content_frame, padding=30)
    container.pack(expand=True)

    current_theme = root.style.theme.name
    heading_fg = "white" if current_theme in ["darkly", "superhero"] else PSA_HEADER_BLUE

    tb.Label(container, text="Enter Security OTP String", font=("Helvetica", 20, "bold"), foreground=heading_fg).pack(pady=(0, 10))
    tb.Label(container, text=f"Account Target Identity Context: {target_username}", font=("Helvetica", 11, "italic")).pack(pady=(0, 20))

    tb.Label(container, text="6-Digit OTP Code Sequence", font=("Helvetica", 11)).pack(anchor="w", pady=(5, 2))
    tb.Entry(container, textvariable=entered_otp_var, width=42, justify="center").pack(pady=5, fill="x")

    tb.Label(container, textvariable=forget_error_var, bootstyle="danger", font=("Helvetica", 10, "bold")).pack(pady=5)

    btn_verify = LiftedRoundedButton(container, text="Verify Verification Token", image=None, command=lambda: execute_otp_validation_check(target_username), variant="primary", width=160, height=45)
    btn_verify.pack(pady=10, fill="x")

    tb.Button(container, text="Back to Login Screen", bootstyle="secondary-link", command=lambda: navigate_to(login_screen)).pack()

def reset_password_entry_screen(target_username):
    container = tb.Frame(content_frame, padding=30)
    container.pack(expand=True)

    current_theme = root.style.theme.name
    heading_fg = "white" if current_theme in ["darkly", "superhero"] else PSA_HEADER_BLUE

    tb.Label(container, text="Establish New Password Parameters", font=("Helvetica", 18, "bold"), foreground=heading_fg).pack(pady=(0, 25))
    tb.Label(container, text="Enter New Password", font=("Helvetica", 11)).pack(anchor="w", pady=(5, 2))
    tb.Entry(container, textvariable=reset_new_password_var, show="*", width=42).pack(pady=5, fill="x")
    tb.Label(container, text="Re-enter New Password", font=("Helvetica", 11)).pack(anchor="w", pady=(5, 2))
    tb.Entry(container, textvariable=reset_confirm_password_var, show="*", width=42).pack(pady=5, fill="x")
    tb.Label(container, textvariable=forget_error_var, bootstyle="danger", font=("Helvetica", 10, "bold")).pack(pady=5)
    btn_finalize = LiftedRoundedButton(container, text="Finalize Password Changes", image=None, command=lambda: finalize_password_override(target_username), variant="primary", width=160, height=45)
    btn_finalize.pack(pady=10, fill="x")

# ==========================================
# RE-ENGINEERED STR REPORT ID WRITER LOGIC
# ==========================================
def save_discrepancy_to_db(registry_num, error_type, explanation, field_name, original_val, revised_val):
    conn = get_db_connection()
    if not conn:
        return False
    cursor = conn.cursor(buffered=True)
    try:
        now = datetime.now()
        prefix = now.strftime("%y-%m-")
        seq_query = "SELECT report_id FROM discrepancy_report WHERE report_id LIKE %s ORDER BY report_id DESC LIMIT 1"
        cursor.execute(seq_query, (prefix + '%',))
        last_row = cursor.fetchone()
        if last_row:
            last_seq = int(last_row[0].split('-')[-1])
            new_seq = last_seq + 1
        else:
            new_seq = 1
        generated_report_id = f"{prefix}{new_seq:05d}"
        global cert_choice
        current_cert_type = cert_choice if cert_choice else "Birth Certificate"
        report_query = """
            INSERT INTO discrepancy_report (report_id, employee_id, registry_number, cert_type, status, created_date)
            VALUES (%s, %s, %s, %s, 'PENDING', NOW())
        """
        cursor.execute(report_query, (generated_report_id, CURRENT_LOGGED_IN_USER, registry_num, current_cert_type))
        entry_query = """
            INSERT INTO discrepancy_entries (report_id, person_name, cert_type, explanation, error_field, original_value, revised_value, modified_by, modified_date)
            VALUES (%s, NULL, %s, %s, %s, %s, %s, %s, NOW())
        """
        cursor.execute(entry_query, (generated_report_id, current_cert_type, explanation, field_name, original_val, revised_val, CURRENT_LOGGED_IN_USER))
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
            cert_choice = ""
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
            cert_choice = ""
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
            cert_choice = ""
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

    tb.Label(container, text="Type of Error: ", anchor="w").grid(row=4, column=0, sticky="w", pady=8, padx=10)
    birth_errorType = tb.Combobox(container, values=["Date of Birth", "Sex", "Place of Birth", "Father Details", "Mother Details", "Type of Birth", "Nationality","Birth Order", "Other (Specify in Explanations)"], state="readonly")
    birth_errorType.grid(row=4, column=1, sticky="ew", pady=8, padx=10)

    tb.Label(container, text="Original Value: ", anchor="w").grid(row=5, column=0, sticky="w", pady=8, padx=10)
    borigEntry = tb.Entry(container)
    borigEntry.grid(row=5, column=1, sticky="ew", pady=8, padx=10)

    tb.Label(container, text="Revised Value: ", anchor="w").grid(row=6, column=0, sticky="w", pady=8, padx=10)
    bnewEntry = tb.Entry(container)
    bnewEntry.grid(row=6, column=1, sticky="ew", pady=8, padx=10)

    tb.Label(container, text="Explanation: ", anchor="w").grid(row=7, column=0, sticky="w", pady=8, padx=10)
    bexplain = tb.Entry(container)
    bexplain.grid(row=7, column=1, sticky="ew", pady=8, padx=10)

    btn_frame = tb.Frame(container)
    btn_frame.grid(row=8, column=0, columnspan=2, pady=25)

    btn_sub = LiftedRoundedButton(btn_frame, text="Submit Entry", image=None, command=birth_confirm, variant="primary", width=160, height=45)
    btn_sub.pack(side=LEFT, padx=10)

    btn_can = LiftedRoundedButton(btn_frame, text="Cancel", image=None, command=lambda: navigate_to(entry_system_screen), variant="default", width=160, height=45)
    btn_can.pack(side=LEFT, padx=10)

def death_cert_screen():
    global death_regEntry, death_nameEntry, death_errorType, origEntry, newEntry, explain
    container = tb.Frame(content_frame, padding=30)
    container.pack(expand=True, fill="both")
    container.columnconfigure(1, weight=1)

    tb.Label(container, text="Registry Number: ", anchor="w").grid(row=0, column=0, sticky="w", pady=8, padx=10)
    death_regEntry = tb.Entry(container)
    death_regEntry.grid(row=0, column=1, sticky="ew", pady=8, padx=10)

    tb.Label(container, text="Name of Deceased: ", anchor="w").grid(row=1, column=0, sticky="w", pady=8, padx=10)
    death_nameEntry = tb.Entry(container)
    death_nameEntry.grid(row=1, column=1, sticky="ew", pady=8, padx=10)

    tb.Label(container, text="Type of Error: ", anchor="w").grid(row=2, column=0, sticky="w", pady=8, padx=10)
    death_errorType = tb.Combobox(container, values=["First Name", "Middle Name", "Last Name", "Date of Death", "Place of Death", "Age at Death", "Civil Status", "Cause of Death", "Registration of death (Date)", "Certification of death (Date)", "Other (Specify in Explanations)"], state="readonly")
    death_errorType.grid(row=2, column=1, sticky="ew", pady=8, padx=10)

    tb.Label(container, text="Original Value: ", anchor="w").grid(row=3, column=0, sticky="w", pady=8, padx=10)
    origEntry = tb.Entry(container)
    origEntry.grid(row=3, column=1, sticky="ew", pady=8, padx=10)

    tb.Label(container, text="Revised Value: ", anchor="w").grid(row=4, column=0, sticky="w", pady=8, padx=10)
    newEntry = tb.Entry(container)
    newEntry.grid(row=4, column=1, sticky="ew", pady=8, padx=10)

    tb.Label(container, text="Explanation: ", anchor="w").grid(row=5, column=0, sticky="w", pady=8, padx=10)
    explain = tb.Entry(container)
    explain.grid(row=5, column=1, sticky="ew", pady=8, padx=10)

    btn_frame = tb.Frame(container)
    btn_frame.grid(row=6, column=0, columnspan=2, pady=25)

    btn_sub = LiftedRoundedButton(btn_frame, text="Submit Entry", image=None, command=death_confirm, variant="primary", width=160, height=45)
    btn_sub.pack(side=LEFT, padx=10)

    btn_can = LiftedRoundedButton(btn_frame, text="Cancel", image=None, command=lambda: navigate_to(entry_system_screen), variant="default", width=160, height=45)
    btn_can.pack(side=LEFT, padx=10)

def marriage_cert_screen():
    global marriage_regEntry, marriage_errorType, applicantEntry, morigEntry, mnewEntry, mexplainEntry
    container = tb.Frame(content_frame, padding=30)
    container.pack(expand=True, fill="both")
    container.columnconfigure(1, weight=1)

    tb.Label(container, text="Registry Number: ", anchor="w").grid(row=0, column=0, sticky="w", pady=8, padx=10)
    marriage_regEntry = tb.Entry(container)
    marriage_regEntry.grid(row=0, column=1, sticky="ew", pady=8, padx=10)

    tb.Label(container, text="Applicant Name: ", anchor="w").grid(row=1, column=0, sticky="w", pady=8, padx=10)
    applicantEntry = tb.Entry(container)
    applicantEntry.grid(row=1, column=1, sticky="ew", pady=8, padx=10)

    tb.Label(container, text="Type of Error: ", anchor="w").grid(row=2, column=0, sticky="w", pady=8, padx=10)
    marriage_errorType = tb.Combobox(container, values=["Name of Husband", "Name of Spouse", "Date of Marriage", "Sex", "Age at Time of Marriage (Applicant)","Age at Time of Marriage (Spouse)", "Place of Marriage", "Registration of Marriage (Date)", "Certification of Marriage (Date)", "Other (Specify in Explanations)"], state="readonly")
    marriage_errorType.grid(row=2, column=1, sticky="ew", pady=8, padx=10)

    tb.Label(container, text="Original Value: ", anchor="w").grid(row=3, column=0, sticky="w", pady=8, padx=10)
    morigEntry = tb.Entry(container)
    morigEntry.grid(row=3, column=1, sticky="ew", pady=8, padx=10)

    tb.Label(container, text="Revised Value: ", anchor="w").grid(row=4, column=0, sticky="w", pady=8, padx=10)
    mnewEntry = tb.Entry(container)
    mnewEntry.grid(row=4, column=1, sticky="ew", pady=8, padx=10)

    tb.Label(container, text="Explanation: ", anchor="w").grid(row=5, column=0, sticky="w", pady=8, padx=10)
    mexplainEntry = tb.Entry(container)
    mexplainEntry.grid(row=5, column=1, sticky="ew", pady=8, padx=10)

    btn_frame = tb.Frame(container)
    btn_frame.grid(row=6, column=0, columnspan=2, pady=25)

    btn_sub = LiftedRoundedButton(btn_frame, text="Submit Entry", image=None, command=marriage_confirm, variant="primary", width=160, height=45)
    btn_sub.pack(side=LEFT, padx=10)

    btn_can = LiftedRoundedButton(btn_frame, text="Cancel", image=None, command=lambda: navigate_to(entry_system_screen), variant="default", width=160, height=45)
    btn_can.pack(side=LEFT, padx=10)

def entry_system_screen():
    global certType
    container = tb.Frame(content_frame, padding=30)
    container.pack(expand=True)

    current_theme = root.style.theme.name
    heading_fg = "white" if current_theme in ["darkly", "superhero"] else PSA_HEADER_BLUE

    tb.Label(container, text="Discrepancy Entry Desk", font=("Helvetica", 22, "bold"), foreground=heading_fg).pack(pady=(0, 20))
    tb.Label(container, text="Please specify the classification of vital statistics document requiring modification:", font=("Helvetica", 11)).pack(pady=(0, 15))

    certType = tb.Combobox(container, values=["Birth Certificate", "Death Certificate", "Marriage Certificate"], state="readonly", width=35)
    certType.pack(pady=10)
    certType.bind("<<ComboboxSelected>>", update_entry)

    def route_form():
        choice = certType.get()
        if choice == "Birth Certificate":
            navigate_to(birth_cert_screen)
        elif choice == "Death Certificate":
            navigate_to(death_cert_screen)
        elif choice == "Marriage Certificate":
            navigate_to(marriage_cert_screen)
        else:
            messagebox.showwarning("Selection Required", "Please choose a valid registry form type.")

    btn_frame = tb.Frame(container)
    btn_frame.pack(pady=20)

    btn_next = LiftedRoundedButton(btn_frame, text="Proceed to Form", image=None, command=route_form, variant="primary", width=160, height=45)
    btn_next.pack(side=LEFT, padx=10)

    btn_back = LiftedRoundedButton(btn_frame, text="Main Menu", image=None, command=lambda: navigate_to(main_menu_screen), variant="default", width=160, height=45)
    btn_back.pack(side=LEFT, padx=10)

def call_audit_logs_view(show_enter_new=False):
    global current_active_page_ref, all_fetched_audit_rows
    container = tb.Frame(content_frame, padding=10)
    container.pack(expand=True, fill="both")
    
    current_theme = root.style.theme.name
    heading_fg = "white" if current_theme in ["darkly", "superhero"] else PSA_HEADER_BLUE

    top_bar = tb.Frame(container)
    top_bar.pack(fill="x", pady=(0, 15))
    
    tb.Label(top_bar, text="Civil Registry Change Metrics Log", font=("Helvetica", 20, "bold"), foreground=heading_fg).pack(side=LEFT)
    
    # Bottom Navigation/Action Bar
    bottom_bar = tb.Frame(container, padding=(0, 10, 0, 0))
    bottom_bar.pack(fill="x", side=BOTTOM)
    
    LiftedRoundedButton(bottom_bar, text="Back to Main Menu", image=None, command=lambda: navigate_to(main_menu_screen), variant="default", width=180, height=45, text_size=12).pack(side=LEFT, padx=5)
    
    if show_enter_new:
        LiftedRoundedButton(top_bar, text="Log Another Entry", image=None, command=lambda: navigate_to(entry_system_screen), variant="primary", width=180, height=40, text_size=11).pack(side=RIGHT, padx=5)

    all_fetched_audit_rows = fetch_latest_audit_rows()
    
    class AuditPageRef:
        def __init__(self):
            self.dv = Tableview(
                master=container,
                coldata=c_dis_entry_audit,
                rowdata=all_fetched_audit_rows,
                paginated=True,
                pagesize=12,
                searchable=True,
                bootstyle="primary"
            )
            self.dv.pack(expand=True, fill="both")
            
    current_active_page_ref = AuditPageRef()
    apply_font_sizes()

def call_employee_logs_view():
    global current_active_page_ref
    container = tb.Frame(content_frame, padding=10)
    container.pack(expand=True, fill="both")
    
    current_theme = root.style.theme.name
    heading_fg = "white" if current_theme in ["darkly", "superhero"] else PSA_HEADER_BLUE

    tb.Label(container, text="Security Audit Log & Employee Footprints", font=("Helvetica", 20, "bold"), foreground=heading_fg).pack(anchor="w", pady=(0, 15))

    logs_list = []
    if os.path.exists(EMPLOYEE_LOGS_FILE):
        try:
            with open(EMPLOYEE_LOGS_FILE, "r") as file:
                raw_data = json.load(file)
                for item in raw_data:
                    logs_list.append((item.get("Username"), item.get("Action"), item.get("Date"), item.get("Time")))
        except:
            logs_list = []

    class EmployeePageRef:
        def __init__(self):
            self.dv = Tableview(
                master=container,
                coldata=c_employee_logs_headers,
                rowdata=logs_list,
                paginated=True,
                pagesize=12,
                searchable=True,
                bootstyle="secondary"
            )
            self.dv.pack(expand=True, fill="both")
            
    current_active_page_ref = EmployeePageRef()
    
    # Bottom Navigation/Action Bar
    bottom_bar = tb.Frame(container, padding=(0, 10, 0, 0))
    bottom_bar.pack(fill="x", side=BOTTOM)
    LiftedRoundedButton(bottom_bar, text="Back to Main Menu", image=None, command=lambda: navigate_to(main_menu_screen), variant="default", width=180, height=45, text_size=12).pack(side=LEFT, padx=5)
    
    apply_font_sizes()

def call_requests_view():
    global current_active_page_ref
    container = tb.Frame(content_frame, padding=10)
    container.pack(expand=True, fill="both")
    
    current_theme = root.style.theme.name
    heading_fg = "white" if current_theme in ["darkly", "superhero"] else PSA_HEADER_BLUE

    tb.Label(container, text="Pending Token Requests (OTP Audit Panel)", font=("Helvetica", 20, "bold"), foreground=heading_fg).pack(anchor="w", pady=(0, 15))

    req_list = []
    for user, data in otp_requests_database.items():
        ts_str = data["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
        req_list.append((user, data["otp"], ts_str))

    class RequestsPageRef:
        def __init__(self):
            self.dv = Tableview(
                master=container,
                coldata=c_requests_headers,
                rowdata=req_list,
                paginated=True,
                pagesize=12,
                searchable=True,
                bootstyle="info"
            )
            self.dv.pack(expand=True, fill="both")
            
    current_active_page_ref = RequestsPageRef()
    
    # Bottom Navigation/Action Bar
    bottom_bar = tb.Frame(container, padding=(0, 10, 0, 0))
    bottom_bar.pack(fill="x", side=BOTTOM)
    LiftedRoundedButton(bottom_bar, text="Back to Main Menu", image=None, command=lambda: navigate_to(main_menu_screen), variant="default", width=180, height=45, text_size=12).pack(side=LEFT, padx=5)
    
    apply_font_sizes()

def accessibility_screen():
    container = tb.Frame(content_frame, padding=15)
    container.pack(expand=True, fill="both")

    current_theme = root.style.theme.name
    heading_fg = "white" if current_theme in ["darkly", "superhero"] else PSA_HEADER_BLUE

    # PACK THE LOWER ACTION INTERFACE TO THE BOTTOM FIRST
    ctrl_row = tb.Frame(container)
    ctrl_row.pack(fill="x", side=BOTTOM, pady=(10, 0))
    
    LiftedRoundedButton(ctrl_row, text="Reset to Factory Defaults", image=None, command=reset_settings, variant="muted_danger", width=220, height=45).pack(side=LEFT, padx=5)
    LiftedRoundedButton(ctrl_row, text="Back to Home Menu", image=None, command=lambda: navigate_to(main_menu_screen), variant="default", width=180, height=45, text_size=12).pack(side=LEFT, padx=5)

    # PACK THE REST OF THE CONTENT
    tb.Label(container, text="Control and Diagnostics Center", font=("Helvetica", 22, "bold"), foreground=heading_fg).pack(anchor="w", pady=(0, 10))

    sect_theme = tb.Labelframe(container, text=" Display & Styling Preferences ", padding=15)
    sect_theme.pack(fill="x", pady=5)
    
    lbl_theme = tb.Label(sect_theme, text="Select Master UI Palette Skin Mode:", font=("Helvetica", 11, "bold"), foreground=PSA_HEADER_BLUE)
    lbl_theme.pack(anchor="w", pady=(0, 5))
    accessibility_labels.append(lbl_theme)

    theme_btn_row = tb.Frame(sect_theme)
    theme_btn_row.pack(anchor="w", pady=5)

    LiftedRoundedButton(theme_btn_row, text="Light Theme", image=None, command=lightmode, variant="default", width=140, height=45).pack(side=LEFT, padx=5)
    LiftedRoundedButton(theme_btn_row, text="Dark Mode", image=None, command=darkmode, variant="accent", width=140, height=45).pack(side=LEFT, padx=5)
    LiftedRoundedButton(theme_btn_row, text="Slate High Contrast", image=None, command=greymode, variant="grey_button", width=180, height=45).pack(side=LEFT, padx=5)

    sect_font = tb.Labelframe(container, text=" Font Resizing & Scale Adaptability Engine ", padding=15)
    sect_font.pack(fill="x", pady=5)

    lbl_font = tb.Label(sect_font, text="Global Application UI Text Scaling controls:", font=("Helvetica", 11, "bold"), foreground=PSA_HEADER_BLUE)
    lbl_font.pack(anchor="w", pady=(0, 5))
    accessibility_labels.append(lbl_font)

    font_btn_row = tb.Frame(sect_font)
    font_btn_row.pack(anchor="w", pady=5)

    LiftedRoundedButton(font_btn_row, text="A+  Enlarge App Font", image=None, command=increase_font, variant="default", width=180, height=45, text_size=12).pack(side=LEFT, padx=5)
    LiftedRoundedButton(font_btn_row, text="A-  Shrink App Font", image=None, command=decrease_font, variant="default", width=180, height=45, text_size=12).pack(side=LEFT, padx=5)

    lbl_table = tb.Label(sect_font, text="Tabular Metadata Rows Resizing engine:", font=("Helvetica", 11, "bold"), foreground=PSA_HEADER_BLUE)
    lbl_table.pack(anchor="w", pady=(10, 5))
    accessibility_labels.append(lbl_table)

    table_btn_row = tb.Frame(sect_font)
    table_btn_row.pack(anchor="w", pady=5)

    LiftedRoundedButton(table_btn_row, text="Increase Rows Font", image=None, command=increase_table_font, variant="default", width=180, height=45, text_size=11).pack(side=LEFT, padx=5)
    LiftedRoundedButton(table_btn_row, text="Decrease Rows Font", image=None, command=decrease_table_font, variant="default", width=180, height=45, text_size=11).pack(side=LEFT, padx=5)
    
    if current_theme in ["darkly", "superhero"]:
        for lbl in accessibility_labels:
            lbl.config(foreground="white")

def main_menu_screen():
    local_icon_scale = 10
    main_container = tb.Frame(content_frame)
    main_container.pack(expand=True, fill="both", padx=40, pady=20)
    
    # Try loading a unique icon file for each of the 6 buttons
    try:
        raw_icon1 = tb.PhotoImage(file=r"/Users/mac/Desktop/system_image/1.png")
        icon1 = raw_icon1.subsample(local_icon_scale, local_icon_scale)
        
        raw_icon2 = tb.PhotoImage(file=r"/Users/mac/Desktop/system_image/2.png")
        icon2 = raw_icon2.subsample(local_icon_scale, local_icon_scale)
        
        raw_icon3 = tb.PhotoImage(file=r"/Users/mac/Desktop/system_image/3.png")
        icon3 = raw_icon3.subsample(local_icon_scale, local_icon_scale)
        
        raw_icon4 = tb.PhotoImage(file=r"/Users/mac/Desktop/system_image/4.png")
        icon4 = raw_icon4.subsample(local_icon_scale, local_icon_scale)
        
        raw_icon5 = tb.PhotoImage(file=r"/Users/mac/Desktop/system_image/5.png")
        icon5 = raw_icon5.subsample(local_icon_scale, local_icon_scale)
        
        raw_icon6 = tb.PhotoImage(file=r"/Users/mac/Desktop/system_image/6.png")
        icon6 = raw_icon6.subsample(local_icon_scale, local_icon_scale)
    except Exception as e:
        icon1 = icon2 = icon3 = icon4 = icon5 = icon6 = None

    # DYNAMIC RENDER INTERFACES: ADMIN vs REGULAR EMPLOYEE
    if CURRENT_LOGGED_IN_USER == "admin":
        main_container.columnconfigure(0, weight=1, uniform="cols")
        main_container.columnconfigure(1, weight=1, uniform="cols")
        main_container.columnconfigure(2, weight=1, uniform="cols")
        main_container.rowconfigure(0, weight=1, uniform="rows")
        main_container.rowconfigure(1, weight=1, uniform="rows")

        # Row 0 Elements (Buttons 1, 2, 3)
        btn_create = LiftedRoundedButton(
            main_container, text="Create New Entry Log", image=icon1, compound="top",
            command=lambda: navigate_to(entry_system_screen), variant="default", text_size=18
        )
        btn_create.image_cache = icon1  
        btn_create.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)

        btn_logs = LiftedRoundedButton(
            main_container, text="View Change Metrics Log", image=icon2, compound="top",
            command=lambda: navigate_to(call_audit_logs_view, show_enter_new=False), variant="default", text_size=18
        )
        btn_logs.image_cache = icon2
        btn_logs.grid(row=0, column=1, sticky="nsew", padx=15, pady=15)

        btn_emp_logs = LiftedRoundedButton(
            main_container, text="Security Employee Logs", image=icon3, compound="top",
            command=lambda: navigate_to(call_employee_logs_view), variant="default", text_size=18
        )
        btn_emp_logs.image_cache = icon3
        btn_emp_logs.grid(row=0, column=2, sticky="nsew", padx=15, pady=15)

        # Row 1 Elements (Buttons 4, 5, 6)
        btn_create_acc = LiftedRoundedButton(
            main_container, text="Register New Account", image=icon4, compound="top",
            command=lambda: navigate_to(signup_screen), variant="default", text_size=18
        )
        btn_create_acc.image_cache = icon4
        btn_create_acc.grid(row=1, column=0, sticky="nsew", padx=15, pady=15)

        btn_requests = LiftedRoundedButton(
            main_container, text="Pending Requests (OTP)", image=icon5, compound="top",
            command=lambda: navigate_to(call_requests_view), variant="default", text_size=18
        )
        btn_requests.image_cache = icon5
        btn_requests.grid(row=1, column=1, sticky="nsew", padx=15, pady=15)

        btn_settings = LiftedRoundedButton(
            main_container, text="Settings & Accessibility", image=icon6, compound="top",
            command=lambda: navigate_to(accessibility_screen), variant="default", text_size=18
        )
        btn_settings.image_cache = icon6
        btn_settings.grid(row=1, column=2, sticky="nsew", padx=15, pady=15)

    else:
        # Standard user configuration handles its 3 items elegantly using the loaded assets
        main_container.columnconfigure(0, weight=1, uniform="cols")
        main_container.columnconfigure(1, weight=1, uniform="cols")
        main_container.rowconfigure(0, weight=1)

        btn_create = LiftedRoundedButton(
            main_container, text="Create New Entry Log", image=icon1, compound="top",
            command=lambda: navigate_to(entry_system_screen), width=320, height=200, variant="default", text_size=22
        )
        btn_create.image_cache = icon1  
        btn_create.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        right_sub_container = tb.Frame(main_container)
        right_sub_container.grid(row=0, column=1, sticky="nsew")
        right_sub_container.columnconfigure(0, weight=1)
        right_sub_container.rowconfigure(0, weight=1, uniform="right_rows")
        right_sub_container.rowconfigure(1, weight=1, uniform="right_rows")

        btn_logs = LiftedRoundedButton(
            right_sub_container, text="View Logs", image=icon2, compound="left",
            command=lambda: navigate_to(call_audit_logs_view, show_enter_new=False), width=320, height=90, variant="default", text_size=18
        )
        btn_logs.image_cache = icon2
        btn_logs.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        btn_settings = LiftedRoundedButton(
            right_sub_container, text="Settings and Accessibility", image=icon6, compound="left",
            command=lambda: navigate_to(accessibility_screen), width=320, height=90, variant="default", text_size=18
        )
        btn_settings.image_cache = icon6
        btn_settings.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)

# ==========================================
# BOOT EXECUTION LAYER TRIGGER
# ==========================================
if __name__ == "__main__":
    navigate_to(login_screen)
    root.mainloop()