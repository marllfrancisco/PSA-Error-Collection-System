# ==========================================
# PSA ERROR COLLECTION SYSTEM
# ==========================================
# MAIN APPLICATION FILE
# This system manages error/discrepancy reporting for PSA (Philippine Statistics Authority)
# It allows employees to report errors in vital records (birth, death, marriage certificates)
# and tracks user actions with audit logs and security features.

# ==========================================
# IMPORT LIBRARIES & DEPENDENCIES
# ==========================================
import re                                  # Regular expressions for data validation
import os                                  # Operating system functions (file handling)
import csv                                 # CSV file reading/writing for account management
import json                                # JSON file handling for audit logs
import random                              # Generate random OTP codes for password reset
import mysql.connector                     # MySQL database connection
from mysql.connector import Error          # MySQL error handling
import ttkbootstrap as tb                  # Modern themed UI widgets
from ttkbootstrap.constants import *       # UI constants and styling
from ttkbootstrap.widgets.tableview import Tableview  # Table display widget
from tkinter import messagebox, StringVar  # Dialog boxes and string variables
from datetime import datetime              # Date/time tracking for logs
import ctypes                              # System-level Windows API calls for DPI scaling
from PIL import Image, ImageTk             # Image loading and display
import traceback                           # Detailed error stack trace printing
import sys                                 # System module (used for PyInstaller and resource resolution)

# ==========================================
# DATABASE & FILE STORAGE SETUP
# ==========================================
# MySQL Database Configuration - connects to the backend database for error records
DB_CONFIG = {
    'host': 'localhost',                   # Database server location (local machine)
    'user': 'root',                        # MySQL username
    'password': '',                        # MySQL password (empty for default setup)
    'database': 'ecorrectdb'               # Database name for error collection
}

# File paths for persistent storage (CSV for accounts, JSON for audit logs)
ACCOUNTS_FILE = "SourceCodes/employee_data.csv"  # Employee credentials storage
EMPLOYEE_LOGS_FILE = "SourceCodes/employee_logs.json"  # Audit trail of all user actions

# ==========================================
# GLOBAL STATE VARIABLES
# ==========================================
# Currently logged-in user tracking
CURRENT_LOGGED_IN_USER = "Guest"           # Stores username of active session
otp_requests_database = {}                 # Temporary storage for OTP reset tokens

# Main account database (loaded from CSV at startup)
account_database = {}

# ==========================================
# ACCOUNT MANAGEMENT FUNCTIONS
# ==========================================
# Load employee credentials from CSV file into memory
def load_accounts():
    """
    PURPOSE: Loads all employee account data from employee_data.csv into memory
    - Reads username, email, password, and metadata
    - Creates default Admin account if CSV doesn't exist
    - Returns dictionary with usernames as keys
    """
    accounts = {}
    if not os.path.exists(ACCOUNTS_FILE):
        # If no CSV exists, create default admin account
        print("CSV not found, creating default structure.")
        return {
            "Admin": {"person_id": "P-1000", "email": "Admin@gmail.com", "password": "123", "created_id": "01/01/2026", "modified_id": "01/01/2026"}
        }

    # Read CSV file and parse each row into account dictionary
    with open(ACCOUNTS_FILE, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)  # Parse CSV headers and rows
        for row in reader:
            # Extract employee_id as the dictionary key (username)
            eid = row.pop("employee_id")  
            accounts[eid] = row  # Store all other fields as account data
    return accounts

# Initialize the account database by loading from CSV at program startup
account_database = load_accounts()

# ==========================================
# ACCOUNT PERSISTENCE & AUDIT LOGGING
# ==========================================
def save_accounts_to_csv():
    """
    PURPOSE: Saves all account changes back to employee_data.csv file
    - Writes current account_database dictionary to CSV
    - Reloads data from CSV to verify save was successful
    - Includes error handling for file write failures
    - Maintains data integrity between sessions
    """
    global account_database
    try:
        # Open CSV file in write mode (overwrites existing content)
        with open(ACCOUNTS_FILE, mode="w", newline="", encoding="utf-8") as file:
            # Define CSV column structure matching the database format
            fieldnames = ["employee_id", "person_id", "email", "password", "created_id", "modified_id"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            
            # Write header row
            writer.writeheader()
            
            # Write each account record with employee_id in first column
            for eid, data in account_database.items():
                row = {"employee_id": eid}  # Username goes in employee_id column
                row.update(data)             # Add all account fields
                writer.writerow(row)
        
        # After saving, reload from CSV to verify the save was successful
        # This ensures data consistency and catches any write errors
        account_database = load_accounts()
        print(f"DEBUG: Successfully saved and reloaded accounts from CSV. Current users: {list(account_database.keys())}")
    except Exception as e:
        # Log any save failures for debugging
        print(f"ERROR: Failed to save accounts to CSV: {e}")
        traceback.print_exc()
        raise

def log_employee_action(username, action):
    """
    PURPOSE: Records all user actions to employee_logs.json for audit trail
    - Tracks account creation, password changes, and other security events
    - Stores timestamp and date of each action
    - Appends new logs without overwriting existing records
    
    ACTIONS LOGGED:
    - 'account created' - when new employee account is added
    - 'changed password' - when employee resets their password
    - Other system events for accountability
    """
    logs = []
    
    # Load existing logs from JSON file (if it exists)
    if os.path.exists(EMPLOYEE_LOGS_FILE):
        try:
            with open(EMPLOYEE_LOGS_FILE, "r") as file:
                logs = json.load(file)  # Parse existing JSON log entries
        except:
            logs = []  # If JSON is corrupted, start fresh
            
    # Create new log entry with current timestamp
    now = datetime.now()
    new_log = {
        "Username": username,           # Who performed the action
        "Action": action,               # What action was performed
        "Date": now.strftime("%Y-%m-%d"),  # Today's date
        "Time": now.strftime("%H:%M:%S")   # Current time
    }
    
    # Append new log to the list
    logs.append(new_log)
    
    # Write updated logs back to JSON file
    with open(EMPLOYEE_LOGS_FILE, "w") as file:
        json.dump(logs, file, indent=4)  # Pretty-print JSON for readability

# ==========================================
# TABLE CONFIGURATION & DISPLAY HEADERS
# ==========================================
# Column headers for the discrepancy/error entry audit table
# Displays submitted error corrections with original vs. revised values
c_dis_entry_audit = [
    {"text": "Report ID", "stretch": True},          # Unique identifier for each error report
    {"text": "Cert Type", "stretch": True},          # Type of certificate (birth, death, marriage)
    {"text": "Error Field", "stretch": True},        # Which field had the error
    {"text": "Original Value", "stretch": True},     # What the value was before correction
    {"text": "Revised Value", "stretch": True},      # What the value should be (correction)
    {"text": "Modified By", "stretch": True}         # Which employee submitted the correction
]

# Column headers for employee audit logs table
# Shows all user actions (login, password change, etc.)
c_employee_logs_headers = [
    {"text": "Username", "stretch": True},           # Who performed the action
    {"text": "Action", "stretch": True},             # What action was performed
    {"text": "Date", "stretch": True},               # Date of the action
    {"text": "Time", "stretch": True}                # Time of the action
]

# Column headers for OTP requests table
# Tracks password reset requests that were issued
c_requests_headers = [
    {"text": "Target Username", "stretch": True},    # User requesting password reset
    {"text": "Generated OTP Code", "stretch": True}, # One-time password code issued
    {"text": "Request Timestamp", "stretch": True}   # When the reset was requested
]

# ==========================================
# PAGE & UI STATE TRACKING
# ==========================================
current_active_page_ref = None              # Reference to the currently displayed UI page
all_fetched_audit_rows = []                 # Cache of audit records fetched from database
accessibility_labels = []                   # Accessibility/label text for UI elements

# ==========================================
# DATABASE CONNECTION & DATA RETRIEVAL
# ==========================================
def get_db_connection():
    """
    PURPOSE: Establishes connection to MySQL database
    - Connects using credentials from DB_CONFIG
    - Returns connection object if successful, None if failed
    - Displays error dialog if connection fails
    - Used for querying error records and audit logs
    """
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            return connection
    except Error as e:
        # Show error message if database connection fails
        messagebox.showerror("Database Error", f"Could not connect to MySQL Database:\n{e}")
        return None

def fetch_latest_audit_rows():
    """
    PURPOSE: Retrieves all error correction records from the database
    - Queries the 'discrepancy_entries' table from MySQL
    - Orders results by most recent first
    - Returns list of tuples with error details
    - Used to populate the audit log display table
    
    RETURNS:
    - List of tuples: (report_id, cert_type, error_field, original_value, revised_value, modified_by)
    """
    conn = get_db_connection()
    if not conn:
        return []  # Return empty list if connection fails
    
    cursor = conn.cursor()
    try:
        # SQL query to get all discrepancy entries sorted by newest first
        query = """
            SELECT report_id, cert_type, error_field, original_value, revised_value, modified_by 
            FROM discrepancy_entries 
            ORDER BY modified_date DESC
        """
        cursor.execute(query)
        rows = cursor.fetchall()  # Get all matching records
        return rows
    except Error as e:
        # Show error if query fails
        messagebox.showerror("Database Query Error", f"Failed to retrieve audit log metrics:\n{e}")
        return []
    finally:
        # Always close database connection to avoid resource leaks
        cursor.close()
        conn.close()

# ==========================================
# GUI MAIN APPLICATION INITIALIZATION
# ==========================================
# Make application DPI-aware on Windows to prevent automatic scaling issues
# This allows the app to properly display at high DPI settings (e.g., 4K monitors)
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass  # Ignore if DPI awareness not available on system

# Get the absolute directory path for reliable file access across all systems
base_dir = os.path.dirname(os.path.abspath(__file__))
# Get a resource path resolver that works in normal and bundled (PyInstaller) runs
root = tb.Window(themename="flatly")

def resolve_resource(*parts):
    """Return an absolute path inside the project or inside a PyInstaller
    bundle. Usage: resolve_resource('images', 'psa.png')"""
    base = getattr(sys, '_MEIPASS', base_dir)
    return os.path.join(base, *parts)

# Try to set a window icon in a cross-platform way:
# - Windows supports .ico via `iconbitmap`
# - Other platforms (mac/linux) should use `iconphoto` with a PhotoImage
try:
    ico_path = resolve_resource('images', 'psa.ico')
    if os.path.exists(ico_path):
        try:
            root.iconbitmap(ico_path)
        except Exception:
            # Fallback: try loading ICO via PIL and set as PhotoImage
            try:
                img = Image.open(ico_path)
                icon_photo = ImageTk.PhotoImage(img)
                root.iconphoto(False, icon_photo)
            except Exception:
                print(f"Failed to set window icon from {ico_path}")
    else:
        # Try PNG fallback when ICO is not present (common on macOS)
        png_icon = resolve_resource('images', 'psa.png')
        if os.path.exists(png_icon):
            try:
                img = Image.open(png_icon)
                icon_photo = ImageTk.PhotoImage(img)
                root.iconphoto(False, icon_photo)
            except Exception:
                print(f"Failed to set window icon from {png_icon}")
except Exception as e:
    print(f"Icon setup error: {e}")

# Configure and maximize the main window
root.update()  # Update window state
width = root.winfo_screenwidth()     # Get screen width (for fullscreen)  
height = root.winfo_screenheight()   # Get screen height
root.geometry("%dx%d" % (width, height))  # Set window to fill entire screen
root.title("PSA Error Collection")   # Set window title
root.state('zoomed')                 # Maximize window on startup

# ==========================================
# COLOR SCHEME & UI STYLING CONFIGURATION
# ==========================================
# Color scheme matching PSA branding
PSA_BLUE = "#4d73ff"                 # Primary accent color for UI elements
PSA_HEADER_BLUE = "#0066cc"          # Darker blue for headers and important text

# Default font sizes (before UI scaling)
DEFAULT_TITLE_SIZE = 25              # Size for main page titles
DEFAULT_BODY_SIZE = 11               # Size for body text and labels
MAX_IMAGE_TABLE_SIZE = 11            # Size for table text

# ==========================================
# UI SCALING & RESPONSIVE DESIGN
# ==========================================
# Universal scaling factor - adjust to scale entire UI (0.8 = 80%, 1.2 = 120%)
# This helps the app look good on different screen sizes and DPI settings
UI_SCALE = 0.8

# Font sizes after applying UI scale (used for all UI elements)
FONT_BODY = int(11 * UI_SCALE)       # Scaled body/label text size
FONT_BUTTON = int(14 * UI_SCALE)     # Scaled button text size
FONT_TITLE = int(22 * UI_SCALE)      # Scaled page title size

# Additional typography settings
font_size_title = DEFAULT_TITLE_SIZE # Title font size
font_size_default = DEFAULT_BODY_SIZE # Default body font size
font_size_table = MAX_IMAGE_TABLE_SIZE # Table content font size

# ==========================================
# GLOBAL UI STATE VARIABLES
# ==========================================
# GLOBAL UI STATE VARIABLES
# ==========================================
icon_scale_factor = 20               # Size multiplier for images/icons
certType = None                      # Type of certificate being processed (birth, death, marriage)
cert_choice = ""                     # String representation of certificate choice

# ==========================================
# LOGIN & AUTHENTICATION UI VARIABLES
# ==========================================
# StringVar objects are used to bind input fields to variables automatically
# This allows real-time access to what users type without manual extraction

# LOGIN SCREEN variables
username_var = StringVar()            # Stores username entered on login screen
password_var = StringVar()            # Stores password entered on login screen
login_error_var = StringVar()         # Displays login error messages to user

# ==========================================
# ACCOUNT CREATION/SIGNUP VARIABLES
# ==========================================
new_username_var = StringVar()        # New account: username being created
new_email_var = StringVar()           # New account: email address
new_password_var = StringVar()        # New account: password entry
confirm_new_password_var = StringVar() # New account: password confirmation
signup_error_var = StringVar()        # Displays account creation error messages

# ==========================================
# PASSWORD RESET/FORGOT PASSWORD VARIABLES
# ==========================================
forget_username_var = StringVar()     # User entering username to reset password
entered_otp_var = StringVar()         # User entering OTP verification code
reset_new_password_var = StringVar()  # New password during reset process
reset_confirm_password_var = StringVar() # Confirm new password during reset
forget_error_var = StringVar()        # Displays password reset error messages

# ==========================================
# ERROR ENTRY FORM VARIABLES (Death Records)
# ==========================================
# Variables for reporting errors in death certificate records
death_regEntry = None                 # Registration number input field
death_nameEntry = None                # Deceased person's name input field
death_errorType = None                # Type of error (misspelling, wrong date, etc)
origEntry = None                      # Original (incorrect) value in record
newEntry = None                       # Corrected/revised value
explain = None                        # Explanation/reason for the correction

# ==========================================
# ERROR ENTRY FORM VARIABLES (Birth Records)
# ==========================================
# Variables for reporting errors in birth certificate records
birth_regEntry = None                 # Registration number input field
youEntry = None                       # Child's name input field
momEntry = None
dadEntry = None
birth_errorType = None
borigEntry = None
bnewEntry = None
bexplain = None

# ==========================================
# ERROR ENTRY FORM VARIABLES (Marriage Records)
# ==========================================
# Variables for reporting errors in marriage certificate records
marriage_regEntry = None              # Registration number input field
marriage_errorType = None             # Type of error in marriage record
applicantEntry = None                 # Applicant/spouse name input field
morigEntry = None                     # Original value in marriage record
mnewEntry = None                      # Corrected value for marriage record
mexplainEntry = None                  # Explanation for the marriage record correction

# =====================================================================
# CUSTOM UI COMPONENT: LIFTED ROUNDED CARD BUTTON
# =====================================================================
# This is a custom button widget with rounded corners and lift animation
# Used throughout the app for a modern, professional appearance
class LiftedRoundedButton(tb.Canvas):
    """
    PURPOSE: Creates a beautiful rounded button with hover/press animations
    - Draws custom button appearance using Canvas graphics
    - Shows lift/shadow effect when hovered
    - Changes color based on variant (primary, secondary, danger, etc)
    - Supports both text and icon display
    - Automatically disables for non-clickable states
    """
    def __init__(self, parent, text, image, command, compound="top", variant="default", text_size=16, bg_override=None, **kwargs):
        current_theme_bg = bg_override if bg_override else (tb.Style().lookup("TFrame", "background") or "#f8f9fa")
        super().__init__(parent, highlightthickness=0, borderwidth=0, bg=current_theme_bg, **kwargs)
        self.text = text                # Button label text
        self.image = image              # Optional image/icon to display
        self.command = command          # Function to call when clicked
        self.compound = compound        # Image/text layout (top, left, right, bottom)
        self.variant = variant          # Button style (primary, secondary, danger, etc)
        self.text_size = text_size      # Font size for button text
        self._disabled = False          # Whether button is clickable
        self.bg_override = bg_override  # Override background color if needed
        
        # Bind mouse and redraw events
        self.bind("<Configure>", self.draw_card)  # Redraw when resized
        self.bind("<ButtonPress-1>", self.on_press)  # Handle mouse press
        self.bind("<ButtonRelease-1>", self.on_release)  # Handle mouse release
        self.bind("<Enter>", self.on_hover)  # Handle mouse enter
        self.bind("<Leave>", self.on_leave)  # Handle mouse leave
        
        self.pressed = False            # Track if button is currently pressed
        self.hovered = False            # Track if mouse is over button

    def set_disabled(self, disabled=True):
        """Enable or disable the button"""
        self._disabled = disabled
        self.draw_card()  # Redraw to show disabled state

    def draw_card(self, event=None):
        """Draw the button appearance with rounded corners and effects"""
        self.delete("all")  # Clear previous drawing
        w = self.winfo_width()
        h = self.winfo_height()
        # If the widget hasn't been placed yet, use a default size 
        # instead of returning/quitting.
        if w < 10: w = 100
        if h < 10: h = 50

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
            self.create_text(center_x, center_y, text=self.text, font=("Helvetica", FONT_BUTTON, "bold"), fill=text_color, justify=CENTER, width=w - 20)

    def create_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        if r == 0:
            return self.create_rectangle(x1, y1, x2, y2, **kwargs)
        
        points = [
            x1+r, y1,  x2-r, y1,  x2, y1,     
            x2, y1+r,  x2, y2-r,  x2, y2,     
            x2-r, y2,  x1+r, y2,  x1, y2,     
            x1, y2-r,  x1, y1+r,  x1, y1      
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
    psa_png_path = resolve_resource('images', 'psa.png')
    raw_img = Image.open(psa_png_path)
    new_width = max(24, raw_img.width // 6)
    new_height = max(24, raw_img.height // 6)
    # Use LANCZOS if available (Pillow >=9), otherwise fall back to ANTIALIAS
    if hasattr(Image, 'Resampling'):
        resample_filter = Image.Resampling.LANCZOS
    else:
        resample_filter = Image.ANTIALIAS
    resized_img = raw_img.resize((new_width, new_height), resample_filter)
    logo_image = ImageTk.PhotoImage(resized_img)
except Exception as e:
    print(f"Could not load banner logo: {e}")
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

nav_home = LiftedRoundedButton(nav_frame, text="Home Menu", image=None, command=lambda: navigate_to(main_menu_screen), variant="navbar_item", width=140+60, height=45, text_size=11, bg_override=PSA_HEADER_BLUE)
nav_home.pack(side=LEFT)

nav_logs = LiftedRoundedButton(nav_frame, text="View Audit Logs", image=None, command=lambda: navigate_to(call_audit_logs_view, show_enter_new=False), variant="navbar_item", width=140+60, height=45, text_size=11, bg_override=PSA_HEADER_BLUE)
nav_logs.pack(side=LEFT)

nav_emp_logs = LiftedRoundedButton(nav_frame, text="Employee Logs", image=None, command=lambda: navigate_to(call_employee_logs_view), variant="navbar_item", width=140+60, height=45, text_size=11, bg_override=PSA_HEADER_BLUE)
nav_create_acc = LiftedRoundedButton(nav_frame, text="Create Account", image=None, command=lambda: navigate_to(signup_screen), variant="navbar_item", width=140+60, height=45, text_size=11, bg_override=PSA_HEADER_BLUE)
nav_requests = LiftedRoundedButton(nav_frame, text="Requests", image=None, command=lambda: navigate_to(call_requests_view), variant="navbar_item", width=140+60, height=45, text_size=11, bg_override=PSA_HEADER_BLUE)

nav_settings = LiftedRoundedButton(nav_frame, text="Accessibility Settings", image=None, command=lambda: navigate_to(accessibility_screen), variant="navbar_item", width=180+60, height=45, text_size=11, bg_override=PSA_HEADER_BLUE)
nav_settings.pack(side=LEFT)

nav_logout = LiftedRoundedButton(nav_frame, text="Logout", image=None, command=lambda: confirm_logout(), variant="navbar_item", width=120+60, height=45, text_size=11, bg_override=PSA_HEADER_BLUE)
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
    for widget in content_frame.winfo_children():
        if isinstance(widget, LiftedRoundedButton):
            widget.draw_card()
        for sub_widget in widget.winfo_children():
            if isinstance(sub_widget, LiftedRoundedButton):
                sub_widget.draw_card()

def darkmode():
    root.style.theme_use("darkly")
    apply_font_sizes() 
    sync_navbar_theme()
    redraw_all_custom_buttons() 
    for lbl in accessibility_labels:
        if lbl.winfo_exists():
            lbl.config(foreground="white")

def lightmode():
    root.style.theme_use("flatly")
    apply_font_sizes()
    sync_navbar_theme()
    redraw_all_custom_buttons() 
    for lbl in accessibility_labels:
        if lbl.winfo_exists():
            lbl.config(foreground=PSA_HEADER_BLUE)

def greymode():
    root.style.theme_use("superhero")
    apply_font_sizes()
    sync_navbar_theme()
    redraw_all_custom_buttons() 
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
    redraw_all_custom_buttons() 
    for lbl in accessibility_labels:
        if lbl.winfo_exists():
            lbl.config(foreground=PSA_HEADER_BLUE)
    messagebox.showinfo("Reset Successful", "Accessibility changes have been restored to default values.")

# ==========================================
# TRANSITION ANIMATION ENGINE
# ==========================================
def navigate_to(screen_drawing_function, *args, **kwargs):
    """
    PURPOSE: Navigate to a different screen/page in the application
    - Clears the current page from memory
    - Removes all widgets from the display area
    - Shows loading message for better UX
    - Calls the new screen's drawing function with provided arguments
    - Updates navigation bar state (buttons, labels) based on current screen
    
    PARAMETERS:
    - screen_drawing_function: The function that draws the new screen
    - *args, **kwargs: Arguments to pass to the screen drawing function
    """
    global current_active_page_ref, accessibility_labels

    # Clear the current page reference and accessibility labels
    current_active_page_ref = None  
    accessibility_labels = [] 

    # Update the navigation bar to show appropriate buttons/labels for new page
    update_navbar_state(screen_drawing_function)

    # Remove all widgets from the content area (clear the screen)
    for widget in content_frame.winfo_children():
        widget.destroy()

    # Show a loading message while the new screen is being drawn
    loading_lbl = tb.Label(content_frame, text="Loading interface context...", font=("Helvetica", 12, "italic"), bootstyle="secondary")
    loading_lbl.pack(expand=True)

    # Schedule the new screen to be drawn after a 250ms delay (for smooth loading animation)
    root.after(250, lambda: execution_wrap(loading_lbl, screen_drawing_function, *args, **kwargs))

def execution_wrap(loader_widget, target_function, *args, **kwargs):
    """
    PURPOSE: Helper function that removes the loading indicator and draws the new screen
    - Removes the loading message widget
    - Calls the target function to draw the actual screen
    - Allows for smooth visual transition between pages
    """
    # Remove the loading message
    loader_widget.destroy()
    # Draw the new screen with provided arguments
    target_function(*args, **kwargs)

# =====================================================================
# =====================================================================
# AUTHENTICATION BUSINESS LOGIC
# =====================================================================
def verify_user_n_passcode():
    """
    PURPOSE: Verify user credentials against the account database
    - Checks if username and password combination is valid
    - Supports both admin login and employee login
    - Employees can login with username OR email
    - Sets CURRENT_LOGGED_IN_USER global variable on success
    - Displays appropriate error messages on failure
    
    LOGIN SCENARIOS:
    1. Hardcoded admin account (username: "admin", password: "admin123")
    2. Employee login by username (checks account_database keys)
    3. Employee login by email (checks account_database values)
    """
    global CURRENT_LOGGED_IN_USER
    
    # Get username and password from login form
    entered_username = username_var.get().strip()
    entered_password = password_var.get().strip()

    # Validate that both fields are filled
    if not entered_username or not entered_password:
        login_error_var.set("Fields cannot be empty")
        return

    # SCENARIO 1: Admin login (hardcoded credentials for system administrator)
    if entered_username == "admin" and entered_password == "admin123":
        CURRENT_LOGGED_IN_USER = "admin"  # Mark as admin
        login_error_var.set("")            # Clear any previous errors
        username_var.set("")               # Clear username field
        password_var.set("")               # Clear password field
        messagebox.showinfo("Access Approved", "Logged in as System Administrator.")
        navigate_to(main_menu_screen)      # Go to main menu
        return

    # SCENARIO 2: Employee login by username
    # Check if entered text matches an employee ID (key in dictionary)
    if entered_username in account_database:
        user_data = account_database[entered_username]
        if entered_password == user_data["password"]:
            # Password is correct - login successful
            CURRENT_LOGGED_IN_USER = entered_username
            login_error_var.set("")
            username_var.set("")
            password_var.set("")
            messagebox.showinfo("Success", "Log in successful")
            navigate_to(main_menu_screen)
            return
        else:
            # Password is wrong
            login_error_var.set("Wrong Password")
            return
        
    # SCENARIO 3: Employee login by email (fallback if username doesn't match)
    # Loop through all employees and check if entered text matches email
    for employee_id, data in account_database.items():
        if entered_username == data.get("email"):
            # Found matching email - now check password
            if entered_password == data["password"]:
                # Password is correct - login successful
                CURRENT_LOGGED_IN_USER = employee_id  # Use employee ID for session
                login_error_var.set("")
                username_var.set("")
                password_var.set("")
                messagebox.showinfo("Success", "Log in successful")
                navigate_to(main_menu_screen)
                return
            else:
                # Password is wrong
                login_error_var.set("Wrong Password")
                return

    # SCENARIO 4: User not found in database
    login_error_var.set("User not found")

# =====================================================================
# UTILITY FUNCTIONS
# =====================================================================
def generate_person_id():
    """
    PURPOSE: Generate the next unique Person ID for a new account
    - Each employee gets a unique Person ID starting with "P-" prefix
    - IDs are sequential (P-10001, P-10002, P-10003, etc.)
    - This ensures no two employees have the same ID
    - Used during account creation to identify employees in database
    """

    if not account_database:
        # If this is the first account, start with P-10001
        return "P-10001"

    # Find the highest existing ID number
    last_id = max(
        int(data["person_id"].split("-")[1])
        for data in account_database.values()
    )

    # Generate next ID by incrementing the highest one
    return f"P-{last_id + 1}"

def get_current_date():
    """
    PURPOSE: Returns today's date in YYYY-MM-DD format
    - Used for timestamping account creation and modifications
    - Provides consistent date formatting throughout the system
    """
    return datetime.now().strftime("%Y-%m-%d")

# =====================================================================
# ACCOUNT CREATION & MANAGEMENT
# =====================================================================
def add_account():
    """
    PURPOSE: Create a new employee account in the system
    - Validates form input (no empty fields, matching passwords)
    - Checks for duplicate emails and reserved usernames
    - Generates unique person_id for the new account
    - Saves account to CSV file and audit logs
    - Logs the account creation event for audit trail
    
    VALIDATION STEPS:
    1. All fields must be filled (username, email, password)
    2. Passwords must match exactly
    3. Username cannot be 'admin' (reserved)
    4. Email must be unique (not used by another account)
    5. Admin must confirm creation via dialog
    """
    # Get form input values
    new_username = new_username_var.get().strip()
    new_email = new_email_var.get().strip()
    new_password = new_password_var.get().strip()
    confirm_password = confirm_new_password_var.get().strip()
    signup_error_var.set("")

    # VALIDATION 1: Check that all fields are filled
    if new_username == "" or new_email == "" or new_password == "":
        signup_error_var.set("Some fields are blank. please fill them all")
        return
    
    # VALIDATION 2: Check that passwords match
    if new_password != confirm_password:
        signup_error_var.set("Mismatched Passwords, try again")
        return
        
    # VALIDATION 3: Check that username is not 'admin' (reserved)
    if new_username.lower() == "admin":
        signup_error_var.set("Username 'admin' is reserved.")
        return
    
    # VALIDATION 4: Check that email and username is not already registered
    for employee_id, data in account_database.items():
        if new_email == data.get("email"):
            signup_error_var.set("Email already exists.")
            return
        if new_username.lower() == employee_id.lower():
            signup_error_var.set("Username already exists.")
            return


    # CONFIRMATION: Ask admin to confirm account creation
    confirm = messagebox.askyesno("Create Account", f"Write account '{new_username}' to CSV?")
    if confirm:
        # Add new account to the in-memory database
        account_database[new_username] = {
            "person_id": generate_person_id(),  # Generate unique ID
            "email": new_email,
            "password": new_password,
            "created_id": get_current_date(),   # Record creation date
            "modified_id": get_current_date()   # Record last modification date
        }
        
        # Save the new account to CSV file
        save_accounts_to_csv()
        record_accounts()  # Update any account-related records
        
        # Log the account creation for audit trail
        log_employee_action(new_username, "account created")
        
        # Clear all form fields after successful creation
        new_username_var.set("")
        new_email_var.set("")
        new_password_var.set("")
        confirm_new_password_var.set("")
        signup_error_var.set("")
        
        navigate_to(main_menu_screen)

def initiate_forgot_password_sequence():
    """
    PURPOSE: Start the password reset process by generating an OTP
    - User enters username to reset password
    - Validates that username exists in database
    - Generates 6-digit OTP (One-Time Password) code
    - Stores OTP temporarily in otp_requests_database
    - Displays OTP to user (for development/demo purposes)
    - Navigates to OTP verification screen
    
    SECURITY NOTE: In production, OTP should be sent via email, not displayed on screen
    """
    target_user = forget_username_var.get().strip()

    if target_user not in account_database:
        print(f"DEBUG: {target_user} not found in database! Keys available: {list(account_database.keys())}")
        forget_error_var.set("Username not found.")
        return
    
    # Confirm that we have a valid username
    matched_username = target_user

    # Generate a random 6-digit OTP code
    generated_token = f"{random.randint(100000, 999999)}"

    # Store the OTP temporarily (linked to the user and timestamp)
    otp_requests_database[matched_username] = {
        "otp": generated_token,
        "timestamp": datetime.now()
    }

    # Display the generated OTP to the user (DEBUG - normally would email this)
    messagebox.showinfo("DEV DEBUG LOG", f"Generated OTP for {matched_username}: {generated_token}")
    messagebox.showinfo("OTP Sent", f"An OTP modification token has been directed to the Admin side. Please coordinate to receive your token.")
    forget_error_var.set("")

    # Navigate to the OTP entry screen, passing the username
    navigate_to(otp_verification_screen, matched_username)

def execute_otp_validation_check(target_user):
    """
    PURPOSE: Verify that the user entered the correct OTP code
    - User enters the 6-digit OTP that was generated
    - Compares user input against the stored OTP
    - If valid: proceeds to password entry screen
    - If invalid: shows error and requests retry
    
    SECURITY: Prevents unauthorized password changes even if someone accesses the form
    """
    user_entry = entered_otp_var.get().strip()

    # Validate that OTP field is not empty
    if not user_entry:
        forget_error_var.set("OTP validation field cannot remain empty.")
        return

    # Check if an OTP request exists for this user
    if target_user not in otp_requests_database:
        forget_error_var.set("Session signature broken. Re-initiate reset pipeline workflow.")
        return

    # Get the correct OTP that was generated
    correct_token = otp_requests_database[target_user]["otp"]

    # Compare user's entry against the correct OTP
    if user_entry == correct_token:
        # OTP is correct - proceed to password reset
        forget_error_var.set("")
        entered_otp_var.set("")
        navigate_to(reset_password_entry_screen, target_user)
    else:
        # OTP is incorrect - show error
        forget_error_var.set("Invalid OTP validation verification string match failure.")

def finalize_password_override(target_user):
    try:
        """
        PURPOSE: Complete the password reset by updating the password in the database
        - User enters new password (twice for confirmation)
        - Validates passwords match and are not empty
        - Handles both old and new account data formats
        - Updates password in account_database
        - Saves changes to CSV file
        - Logs password change for audit trail
        - Returns user to login screen
        
        SECURITY: Passwords are hashed in production (currently stored in plaintext for demo)
        """
        if target_user is None:
            forget_error_var.set("ERROR: No valid user selected. Please restart the password reset process.")
            navigate_to(login_screen)
            return

        # Get the new passwords from the form
        pwd1 = reset_new_password_var.get().strip()
        pwd2 = reset_confirm_password_var.get().strip()

        # Validate that both password fields are filled
        if not pwd1 or not pwd2:
            forget_error_var.set("Input entries must remain populated.")
            return

        # Validate that both passwords match exactly
        if pwd1 != pwd2:
            forget_error_var.set("Validation parameters mismatch. Passwords must match.")
            return

        # Get the user's account data
        user_data = account_database.get(target_user)

        # Handle backward compatibility: convert old list format to new dict format
        if isinstance(user_data, list):
            # OLD FORMAT: ["email", "password"] - convert to new format
            user_data = {"email": user_data[0], "password": user_data[1], "person_id": "N/A", "created_id": "N/A", "modified_id": "N/A"}
            account_database[target_user] = user_data

        # Update the password in the account database
        account_database[target_user]["password"] = pwd1

        # Save all account changes back to CSV file
        save_accounts_to_csv()

        # Log this password change event for audit trail
        log_employee_action(target_user, "changed password")
        messagebox.showinfo("Success", "Password updated successfully!")

        # Clear all password reset form fields
        forget_username_var.set("")
        reset_new_password_var.set("")
        reset_confirm_password_var.set("")
        forget_error_var.set("")

        # Return user to login screen so they can login with new password
        navigate_to(login_screen)
        
    except Exception as e:
        print(f"CRITICAL ERROR IN FINALIZE_PASSWORD: {e}")
        traceback.print_exc() # This will print the exact line causing the crash
        messagebox.showerror("Error", f"Could not update password: {e}")

def record_accounts():
    # Ensure the file is opened correctly
    with open(ACCOUNTS_FILE, "w", newline="", encoding="utf-8") as file:
        fieldnames = [
            "employee_id",
            "person_id",
            "email",
            "password",
            "created_id",
            "modified_id"
        ]

        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        # FIX: Iterate over account_database
        for employee_id, data in account_database.items():
            
            # Add a check to prevent crashes if data is malformed
            if isinstance(data, dict):
                writer.writerow({
                    "employee_id": employee_id,
                    "person_id": data.get("person_id", "N/A"),
                    "email": data.get("email", "N/A"),
                    "password": data.get("password", "N/A"),
                    "created_id": data.get("created_id", "N/A"),
                    "modified_id": data.get("modified_id", "N/A")
                })


# ==========================================
# AUTHENTICATION VISUAL INTERFACES
# ==========================================
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

def login_screen():
    """
    PURPOSE: Display the user login screen
    - Shows username/email and password input fields
    - Provides "Sign In" button to authenticate user
    - Shows "Forgot Password?" link for password reset
    - Displays error messages for failed login attempts
    - First screen users see when starting the application
    """
    container = tb.Frame(content_frame, padding=30)
    container.pack(expand=True)

    # Get current theme to apply appropriate colors
    current_theme = root.style.theme.name
    heading_fg = "white" if current_theme in ["darkly", "superhero"] else PSA_HEADER_BLUE

    # Display title labels
    tb.Label(container, text="Error Collection System", font=("Helvetica", 14, "italic"), foreground="grey").pack(pady=(0, 5))
    tb.Label(container, text="User Login Portal", font=("Helvetica", 22, "bold"), foreground=heading_fg).pack(pady=(0, 25))

    # Username/email input field
    tb.Label(container, text="Username / Email: ", font=("Helvetica", 11)).pack(anchor="w", pady=(5, 2))
    ent_user = tb.Entry(container, textvariable=username_var, width=42)
    ent_user.pack(pady=5, fill="x")

    # Password input field (masked with asterisks)
    tb.Label(container, text="Password: ", font=("Helvetica", 11)).pack(anchor="w", pady=(5, 2))
    ent_pass = tb.Entry(container, textvariable=password_var, show="*", width=42)
    ent_pass.pack(pady=5, fill="x")

    # Error message label (shown when login fails)
    err_lbl = tb.Label(container, textvariable=login_error_var, bootstyle="danger", font=("Helvetica", 10, "bold"))
    err_lbl.pack(pady=5)

    # Button row for login button
    btn_row = tb.Frame(container)
    btn_row.pack(fill="x", pady=15)

    # Sign In button - calls verify_user_n_passcode to authenticate
    login_btn = LiftedRoundedButton(btn_row, text="Sign In", image=None, command=verify_user_n_passcode, variant="primary", width=160, height=45)
    login_btn.pack(pady=5, fill="x")

    # Links for forgot password recovery
    links_row = tb.Frame(container)
    links_row.pack(fill="x", pady=5)
    tb.Button(links_row, text="Forgot Password?", bootstyle="link", command=lambda: navigate_to(forget_screen)).pack(anchor="center", expand=True)

def signup_screen():
    """
    PURPOSE: Display the account creation screen for admins to create new employee accounts
    - Takes username, email, password for the new account
    - Validates all inputs (no duplicates, matching passwords)
    - Creates unique Person ID for the employee
    - Saves account to CSV file
    - Logs the account creation event
    - Shows success/error messages
    """
    container = tb.Frame(content_frame, padding=30)
    container.pack(expand=True)

    # Get current theme for consistent styling
    current_theme = root.style.theme.name
    heading_fg = "white" if current_theme in ["darkly", "superhero"] else PSA_HEADER_BLUE

    # Page title
    tb.Label(container, text="Register New Account", font=("Helvetica", 22, "bold"), foreground=heading_fg).pack(pady=(0, 25))

    # Username input field
    tb.Label(container, text="Enter Username", font=("Helvetica", 11)).pack(anchor="w", pady=(5, 2))
    tb.Entry(container, textvariable=new_username_var, width=42).pack(pady=5, fill="x")

    # Email address input field
    tb.Label(container, text="Enter Email Address", font=("Helvetica", 11)).pack(anchor="w", pady=(5, 2))
    tb.Entry(container, textvariable=new_email_var, width=42).pack(pady=5, fill="x")

    # Password input field
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

def otp_verification_screen(target_user):
    container = tb.Frame(content_frame, padding=30)
    container.pack(expand=True)

    current_theme = root.style.theme.name
    heading_fg = "white" if current_theme in ["darkly", "superhero"] else PSA_HEADER_BLUE

    tb.Label(container, text="Enter Security OTP String", font=("Helvetica", 20, "bold"), foreground=heading_fg).pack(pady=(0, 10))
    tb.Label(container, text=f"Account Target Identity Context: {target_user}", font=("Helvetica", 11, "italic")).pack(pady=(0, 20))

    tb.Label(container, text="6-Digit OTP Code Sequence", font=("Helvetica", 11)).pack(anchor="w", pady=(5, 2))
    tb.Entry(container, textvariable=entered_otp_var, width=42, justify="center").pack(pady=5, fill="x")

    tb.Label(container, textvariable=forget_error_var, bootstyle="danger", font=("Helvetica", 10, "bold")).pack(pady=5)

    btn_verify = LiftedRoundedButton(container, text="Verify Verification Token", image=None, command=lambda: execute_otp_validation_check(target_user), variant="primary", width=160, height=45)
    btn_verify.pack(pady=10, fill="x")

    tb.Button(container, text="Back to Login Screen", bootstyle="secondary-link", command=lambda: navigate_to(login_screen)).pack()

def reset_password_entry_screen(target_user):
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
    btn_finalize = LiftedRoundedButton(container, text="Finalize Password Changes", image=None, command=lambda: finalize_password_override(target_user), variant="primary", width=160, height=45)
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
    # Removed momEntry and dadEntry globals since they are no longer used
    global birth_regEntry, birth_errorType, youEntry, borigEntry, bnewEntry, bexplain, cert_choice
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
    # --- Mother and Father validations removed from here ---
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
    # Removed momEntry and dadEntry globals from the UI constructor
    global birth_regEntry, youEntry, birth_errorType, borigEntry, bnewEntry, bexplain
    container = tb.Frame(content_frame, padding=30)
    container.pack(expand=True, fill="both")
    container.columnconfigure(1, weight=1)

    # Row 0: Registry Number
    tb.Label(container, text="Registry Number: ", anchor="w").grid(row=0, column=0, sticky="w", pady=8, padx=10)
    birth_regEntry = tb.Entry(container)
    birth_regEntry.grid(row=0, column=1, sticky="ew", pady=8, padx=10)

    # Row 1: Name
    tb.Label(container, text="Name: ", anchor="w").grid(row=1, column=0, sticky="w", pady=8, padx=10)
    youEntry = tb.Entry(container)
    youEntry.grid(row=1, column=1, sticky="ew", pady=8, padx=10)

    # --- Mother and Father input entry blocks completely removed from here ---

    # Row 2 (Shifted up): Type of Error
    tb.Label(container, text="Type of Error: ", anchor="w").grid(row=2, column=0, sticky="w", pady=8, padx=10)
    birth_errorType = tb.Combobox(container, values=["Date of Birth", "Sex", "Place of Birth", "Father Details", "Mother Details", "Type of Birth", "Nationality","Birth Order", "Other (Specify in Explanations)"], state="readonly")
    birth_errorType.grid(row=2, column=1, sticky="ew", pady=8, padx=10)

    # Row 3 (Shifted up): Original Value
    tb.Label(container, text="Original Value: ", anchor="w").grid(row=3, column=0, sticky="w", pady=8, padx=10)
    borigEntry = tb.Entry(container)
    borigEntry.grid(row=3, column=1, sticky="ew", pady=8, padx=10)

    # Row 4 (Shifted up): Revised Value
    tb.Label(container, text="Revised Value: ", anchor="w").grid(row=4, column=0, sticky="w", pady=8, padx=10)
    bnewEntry = tb.Entry(container)
    bnewEntry.grid(row=4, column=1, sticky="ew", pady=8, padx=10)

    # Row 5 (Shifted up): Explanation
    tb.Label(container, text="Explanation: ", anchor="w").grid(row=5, column=0, sticky="w", pady=8, padx=10)
    bexplain = tb.Entry(container)
    bexplain.grid(row=5, column=1, sticky="ew", pady=8, padx=10)

    # Row 6 (Shifted up): Buttons Frame
    btn_frame = tb.Frame(container)
    btn_frame.grid(row=6, column=0, columnspan=2, pady=25)

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

    btn_next = LiftedRoundedButton(btn_frame, text="Proceed to Form", image=None, command=route_form, variant="primary", width=160+60, height=45)
    btn_next.pack(side=LEFT, padx=10)

    btn_back = LiftedRoundedButton(btn_frame, text="Main Menu", image=None, command=lambda: navigate_to(main_menu_screen), variant="default", width=160+60, height=45)
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
    
    bottom_bar = tb.Frame(container, padding=(0, 10, 0, 0))
    bottom_bar.pack(fill="x", side=BOTTOM)
    
    LiftedRoundedButton(bottom_bar, text="Back to Main Menu", image=None, command=lambda: navigate_to(main_menu_screen), variant="default", width=180+60, height=45, text_size=12).pack(side=LEFT, padx=5)
    
    if show_enter_new:
        LiftedRoundedButton(top_bar, text="Log Another Entry", image=None, command=lambda: navigate_to(entry_system_screen), variant="primary", width=180+60, height=40, text_size=11).pack(side=RIGHT, padx=5)

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
    
    bottom_bar = tb.Frame(container, padding=(0, 10, 0, 0))
    bottom_bar.pack(fill="x", side=BOTTOM)
    LiftedRoundedButton(bottom_bar, text="Back to Main Menu", image=None, command=lambda: navigate_to(main_menu_screen), variant="default", width=180+60, height=45, text_size=12).pack(side=LEFT, padx=5)
    
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
    
    bottom_bar = tb.Frame(container, padding=(0, 10, 0, 0))
    bottom_bar.pack(fill="x", side=BOTTOM)
    LiftedRoundedButton(bottom_bar, text="Back to Main Menu", image=None, command=lambda: navigate_to(main_menu_screen), variant="default", width=180+60, height=45, text_size=12).pack(side=LEFT, padx=5)
    
    apply_font_sizes()

def accessibility_screen():
    container = tb.Frame(content_frame, padding=15)
    container.pack(expand=True, fill="both")

    current_theme = root.style.theme.name
    heading_fg = "white" if current_theme in ["darkly", "superhero"] else PSA_HEADER_BLUE

    ctrl_row = tb.Frame(container)
    ctrl_row.pack(fill="x", side=BOTTOM, pady=(10, 0))
    
    LiftedRoundedButton(ctrl_row, text="Reset to Factory Defaults", image=None, command=reset_settings, variant="muted_danger", width=220+60, height=45).pack(side=LEFT, padx=5)
    LiftedRoundedButton(ctrl_row, text="Back to Home Menu", image=None, command=lambda: navigate_to(main_menu_screen), variant="default", width=180+60, height=45, text_size=12).pack(side=LEFT, padx=5)

    tb.Label(container, text="Control and Diagnostics Center", font=("Helvetica", 22, "bold"), foreground=heading_fg).pack(anchor="w", pady=(0, 10))

    sect_theme = tb.Labelframe(container, text=" Display & Styling Preferences ", padding=15)
    sect_theme.pack(fill="x", pady=5)
    
    lbl_theme = tb.Label(sect_theme, text="Select Master UI Palette Skin Mode:", font=("Helvetica", 11, "bold"), foreground=PSA_HEADER_BLUE)
    lbl_theme.pack(anchor="w", pady=(0, 5))
    accessibility_labels.append(lbl_theme)

    theme_btn_row = tb.Frame(sect_theme)
    theme_btn_row.pack(anchor="w", pady=5)

    LiftedRoundedButton(theme_btn_row, text="Light Theme", image=None, command=lightmode, variant="default", width=140+60, height=45).pack(side=LEFT, padx=5)
    LiftedRoundedButton(theme_btn_row, text="Dark Mode", image=None, command=darkmode, variant="accent", width=140+60, height=45).pack(side=LEFT, padx=5)
    LiftedRoundedButton(theme_btn_row, text="Slate High Contrast", image=None, command=greymode, variant="grey_button", width=180+60, height=45).pack(side=LEFT, padx=5)

    sect_font = tb.Labelframe(container, text=" Font Resizing & Scale Adaptability Engine ", padding=15)
    sect_font.pack(fill="x", pady=5)

    lbl_font = tb.Label(sect_font, text="Global Application UI Text Scaling controls:", font=("Helvetica", 11, "bold"), foreground=PSA_HEADER_BLUE)
    lbl_font.pack(anchor="w", pady=(0, 5))
    accessibility_labels.append(lbl_font)

    font_btn_row = tb.Frame(sect_font)
    font_btn_row.pack(anchor="w", pady=5)

    LiftedRoundedButton(font_btn_row, text="A+  Enlarge App Font", image=None, command=increase_font, variant="default", width=180+60, height=45, text_size=12).pack(side=LEFT, padx=5)
    LiftedRoundedButton(font_btn_row, text="A-  Shrink App Font", image=None, command=decrease_font, variant="default", width=180+60, height=45, text_size=12).pack(side=LEFT, padx=5)

    lbl_table = tb.Label(sect_font, text="Tabular Metadata Rows Resizing engine:", font=("Helvetica", 11, "bold"), foreground=PSA_HEADER_BLUE)
    lbl_table.pack(anchor="w", pady=(10, 5))
    accessibility_labels.append(lbl_table)

    table_btn_row = tb.Frame(sect_font)
    table_btn_row.pack(anchor="w", pady=5)

    LiftedRoundedButton(table_btn_row, text="Increase Rows Font", image=None, command=increase_table_font, variant="default", width=180+60, height=45, text_size=11).pack(side=LEFT, padx=5)
    LiftedRoundedButton(table_btn_row, text="Decrease Rows Font", image=None, command=decrease_table_font, variant="default", width=180+60, height=45, text_size=11).pack(side=LEFT, padx=5)
    
    if current_theme in ["darkly", "superhero"]:
        for lbl in accessibility_labels:
            lbl.config(foreground="white")

def main_menu_screen():
    local_icon_scale = 10
    main_container = tb.Frame(content_frame)
    main_container.pack(expand=True, fill="both", padx=40, pady=20)
    
    # ADD THIS LINE: It forces the window to calculate sizes immediately
    main_container.update_idletasks()

    # Try loading a unique icon file for each of the 6 buttons
    # --- CRISP IMAGE LOADING WITH PILLOW ---
    # add
    try:
        path_1 = os.path.join(base_dir, "images", "1.png")
        img_plus = Image.open(path_1)
        resized_plus = img_plus.resize((img_plus.width // 13, img_plus.height // 13), Image.Resampling.LANCZOS)
        icon1 = ImageTk.PhotoImage(resized_plus)
    except Exception as e:
        print(f"Could not load plus image: {e}")
        icon1 = None  

    # paper
    try:
        path_2 = os.path.join(base_dir, "images", "2.png")
        img_paper = Image.open(path_2)
        resized_paper = img_paper.resize((img_paper.width // 10, img_paper.height // 10), Image.Resampling.LANCZOS)
        icon2 = ImageTk.PhotoImage(resized_paper)
    except Exception as e:
        print(f"Could not load paper image: {e}")
        icon2 = None

    # gear
    try:
        path_6 = os.path.join(base_dir, "images", "6.png")
        img_gear = Image.open(path_6)
        resized_gear = img_gear.resize((img_gear.width // 12, img_gear.height // 12), Image.Resampling.LANCZOS)
        gear = ImageTk.PhotoImage(resized_gear)
    except Exception as e:
        print(f"Could not load gear image: {e}")
        gear = None

    try:
        # profile
        path_4 = os.path.join(base_dir, "images", "4.png")
        profile_paper = Image.open(path_4)
        resized_profile = profile_paper.resize((profile_paper.width // 12, profile_paper.height // 12), Image.Resampling.LANCZOS)
        icon4 = ImageTk.PhotoImage(resized_profile)

        # clipboard
        path_5 = os.path.join(base_dir, "images", "5.png")
        clipboard = Image.open(path_5)
        resized_cb = clipboard.resize((clipboard.width // 10, clipboard.height // 10), Image.Resampling.LANCZOS)
        icon5 = ImageTk.PhotoImage(resized_cb)

        # add friend
        path_3 = os.path.join(base_dir, "images", "3.png")
        add_friend = Image.open(path_3)
        resized_af = add_friend.resize((add_friend.width // 10, add_friend.height // 10), Image.Resampling.LANCZOS)
        icon6 = ImageTk.PhotoImage(resized_af)

    except Exception as e:
        print(f"Could not load secondary icons: {e}")
        icon4 = icon5 = icon6 = None

    # DYNAMIC RENDER INTERFACES: ADMIN vs REGULAR EMPLOYEE
    if CURRENT_LOGGED_IN_USER == "admin":
        main_container.columnconfigure(0, weight=1, uniform="cols")
        main_container.columnconfigure(1, weight=1, uniform="cols")
        main_container.columnconfigure(2, weight=1, uniform="cols")
        main_container.rowconfigure(0, weight=1, uniform="rows")
        main_container.rowconfigure(1, weight=1, uniform="rows")

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
            main_container, text="Security Employee Logs", image=icon4, compound="top",
            command=lambda: navigate_to(call_employee_logs_view), variant="default", text_size=18
        )
        btn_emp_logs.image_cache = gear
        btn_emp_logs.grid(row=0, column=2, sticky="nsew", padx=15, pady=15)

        btn_create_acc = LiftedRoundedButton(
            main_container, text="Register New Account", image=icon6, compound="top",
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
            main_container, text="Settings & Accessibility", image=gear, compound="top",
            command=lambda: navigate_to(accessibility_screen), variant="default", text_size=18
        )
        btn_settings.image_cache = icon6
        btn_settings.grid(row=1, column=2, sticky="nsew", padx=15, pady=15)

    else:
        main_container.columnconfigure(0, weight=1, uniform="cols")
        main_container.columnconfigure(1, weight=1, uniform="cols")
        main_container.rowconfigure(0, weight=1)

        btn_create = LiftedRoundedButton(
            main_container, text="Create New Entry Log", image=icon1, compound="top",
            command=lambda: navigate_to(entry_system_screen), variant="default", text_size=22
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
            right_sub_container, text="Settings and Accessibility", image=gear, compound="left",
            command=lambda: navigate_to(accessibility_screen), width=320, height=90, variant="default", text_size=18
        )
        btn_settings.image_cache = gear
        btn_settings.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)

# ==========================================
# BOOT EXECUTION LAYER TRIGGER
# ==========================================
if __name__ == "__main__":
    navigate_to(login_screen)
    root.mainloop()