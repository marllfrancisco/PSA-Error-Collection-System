import re
import mysql.connector
from mysql.connector import Error
import ttkbootstrap as tb  
from ttkbootstrap.constants import *
from tkinter import messagebox
import uuid  # Imported to generate unique IDs for VARCHAR(20) primary keys

# ==========================================
# DATABASE CONNECTION SETUP
# ==========================================
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',          
    'password': '',          
    'database': 'ecorrectdb'
}

ACTIVE_EMPLOYEE_ID = 1 

def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            return connection
    except Error as e:
        messagebox.showerror("Database Error", f"Could not connect to MySQL Database:\n{e}")
        return None

# ==========================================
# GUI MAIN APPLICATION INITIALIZATION
# ==========================================
root = tb.Window(themename="flatly")

width = root.winfo_screenwidth() 
height = root.winfo_screenheight()
root.geometry("%dx%d" % (width, height))
root.title("PSA Error Collection System")
root.state('zoomed') 

DEFAULT_TITLE_SIZE = 25
DEFAULT_BODY_SIZE = 11

font_size_title = DEFAULT_TITLE_SIZE
font_size_default = DEFAULT_BODY_SIZE

def apply_font_sizes():
    Title.config(font=("Helvetica", font_size_title))
    style = tb.Style()
    style.configure('.', font=("Helvetica", font_size_default))          
    style.configure('TLabel', font=("Helvetica", font_size_default))     
    style.configure('TButton', font=("Helvetica", font_size_default))    
    style.configure('TEntry', font=("Helvetica", font_size_default))     
    style.configure('TCombobox', font=("Helvetica", font_size_default))  

def increase_font():
    global font_size_title, font_size_default
    if font_size_default < 24:  
        font_size_title += 2
        font_size_default += 2
        apply_font_sizes()
    else:
        messagebox.showinfo("Font Limit", "Maximum font size reached.")

def decrease_font():
    global font_size_title, font_size_default
    if font_size_default > 8:  
        font_size_title -= 2
        font_size_default -= 2
        apply_font_sizes()
    else:
        messagebox.showinfo("Font Limit", "Minimum font size reached.")

def reset_settings():
    global font_size_title, font_size_default
    font_size_title = DEFAULT_TITLE_SIZE
    font_size_default = DEFAULT_BODY_SIZE
    root.style.theme_use("flatly")
    apply_font_sizes()
    messagebox.showinfo("Reset Successful", "Accessibility changes have been restored to default values.")

# Application Top Banner Header
Title = tb.Label(root, text="PSA Error Collection System", font=("Helvetica", font_size_title), bootstyle="inverse-primary", anchor="center")
Title.pack(pady=20, fill="x")

# Dynamic Central Content Container Frame
content_frame = tb.Frame(root, padding=20)
content_frame.pack(expand=True, fill="both")

cert_choice = ""
LABEL_WIDTH = 25  
ENTRY_WIDTH = 40  

def update_entry(event):
    global cert_choice
    cert_choice = certType.get()

def darkmode():
    root.style.theme_use("darkly")
    apply_font_sizes() 

def lightmode():
    root.style.theme_use("flatly")
    apply_font_sizes()

def greymode():
    root.style.theme_use("superhero")
    apply_font_sizes()

# ==========================================
# TRANSITION ANIMATION ENGINE
# ==========================================
def navigate_to(screen_drawing_function, *args, **kwargs):
    """
    Clears the container frame, creates a brief visual processing pause 
    using a micro-delay, and then safely loads the next destination layout.
    """
    # Step 1: Wipe current view content immediately 
    for widget in content_frame.winfo_children():
        widget.destroy()
        
    # Step 2: Render a brief stylized status message or placeholder
    loading_lbl = tb.Label(content_frame, text="Loading interface context...", font=("Helvetica", 12, "italic"), bootstyle="secondary")
    loading_lbl.pack(expand=True)
    
    # Step 3: Run safe asynchronous mainloop schedule drop to prevent UI freezing
    root.after(250, lambda: execution_wrap(loading_lbl, screen_drawing_function, *args, **kwargs))

def execution_wrap(loader_widget, target_function, *args, **kwargs):
    """Removes the loading notice and renders the next frame setup securely."""
    loader_widget.destroy()
    target_function(*args, **kwargs)

def fetch_all_results():
    conn = get_db_connection()
    if not conn:
        return []
    
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT dr.report_id, dr.registry_number, dr.status, de.cert_type, de.explanation, de.error_field, de.original_value, de.revised_value
            FROM discrepancy_report dr
            JOIN discrepancy_entries de ON dr.report_id = de.report_id
            ORDER BY dr.report_id DESC
        """
        cursor.execute(query)
        return cursor.fetchall()
    except Error as e:
        messagebox.showerror("Database Error", f"Error fetching results:\n{e}")
        return []
    finally:
        cursor.close()
        conn.close()

def results_panel_screen(post_entry=False):
    container = tb.Frame(content_frame, padding=30)
    container.pack(expand=True, fill="both")

    lbl_header = tb.Label(container, text="All Reported Discrepancies", font=("Helvetica", 16, "bold"), anchor="center")
    lbl_header.pack(fill="x", pady=(0, 20))

    # Use a Treeview for the results panel
    columns = ("id", "reg", "type", "field", "original", "revised", "status")
    tree = tb.Treeview(container, columns=columns, show="headings", bootstyle="primary")
    
    tree.heading("id", text="Report ID")
    tree.heading("reg", text="Registry No")
    tree.heading("type", text="Cert Type")
    tree.heading("field", text="Error Field")
    tree.heading("original", text="Original")
    tree.heading("revised", text="Revised")
    tree.heading("status", text="Status")

    tree.column("id", width=100)
    tree.column("reg", width=100)
    tree.column("type", width=100)
    tree.column("field", width=120)
    tree.column("original", width=120)
    tree.column("revised", width=120)
    tree.column("status", width=80)

    results = fetch_all_results()
    cert_type_reverse_map = {1: "Birth", 2: "Marriage", 3: "Death"}

    for row in results:
        tree.insert("", "end", values=(
            row['report_id'], 
            row['registry_number'], 
            cert_type_reverse_map.get(row['cert_type'], "Unknown"), 
            row['error_field'], 
            row['original_value'], 
            row['revised_value'], 
            row['status']
        ))

    tree.pack(expand=True, fill="both", pady=10)

    btn_row = tb.Frame(container)
    btn_row.pack(fill="x", pady=20)
    
    if post_entry:
        enter_another_but = tb.Button(btn_row, text="Enter another entry", command=lambda: navigate_to(entry_system_screen), bootstyle="success")
        enter_another_but.pack(side=LEFT, padx=10, expand=True)
        back_but = tb.Button(btn_row, text="Return to main menu", command=lambda: navigate_to(main_menu_screen), bootstyle="danger")
        back_but.pack(side=LEFT, padx=10, expand=True)
    else:
        back_but = tb.Button(btn_row, text="Back to Main Menu", command=lambda: navigate_to(main_menu_screen), bootstyle="danger")
        back_but.pack(side=LEFT, padx=10, expand=True)

def save_discrepancy_to_db(registry_num, error_type, explanation, field_name, original_val, revised_val):
    conn = get_db_connection()
    if not conn:
        return False
    
    # Using buffered=True prevents the "Unread result found" error entirely
    cursor = conn.cursor(buffered=True)
    try:
        # Generate random unique 20-character strings for your VARCHAR schema IDs
        report_id = str(uuid.uuid4())[:20]
        discrepancy_id = str(uuid.uuid4())[:20]

        # 1. Insert into discrepancy_report (Matches DB Dump table name exactly)
        report_query = """
            INSERT INTO discrepancy_report (report_id, employee_id, registry_number, status) 
            VALUES (%s, %s, %s, 'PENDING')
        """
        cursor.execute(report_query, (report_id, ACTIVE_EMPLOYEE_ID, registry_num))

        # Map certificate types to matches: 1=Birth, 2=Marriage, 3=Death
        global cert_choice
        cert_type_map = {"Birth Certificate": 1, "Marriage Certificate": 2, "Death Certificate": 3}
        current_cert_type = cert_type_map.get(cert_choice, 1)

        # 2. Insert into discrepancy_entries (Matches DB Dump table name and 'error_field' column)
        entry_query = """
            INSERT INTO discrepancy_entries (discrepancy_id, report_id, cert_type, explanation, error_field, original_value, revised_value, modified_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(entry_query, (
            discrepancy_id, 
            report_id, 
            current_cert_type, 
            explanation, 
            field_name, 
            original_val, 
            revised_val, 
            ACTIVE_EMPLOYEE_ID
        ))
        
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
# FORM CONFIRMATION WINDOW LAYOUTS (IN-PLACE)
# ==========================================
def show_confirmation_screen(title_text, summary_data):
    container = tb.Frame(content_frame, padding=30)
    container.pack(expand=True)

    lbl_header = tb.Label(container, text=title_text, font=("Helvetica", 14, "bold"), anchor="w")
    lbl_header.pack(fill="x", pady=(0, 15))

    for label_text, entry_val in summary_data:
        row = tb.Frame(container)
        row.pack(fill="x", pady=5)
        lbl = tb.Label(row, text=label_text, width=LABEL_WIDTH, anchor="w")
        ent = tb.Entry(row, width=ENTRY_WIDTH)
        lbl.pack(side=LEFT)
        ent.pack(side=LEFT, fill="x", expand=True)
        ent.insert(0, entry_val)
        ent.config(state=DISABLED)

    btn_row = tb.Frame(container)
    btn_row.pack(fill="x", pady=20)
    
    close_but = tb.Button(btn_row, text="Back to Home", command=lambda: navigate_to(main_menu_screen), bootstyle="danger")
    close_but.pack(side=LEFT, padx=10, expand=True)
    
    new_button = tb.Button(btn_row, text="New Entry", command=lambda: navigate_to(entry_system_screen), bootstyle="success")
    new_button.pack(side=LEFT, padx=10, expand=True)

# ==========================================
# FORM SUBMISSIONS & VALIDATIONS
# ==========================================
def death_confirm():
    reg_pattern = r"^\d{4}-\d{7}$"
    if death_regEntry.get() == "":
        messagebox.showerror("Error", "Please input the proper Registration Number (ex. YYYY-XXXXXXX).")
        return
    elif not re.match(reg_pattern, death_regEntry.get()):
        messagebox.showerror("Error", "Invalid format! Registration Number must follow YYYY-XXXXXXX (e.g., 2026-1234567).")
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
            navigate_to(results_panel_screen, post_entry=True)
    else:
        messagebox.showinfo("Cancelled Input", "Your Entry has been Cancelled.")

def birth_confirm():
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
            navigate_to(results_panel_screen, post_entry=True)
    else:
        messagebox.showinfo("Cancelled Input", "Your Entry has been Cancelled.")

def marriage_confirm():
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
            navigate_to(results_panel_screen, post_entry=True)
    else:
        messagebox.showinfo("Cancelled Input", "Your Entry has been Cancelled.")

# ==========================================
# CENTRALIZED SCREEN DRAWING CONTROLLERS
# ==========================================
def birth_cert_screen():
    container = tb.Frame(content_frame, padding=30)
    container.pack(expand=True)

    row1 = tb.Frame(container)
    row1.pack(fill="x", pady=5)
    global birth_regEntry
    birth_reg = tb.Label(row1, text="Registry Number: ", width=LABEL_WIDTH, anchor="w")
    birth_regEntry = tb.Entry(row1, width=ENTRY_WIDTH)
    birth_reg.pack(side=LEFT)
    birth_regEntry.pack(side=LEFT, fill="x", expand=True)

    row2 = tb.Frame(container)
    row2.pack(fill="x", pady=5)
    global youEntry
    youTitle = tb.Label(row2, text="Name: ", width=LABEL_WIDTH, anchor="w")
    youEntry = tb.Entry(row2, width=ENTRY_WIDTH)
    youTitle.pack(side=LEFT)
    youEntry.pack(side=LEFT, fill="x", expand=True)

    row3 = tb.Frame(container)
    row3.pack(fill="x", pady=5)
    global momEntry
    momTitle = tb.Label(row3, text="Mother's Maiden Name: ", width=LABEL_WIDTH, anchor="w")
    momEntry = tb.Entry(row3, width=ENTRY_WIDTH)
    momTitle.pack(side=LEFT)
    momEntry.pack(side=LEFT, fill="x", expand=True)

    row4 = tb.Frame(container)
    row4.pack(fill="x", pady=5)
    global dadEntry
    dadTitle = tb.Label(row4, text="Father's Name: ", width=LABEL_WIDTH, anchor="w")
    dadEntry = tb.Entry(row4, width=ENTRY_WIDTH)
    dadTitle.pack(side=LEFT)
    dadEntry.pack(side=LEFT, fill="x", expand=True)
   
    row5 = tb.Frame(container)
    row5.pack(fill="x", pady=5)
    global birth_errorType
    birth_Title = tb.Label(row5, text="Select an Error: ", width=LABEL_WIDTH, anchor="w")
    bErrors = ["Date of Birth", "Sex", "Place of Birth", "Father Details", "Mother Details", "Birth Order", "Type of Birth"]
    birth_errorType = tb.Combobox(row5, values=bErrors, width=ENTRY_WIDTH-3, state='readonly')
    birth_errorType.set(" ")
    birth_Title.pack(side=LEFT) 
    birth_errorType.pack(side=LEFT, fill="x", expand=True)
    
    row6 = tb.Frame(container)
    row6.pack(fill="x", pady=5)
    global borigEntry
    borigTitle = tb.Label(row6, text="Erroneous Value: ", width=LABEL_WIDTH, anchor="w")
    borigEntry = tb.Entry(row6, width=ENTRY_WIDTH)
    borigTitle.pack(side=LEFT)
    borigEntry.pack(side=LEFT, fill="x", expand=True)
    
    row7 = tb.Frame(container)
    row7.pack(fill="x", pady=5)
    global bnewEntry
    bnewTitle = tb.Label(row7, text="New Value: ", width=LABEL_WIDTH, anchor="w")
    bnewEntry = tb.Entry(row7, width=ENTRY_WIDTH)
    bnewTitle.pack(side=LEFT)
    bnewEntry.pack(side=LEFT, fill="x", expand=True)

    row8 = tb.Frame(container)
    row8.pack(fill="x", pady=5)
    global bexplain
    bexplainTitle = tb.Label(row8, text="Explanation for the Change: ", width=LABEL_WIDTH, anchor="w")
    bexplain = tb.Entry(row8, width=ENTRY_WIDTH)
    bexplainTitle.pack(side=LEFT)
    bexplain.pack(side=LEFT, fill="x", expand=True)

    row9 = tb.Frame(container)
    row9.pack(fill="x", pady=20)
    close_but = tb.Button(row9, text="Cancel", command=lambda: navigate_to(entry_system_screen), bootstyle="danger")
    close_but.pack(side=LEFT, padx=10, expand=True)
    test_but = tb.Button(row9, text="Confirm", command=birth_confirm, bootstyle="primary")
    test_but.pack(side=LEFT, padx=10, expand=True)

def death_cert_screen():
    container = tb.Frame(content_frame, padding=30)
    container.pack(expand=True)

    row1 = tb.Frame(container)
    row1.pack(fill="x", pady=5)
    global death_regEntry
    death_reg = tb.Label(row1, text="Registry Number: ", width=LABEL_WIDTH, anchor="w")
    death_regEntry = tb.Entry(row1, width=ENTRY_WIDTH)
    death_reg.pack(side=LEFT)
    death_regEntry.pack(side=LEFT, fill="x", expand=True)
   
    row2 = tb.Frame(container)
    row2.pack(fill="x", pady=5)
    global death_errorType
    death_Title = tb.Label(row2, text="Select an Error: ", width=LABEL_WIDTH, anchor="w")
    bErrors = ["Name", "Date of death", "Sex", "Age at Time of death", "Place of death", "Registration of death (Date)", "Certification of death (Date)"]
    death_errorType = tb.Combobox(row2, values=bErrors, width=ENTRY_WIDTH-3, state='readonly')
    death_errorType.set(" ")
    death_Title.pack(side=LEFT) 
    death_errorType.pack(side=LEFT, fill="x", expand=True)
    
    row3 = tb.Frame(container)
    row3.pack(fill="x", pady=5)
    global origEntry
    origTitle = tb.Label(row3, text="Erroneous Value: ", width=LABEL_WIDTH, anchor="w")
    origEntry = tb.Entry(row3, width=ENTRY_WIDTH)
    origTitle.pack(side=LEFT)
    origEntry.pack(side=LEFT, fill="x", expand=True)
    
    row4 = tb.Frame(container)
    row4.pack(fill="x", pady=5)
    global newEntry
    newTitle = tb.Label(row4, text="New Value: ", width=LABEL_WIDTH, anchor="w")
    newEntry = tb.Entry(row4, width=ENTRY_WIDTH)
    newTitle.pack(side=LEFT)
    newEntry.pack(side=LEFT, fill="x", expand=True)

    row5 = tb.Frame(container)
    row5.pack(fill="x", pady=5)
    global explain
    exp_title = tb.Label(row5, text="Explanation for the Change: ", width=LABEL_WIDTH, anchor="w")
    explain = tb.Entry(row5, width=ENTRY_WIDTH)
    exp_title.pack(side=LEFT)
    explain.pack(side=LEFT, fill="x", expand=True)

    row6 = tb.Frame(container)
    row6.pack(fill="x", pady=20)
    close_but = tb.Button(row6, text="Cancel", command=lambda: navigate_to(entry_system_screen), bootstyle="danger")
    close_but.pack(side=LEFT, padx=10, expand=True)
    test_but = tb.Button(row6, text="Confirm", command=death_confirm, bootstyle="primary")
    test_but.pack(side=LEFT, padx=10, expand=True)

def marriage_cert_screen():
    container = tb.Frame(content_frame, padding=30)
    container.pack(expand=True)

    row1 = tb.Frame(container)
    row1.pack(fill="x", pady=5)
    global marriage_regEntry
    marriage_reg = tb.Label(row1, text="Registry Number: ", width=LABEL_WIDTH, anchor="w")
    marriage_regEntry = tb.Entry(row1, width=ENTRY_WIDTH)
    marriage_reg.pack(side=LEFT)
    marriage_regEntry.pack(side=LEFT, fill="x", expand=True)
   
    row2 = tb.Frame(container)
    row2.pack(fill="x", pady=5)
    global marriage_errorType
    marriage_Title = tb.Label(row2, text="Select an Error: ", width=LABEL_WIDTH, anchor="w")
    bErrors = ["Name of Husband", "Name of Spouse", "Date of Marriage", "Sex", "Age at Time of Marriage", "Place of Marriage", "Registration of Marriage (Date)", "Certification of Marriage (Date)"]
    marriage_errorType = tb.Combobox(row2, values=bErrors, width=ENTRY_WIDTH-3, state='readonly')
    marriage_errorType.set(" ")
    marriage_Title.pack(side=LEFT) 
    marriage_errorType.pack(side=LEFT, fill="x", expand=True)
    
    row3 = tb.Frame(container)
    row3.pack(fill="x", pady=5)
    global applicantName
    applicantTitle = tb.Label(row3, text="Applicant Name: ", width=LABEL_WIDTH, anchor="w")
    applicantEntry = tb.Entry(row3, width=ENTRY_WIDTH)
    applicantTitle.pack(side=LEFT)
    applicantEntry.pack(side=LEFT, fill="x", expand=True)

    row4 = tb.Frame(container)
    row4.pack(fill="x", pady=5)
    global morigEntry
    origTitle = tb.Label(row4, text="Erroneous Value: ", width=LABEL_WIDTH, anchor="w")
    morigEntry = tb.Entry(row4, width=ENTRY_WIDTH)
    origTitle.pack(side=LEFT)
    morigEntry.pack(side=LEFT, fill="x", expand=True)

    row5 = tb.Frame(container)
    row5.pack(fill="x", pady=5)
    global mnewEntry
    newTitle = tb.Label(row5, text="New Value: ", width=LABEL_WIDTH, anchor="w")
    mnewEntry = tb.Entry(row5, width=ENTRY_WIDTH)
    newTitle.pack(side=LEFT)
    mnewEntry.pack(side=LEFT, fill="x", expand=True)

    row6 = tb.Frame(container)
    row6.pack(fill="x", pady=5)
    global mexplainEntry
    mexplainTitle = tb.Label(row6, text="Explanation for the Change: ", width=LABEL_WIDTH, anchor="w")
    mexplainEntry = tb.Entry(row6, width=ENTRY_WIDTH)
    mexplainTitle.pack(side=LEFT)
    mexplainEntry.pack(side=LEFT, fill="x", expand=True)

    row7 = tb.Frame(container)
    row7.pack(fill="x", pady=20)
    close_but = tb.Button(row7, text="Cancel", command=lambda: navigate_to(entry_system_screen), bootstyle="danger")
    close_but.pack(side=LEFT, padx=10, expand=True)
    test_but = tb.Button(row7, text="Confirm", command=marriage_confirm, bootstyle="primary")
    test_but.pack(side=LEFT, padx=10, expand=True)

def dispatch_choice():   
    if cert_choice == "Death Certificate":
        navigate_to(death_cert_screen)
    elif cert_choice == "Birth Certificate":
        navigate_to(birth_cert_screen)
    elif cert_choice == "Marriage Certificate":
        navigate_to(marriage_cert_screen)
    elif cert_choice == "":
        messagebox.showwarning("Warning", "Please select a Certificate Type first.")

def accessibility_screen():
    container = tb.Frame(content_frame, padding=30)
    container.pack(expand=True)

    theme_label = tb.Label(container, text="UI Themes", font=("Helvetica", 14, "bold"))
    theme_label.pack(anchor="w", pady=(0, 10))
    
    row1 = tb.Frame(container)
    row1.pack(fill="x", pady=(0, 20))

    light_but = tb.Button(row1, text="Light Mode", command=lightmode, bootstyle="light")
    light_but.pack(side=LEFT, padx=10)

    dark_but = tb.Button(row1, text="Dark Mode", command=darkmode, bootstyle="dark")
    dark_but.pack(side=LEFT, padx=10)

    grey_but = tb.Button(row1, text="Grey Mode", command=greymode, bootstyle="secondary")
    grey_but.pack(side=LEFT, padx=10)

    font_label = tb.Label(container, text="Text Sizing Options", font=("Helvetica", 14, "bold"))
    font_label.pack(anchor="w", pady=(10, 10))

    row2 = tb.Frame(container)
    row2.pack(fill="x", pady=(0, 20))

    inc_font_but = tb.Button(row2, text="Increase Font Size (+)", command=increase_font, bootstyle="info")
    inc_font_but.pack(side=LEFT, padx=10)

    dec_font_but = tb.Button(row2, text="Decrease Font Size (-)", command=decrease_font, bootstyle="info-outline")
    dec_font_but.pack(side=LEFT, padx=10)

    reset_label = tb.Label(container, text="System Actions", font=("Helvetica", 14, "bold"))
    reset_label.pack(anchor="w", pady=(10, 10))

    row3 = tb.Frame(container)
    row3.pack(fill="x", pady=(0, 20))

    reset_but = tb.Button(row3, text="Reset Settings", command=reset_settings, bootstyle="warning")
    reset_but.pack(side=LEFT, padx=10)

    row4 = tb.Frame(container)
    row4.pack(fill="x", pady=(20, 0))
    close_but = tb.Button(row4, text="Back to Main Menu", command=lambda: navigate_to(main_menu_screen), bootstyle="danger")
    close_but.pack(side=LEFT, padx=10)

def entry_system_screen():
    container = tb.Frame(content_frame, padding=30)
    container.pack(expand=True)

    row1 = tb.Frame(container)
    row1.pack(fill="x", pady=5)
    certificates = ["Birth Certificate", "Death Certificate", "Marriage Certificate"]
    certTitle = tb.Label(row1, text="Certificate Type: ", width=LABEL_WIDTH, anchor="w")
    
    global certType
    certType = tb.Combobox(row1, values=certificates, width=ENTRY_WIDTH-3, state='readonly')
    certType.bind("<<ComboboxSelected>>", update_entry)  
    certType.set(cert_choice if cert_choice else "")

    certTitle.pack(side=LEFT)
    certType.pack(side=LEFT, fill="x", expand=True)

    row2 = tb.Frame(container)
    row2.pack(fill="x", pady=20)

    close_but = tb.Button(row2, text="Back to Main Menu", command=lambda: navigate_to(main_menu_screen), bootstyle="danger")
    close_but.pack(side=LEFT, padx=10, expand=True)

    test_but = tb.Button(row2, text="Next", command=dispatch_choice, bootstyle="primary")
    test_but.pack(side=LEFT, padx=10, expand=True)

def main_menu_screen():
    main_container = tb.Frame(content_frame, padding=20)
    main_container.pack(expand=True)

    row1 = tb.Frame(main_container)
    row1.pack(fill="x", pady=10)
    main_button = tb.Button(row1, text="Create New Entry", command=lambda: navigate_to(entry_system_screen), bootstyle="primary")
    main_button.pack(ipadx=10, ipady=5)

    row2 = tb.Frame(main_container)
    row2.pack(fill="x", pady=10)
    accessibility_but = tb.Button(row2, text="Accessibility Settings", command=lambda: navigate_to(accessibility_screen), bootstyle="outline-secondary")
    accessibility_but.pack(ipadx=10, ipady=5)

    row3 = tb.Frame(main_container)
    row3.pack(fill="x", pady=10)
    results_but = tb.Button(row3, text="View Results Panel", command=lambda: navigate_to(results_panel_screen), bootstyle="info")
    results_but.pack(ipadx=10, ipady=5)

# Initialize application layout with the main landing menu
main_menu_screen()
apply_font_sizes()

root.mainloop()