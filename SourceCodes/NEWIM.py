import re
import ttkbootstrap as tb  # Replaces standard tkinter and ttk
from ttkbootstrap.constants import *
from tkinter import messagebox

# Using ttkbootstrap's Window instead of standard Tk()
frame = tb.Window(themename="flatly")

# Setting up main window dimensions
width = frame.winfo_screenwidth() 
height = frame.winfo_screenheight()
frame.geometry("%dx%d" % (width, height))
frame.title("PSA Error Correction System")
frame.state('zoomed') 

# Baseline initial values for resetting
DEFAULT_TITLE_SIZE = 25
DEFAULT_BODY_SIZE = 11

# Global font scale variable tracking state
font_size_title = DEFAULT_TITLE_SIZE
font_size_default = DEFAULT_BODY_SIZE

def apply_font_sizes():
    """Dynamically applies global font sizes across bootstrap widget classes."""
    # Configure the main header title font specifically
    Title.config(font=("Helvetica", font_size_title))
    
    # Configure master styles for the entire application environment
    style = tb.Style()
    style.configure('.', font=("Helvetica", font_size_default))          # Base style for everything
    style.configure('TLabel', font=("Helvetica", font_size_default))     # Labels
    style.configure('TButton', font=("Helvetica", font_size_default))    # Buttons
    style.configure('TEntry', font=("Helvetica", font_size_default))     # Input fields
    style.configure('TCombobox', font=("Helvetica", font_size_default))  # Dropdowns

def increase_font():
    global font_size_title, font_size_default
    if font_size_default < 24:  # Set an upper safety limit
        font_size_title += 2
        font_size_default += 2
        apply_font_sizes()
    else:
        messagebox.showinfo("Font Limit", "Maximum font size reached.")

def decrease_font():
    global font_size_title, font_size_default
    if font_size_default > 8:  # Set a lower safety limit
        font_size_title -= 2
        font_size_default -= 2
        apply_font_sizes()
    else:
        messagebox.showinfo("Font Limit", "Minimum font size reached.")

def reset_settings():
    """Resets the themes and font settings completely back to their factory layout configurations."""
    global font_size_title, font_size_default
    font_size_title = DEFAULT_TITLE_SIZE
    font_size_default = DEFAULT_BODY_SIZE
    
    # Restore Default Flatly Bootstrap Theme
    frame.style.theme_use("flatly")
    
    # Restore default fonts
    apply_font_sizes()
    messagebox.showinfo("Reset Successful", "Accessibility changes have been restored to default values.")

# Main System Title
Title = tb.Label(frame, text="PSA Error Correction System", font=("Helvetica", font_size_title), bootstyle="inverse-primary")
Title.pack(pady=20, fill="x")

# Initialize global variables to prevent NameErrors if users click buttons early
cert_choice = ""
death_Error = ""

# Track all active windows globally
open_windows = {}

def update_entry(event):
    global cert_choice, death_Error
    cert_choice = certType.get()
    if 'death_errorType' in globals():
        death_Error = death_errorType.get()

# Helper constants for structural alignment
LABEL_WIDTH = 25  
ENTRY_WIDTH = 40  

# Dynamic Theme Switching using Bootstrap Built-in Styles
def darkmode():
    frame.style.theme_use("darkly")
    apply_font_sizes() # Re-apply fonts when theme structure resets

def lightmode():
    frame.style.theme_use("flatly")
    apply_font_sizes()

def greymode():
    frame.style.theme_use("superhero")
    apply_font_sizes()

def death_confirm(window_ref):
    reg_pattern = r"^\d{4}-\d{7}$"
    if death_regEntry.get() == "":
        messagebox.showerror("Error", "Please input the proper Registration Number (ex. YYYY-XXXXXXX).", parent=window_ref)
        return
    elif not re.match(reg_pattern, death_regEntry.get()):
        messagebox.showerror("Error", "Invalid format! Registration Number must follow YYYY-XXXXXXX (e.g., 2026-1234567).", parent=window_ref)
        return
    elif death_errorType.get() == " ":
        messagebox.showerror("Error", "Please specify an error type.", parent=window_ref)
        return
    elif origEntry.get() == "":
        messagebox.showerror("Error", "Please specify the erroneous value.", parent=window_ref)
        return
    elif newEntry.get() == "":
        messagebox.showerror("Error", "Please specify the new value.", parent=window_ref)
        return
    elif explain.get() == "":
        messagebox.showerror("Error", "Please indicate the reason for this change", parent=window_ref)
        return
    else:
        final = messagebox.askyesno("Confirmation", "Are you sure with the information inputted?", parent=window_ref)
        
    if final:
        confirmation_window = tb.Toplevel(frame)
        open_windows['death_confirm'] = confirmation_window
        confirmation_window.geometry("%dx%d" % (width, height))
        confirmation_window.title("Death Certificate Corrections Confirmation")
        confirmation_window.state('zoomed')
       
        container = tb.Frame(confirmation_window, padding=30)
        container.pack(expand=True)

        for label_text, entry_val in [
            ("Registry Number: ", death_regEntry.get()),
            ("Certificate Type: ", certType.get()),
            ("Original Value: ", origEntry.get()),
            ("New Value: ", newEntry.get()),
            ("Explanation for the change: ", explain.get())
        ]:
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
        close_but = tb.Button(btn_row, text="Close", command=confirmation_window.destroy, bootstyle="danger")
        close_but.pack(side=LEFT, padx=10, expand=True)
        new_button = tb.Button(btn_row, text="New Entry", command=entry_system, bootstyle="success")
        new_button.pack(side=LEFT, padx=10, expand=True)
        window_ref.destroy()
        main_window.destroy()
    else:
        messagebox.showinfo("Cancelled Input", "Your Entry has been Cancelled.", parent=window_ref)

def birth_confirm(window_ref):
    reg_pattern = r"^\d{4}-\d{7}$"
    if birth_regEntry.get() == "":
        messagebox.showerror("Error", "Please input the proper Registration Number (ex. YYYY-XXXXXXX).", parent=window_ref)
        return
    elif not re.match(reg_pattern, birth_regEntry.get()):
        messagebox.showerror("Error", "Invalid format! Registration Number must follow YYYY-XXXXXXX (e.g., 2026-1234567).", parent=window_ref)
        return
    elif birth_errorType.get() == " ":
        messagebox.showerror("Error", "Please specify an error type.", parent=window_ref)
        return
    elif youEntry.get() == "":
        messagebox.showerror("Error", "Please Specify the Document owner's Name", parent=window_ref)
        return
    elif momEntry.get() == "":
        messagebox.showerror("Error", "Please Specify the Mother's Name", parent=window_ref)
        return
    elif dadEntry.get() == "":
        messagebox.showerror("Error", "Please Specify the Father's Name", parent=window_ref)
        return
    elif borigEntry.get() == "":
        messagebox.showerror("Error", "Please specify the erroneous value.", parent=window_ref)
        return
    elif bnewEntry.get() == "":
        messagebox.showerror("Error", "Please specify the new value.", parent=window_ref)
        return
    elif bexplain.get() == "":
        messagebox.showerror("Error", "Please indicate the reason for this change", parent=window_ref)
        return
    else:
        final = messagebox.askyesno("Confirmation", "Are you sure with the information inputted?", parent=window_ref)
        
    if final:
        bconfirmation_window = tb.Toplevel(frame)
        open_windows['birth_confirm'] = bconfirmation_window
        bconfirmation_window.geometry("%dx%d" % (width, height))
        bconfirmation_window.title("Birth Certificate Corrections Confirmation")
        bconfirmation_window.state('zoomed')
       
        container = tb.Frame(bconfirmation_window, padding=30)
        container.pack(expand=True)

        for label_text, entry_val in [
            ("Registry Number: ", birth_regEntry.get()),
            ("Certificate Type: ", certType.get()),
            ("Owner Name: ", youEntry.get()),
            ("Mother's Maiden Name: ", momEntry.get()),
            ("Father's Name: ", dadEntry.get()),
            ("Original Value: ", borigEntry.get()),
            ("New Value: ", bnewEntry.get()),
            ("Explanation for the change: ", bexplain.get())
        ]:
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
        close_but = tb.Button(btn_row, text="Close", command=bconfirmation_window.destroy, bootstyle="danger")
        close_but.pack(side=LEFT, padx=10, expand=True)
        new_button = tb.Button(btn_row, text="New Entry", command=entry_system, bootstyle="success")
        new_button.pack(side=LEFT, padx=10, expand=True)
        window_ref.destroy()
        main_window.destroy()
    else:
        messagebox.showinfo("Cancelled Input", "Your Entry has been Cancelled.", parent=window_ref)

def marriage_confirm(window_ref):
    reg_pattern = r"^\d{4}-\d{7}$"
    if marriage_regEntry.get() == "":
        messagebox.showerror("Error", "Please input the proper Registration Number (ex. YYYY-XXXXXXX).", parent=window_ref)
        return
    elif not re.match(reg_pattern, marriage_regEntry.get()):
        messagebox.showerror("Error", "Invalid format! Registration Number must follow YYYY-XXXXXXX (e.g., 2026-1234567).", parent=window_ref)
        return
    elif marriage_errorType.get().strip() == "":
        messagebox.showerror("Error", "Please specify an error type.", parent=window_ref)
        return
    elif morigEntry.get() == "":
        messagebox.showerror("Error", "Please specify the erroneous value.", parent=window_ref)
        return
    elif mnewEntry.get() == "":
        messagebox.showerror("Error", "Please specify the new value.", parent=window_ref)
        return
    elif mexplainEntry.get() == "": 
        messagebox.showerror("Error", "Please indicate the reason for this change", parent=window_ref)
        return
    else:
        final = messagebox.askyesno("Confirmation", "Are you sure with the information inputted?", parent=window_ref)
        
        if final:
            mconfirmation_window = tb.Toplevel(frame)
            open_windows['marriage_confirm'] = mconfirmation_window
            mconfirmation_window.geometry("%dx%d" % (width, height))
            mconfirmation_window.title("Marriage Certificate Corrections Confirmation")
            mconfirmation_window.state('zoomed')
            
            container = tb.Frame(mconfirmation_window, padding=30)
            container.pack(expand=True)

            for label_text, entry_val in [
                ("Registry Number: ", marriage_regEntry.get()),
                ("Certificate Type: ", certType.get()),
                ("Original Value: ", morigEntry.get()),
                ("New Value: ", mnewEntry.get()),
                ("Explanation for the change: ", mexplainEntry.get())
            ]:
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
            close_but = tb.Button(btn_row, text="Close", command=mconfirmation_window.destroy, bootstyle="danger")
            close_but.pack(side=LEFT, padx=10, expand=True)
            new_button = tb.Button(btn_row, text="New Entry", command=entry_system, bootstyle="success")
            new_button.pack(side=LEFT, padx=10, expand=True)
            window_ref.destroy()
            main_window.destroy()
        else:
            messagebox.showinfo("Cancelled Input", "Your Entry has been Cancelled.", parent=window_ref)

def birth_cert():
    birth_window = tb.Toplevel(frame)
    open_windows['birth'] = birth_window
    birth_window.geometry("%dx%d" % (width, height))
    birth_window.title("Birth Certificate Corrections")
    birth_window.state('zoomed') 
    
    container = tb.Frame(birth_window, padding=30)
    container.pack(expand=True)

    # Row 1
    row1 = tb.Frame(container)
    row1.pack(fill="x", pady=5)
    global birth_regEntry
    birth_reg = tb.Label(row1, text="Registry Number: ", width=LABEL_WIDTH, anchor="w")
    birth_regEntry = tb.Entry(row1, width=ENTRY_WIDTH)
    birth_reg.pack(side=LEFT)
    birth_regEntry.pack(side=LEFT, fill="x", expand=True)

    # Row 2
    row2 = tb.Frame(container)
    row2.pack(fill="x", pady=5)
    global youEntry
    youTitle = tb.Label(row2, text="Name: ", width=LABEL_WIDTH, anchor="w")
    youEntry = tb.Entry(row2, width=ENTRY_WIDTH)
    youTitle.pack(side=LEFT)
    youEntry.pack(side=LEFT, fill="x", expand=True)

    # Row 3
    row3 = tb.Frame(container)
    row3.pack(fill="x", pady=5)
    global momEntry
    momTitle = tb.Label(row3, text="Mother's Maiden Name: ", width=LABEL_WIDTH, anchor="w")
    momEntry = tb.Entry(row3, width=ENTRY_WIDTH)
    momTitle.pack(side=LEFT)
    momEntry.pack(side=LEFT, fill="x", expand=True)

    # Row 4
    row4 = tb.Frame(container)
    row4.pack(fill="x", pady=5)
    global dadEntry
    dadTitle = tb.Label(row4, text="Father's Name: ", width=LABEL_WIDTH, anchor="w")
    dadEntry = tb.Entry(row4, width=ENTRY_WIDTH)
    dadTitle.pack(side=LEFT)
    dadEntry.pack(side=LEFT, fill="x", expand=True)
   
    # Row 5
    row5 = tb.Frame(container)
    row5.pack(fill="x", pady=5)
    global birth_errorType
    birth_Title = tb.Label(row5, text="Select an Error: ", width=LABEL_WIDTH, anchor="w")
    bErrors = ["Date of Birth", "Sex", "Place of Birth", "Father Details", "Mother Details", "Birth Order", "Type of Birth"]
    birth_errorType = tb.Combobox(row5, values=bErrors, width=ENTRY_WIDTH-3, state='readonly')
    birth_errorType.set(" ")
    birth_errorType.bind("<<ComboboxSelected>>", update_entry) 
    birth_Title.pack(side=LEFT) 
    birth_errorType.pack(side=LEFT, fill="x", expand=True)
    
    # Row 6
    row6 = tb.Frame(container)
    row6.pack(fill="x", pady=5)
    global borigEntry
    borigTitle = tb.Label(row6, text="Erroneous Value: ", width=LABEL_WIDTH, anchor="w")
    borigEntry = tb.Entry(row6, width=ENTRY_WIDTH)
    borigTitle.pack(side=LEFT)
    borigEntry.pack(side=LEFT, fill="x", expand=True)
    
    # Row 7
    row7 = tb.Frame(container)
    row7.pack(fill="x", pady=5)
    global bnewEntry
    bnewTitle = tb.Label(row7, text="New Value: ", width=LABEL_WIDTH, anchor="w")
    bnewEntry = tb.Entry(row7, width=ENTRY_WIDTH)
    bnewTitle.pack(side=LEFT)
    bnewEntry.pack(side=LEFT, fill="x", expand=True)

    # Row 8
    row8 = tb.Frame(container)
    row8.pack(fill="x", pady=5)
    global bexplain
    bexplainTitle = tb.Label(row8, text="Explanation for the Change: ", width=LABEL_WIDTH, anchor="w")
    bexplain = tb.Entry(row8, width=ENTRY_WIDTH)
    bexplainTitle.pack(side=LEFT)
    bexplain.pack(side=LEFT, fill="x", expand=True)

    # Actions Button Row
    row9 = tb.Frame(container)
    row9.pack(fill="x", pady=20)
    close_but = tb.Button(row9, text="Close", command=birth_window.destroy, bootstyle="danger")
    close_but.pack(side=LEFT, padx=10, expand=True)
    test_but = tb.Button(row9, text="Confirm", command=lambda: birth_confirm(birth_window), bootstyle="primary")
    test_but.pack(side=LEFT, padx=10, expand=True)

def death_cert():
    death_window = tb.Toplevel(frame)
    open_windows['death'] = death_window
    death_window.geometry("%dx%d" % (width, height))
    death_window.title("Death Certificate Corrections")
    death_window.state('zoomed') 
    
    container = tb.Frame(death_window, padding=30)
    container.pack(expand=True)

    # Row 1
    row1 = tb.Frame(container)
    row1.pack(fill="x", pady=5)
    global death_regEntry
    death_reg = tb.Label(row1, text="Registry Number: ", width=LABEL_WIDTH, anchor="w")
    death_regEntry = tb.Entry(row1, width=ENTRY_WIDTH)
    death_reg.pack(side=LEFT)
    death_regEntry.pack(side=LEFT, fill="x", expand=True)
   
    # Row 2
    row2 = tb.Frame(container)
    row2.pack(fill="x", pady=5)
    global death_errorType
    death_Title = tb.Label(row2, text="Select an Error: ", width=LABEL_WIDTH, anchor="w")
    bErrors = ["Name", "Date of death", "Sex", "Age at Time of death", "Place of death", "Registration of death (Date)", "Certification of death (Date)"]
    death_errorType = tb.Combobox(row2, values=bErrors, width=ENTRY_WIDTH-3, state='readonly')
    death_errorType.set(" ")
    death_errorType.bind("<<ComboboxSelected>>", update_entry) 
    death_Title.pack(side=LEFT) 
    death_errorType.pack(side=LEFT, fill="x", expand=True)
    
    # Row 3
    row3 = tb.Frame(container)
    row3.pack(fill="x", pady=5)
    global origEntry
    origTitle = tb.Label(row3, text="Erroneous Value: ", width=LABEL_WIDTH, anchor="w")
    origEntry = tb.Entry(row3, width=ENTRY_WIDTH)
    origTitle.pack(side=LEFT)
    origEntry.pack(side=LEFT, fill="x", expand=True)
    
    # Row 4
    row4 = tb.Frame(container)
    row4.pack(fill="x", pady=5)
    global newEntry
    newTitle = tb.Label(row4, text="New Value: ", width=LABEL_WIDTH, anchor="w")
    newEntry = tb.Entry(row4, width=ENTRY_WIDTH)
    newTitle.pack(side=LEFT)
    newEntry.pack(side=LEFT, fill="x", expand=True)

    # ROW 5
    row5 = tb.Frame(container)
    row5.pack(fill="x", pady=5)
    global explain
    exp_title = tb.Label(row5, text="Explanation for the Change: ", width=LABEL_WIDTH, anchor="w")
    explain = tb.Entry(row5, width=ENTRY_WIDTH)
    exp_title.pack(side=LEFT)
    explain.pack(side=LEFT, fill="x", expand=True)

    # ROW 6 Buttons
    row6 = tb.Frame(container)
    row6.pack(fill="x", pady=20)
    close_but = tb.Button(row6, text="Close", command=death_window.destroy, bootstyle="danger")
    close_but.pack(side=LEFT, padx=10, expand=True)
    test_but = tb.Button(row6, text="Confirm", command=lambda: death_confirm(death_window), bootstyle="primary")
    test_but.pack(side=LEFT, padx=10, expand=True)

def marriage_cert():
    marriage_window = tb.Toplevel(frame)
    open_windows['marriage'] = marriage_window
    marriage_window.geometry("%dx%d" % (width, height))
    marriage_window.title("Marriage Certificate Corrections")
    marriage_window.state('zoomed') 
    
    container = tb.Frame(marriage_window, padding=30)
    container.pack(expand=True)

    # Row 1
    row1 = tb.Frame(container)
    row1.pack(fill="x", pady=5)
    global marriage_regEntry
    marriage_reg = tb.Label(row1, text="Registry Number: ", width=LABEL_WIDTH, anchor="w")
    marriage_regEntry = tb.Entry(row1, width=ENTRY_WIDTH)
    marriage_reg.pack(side=LEFT)
    marriage_regEntry.pack(side=LEFT, fill="x", expand=True)
   
    # Row 2
    row2 = tb.Frame(container)
    row2.pack(fill="x", pady=5)
    global marriage_errorType
    marriage_Title = tb.Label(row2, text="Select an Error: ", width=LABEL_WIDTH, anchor="w")
    bErrors = ["Name of Husband", "Name of Spouse", "Date of Marriage", "Sex", "Age at Time of Marriage", "Place of Marriage", "Registration of Marriage (Date)", "Certification of Marriage (Date)"]
    marriage_errorType = tb.Combobox(row2, values=bErrors, width=ENTRY_WIDTH-3, state='readonly')
    marriage_errorType.set(" ")
    marriage_errorType.bind("<<ComboboxSelected>>", update_entry) 
    marriage_Title.pack(side=LEFT) 
    marriage_errorType.pack(side=LEFT, fill="x", expand=True)
    
    # Row 3
    row3 = tb.Frame(container)
    row3.pack(fill="x", pady=5)
    global applicantName
    applicantTitle = tb.Label(row3, text="Applicant Name: ", width=LABEL_WIDTH, anchor="w")
    applicantEntry = tb.Entry(row3, width=ENTRY_WIDTH)
    applicantTitle.pack(side=LEFT)
    applicantEntry.pack(side=LEFT, fill="x", expand=True)

    # Row 4
    row4 = tb.Frame(container)
    row4.pack(fill="x", pady=5)
    global morigEntry
    origTitle = tb.Label(row4, text="Erroneous Value: ", width=LABEL_WIDTH, anchor="w")
    morigEntry = tb.Entry(row4, width=ENTRY_WIDTH)
    origTitle.pack(side=LEFT)
    morigEntry.pack(side=LEFT, fill="x", expand=True)

    # Row 5
    row5 = tb.Frame(container)
    row5.pack(fill="x", pady=5)
    global mnewEntry
    newTitle = tb.Label(row5, text="New Value: ", width=LABEL_WIDTH, anchor="w")
    mnewEntry = tb.Entry(row5, width=ENTRY_WIDTH)
    newTitle.pack(side=LEFT)
    mnewEntry.pack(side=LEFT, fill="x", expand=True)

    # Row 6
    row6 = tb.Frame(container)
    row6.pack(fill="x", pady=5)
    global mexplainEntry
    mexplainTitle = tb.Label(row6, text="Explanation for the Change: ", width=LABEL_WIDTH, anchor="w")
    mexplainEntry = tb.Entry(row6, width=ENTRY_WIDTH)
    mexplainTitle.pack(side=LEFT)
    mexplainEntry.pack(side=LEFT, fill="x", expand=True)

    # Row 7 Buttons
    row7 = tb.Frame(container)
    row7.pack(fill="x", pady=20)
    close_but = tb.Button(row7, text="Close", command=marriage_window.destroy, bootstyle="danger")
    close_but.pack(side=LEFT, padx=10, expand=True)
    test_but = tb.Button(row7, text="Confirm", command=lambda: marriage_confirm(marriage_window), bootstyle="primary")
    test_but.pack(side=LEFT, padx=10, expand=True)

def choice():   
    if cert_choice == "Death Certificate":
        death_cert()
    elif cert_choice == "Birth Certificate":
        birth_cert()
    elif cert_choice == "Marriage Certificate":
        marriage_cert()
    elif cert_choice == "":
        messagebox.showwarning("Warning", "Please select a Certificate Type first.", parent=frame)

def accessibility():
    accessibility_window = tb.Toplevel(frame)
    open_windows['accessibility'] = accessibility_window
    accessibility_window.geometry("%dx%d" % (width, height))
    accessibility_window.title("Accessibility Setup")
    accessibility_window.state('zoomed') 

    container = tb.Frame(accessibility_window, padding=30)
    container.pack(expand=True)

    # --- Section 1: Themes ---
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

    # --- Section 2: Text Sizing Controls ---
    font_label = tb.Label(container, text="Text Sizing Options", font=("Helvetica", 14, "bold"))
    font_label.pack(anchor="w", pady=(10, 10))

    row2 = tb.Frame(container)
    row2.pack(fill="x", pady=(0, 20))

    inc_font_but = tb.Button(row2, text="Increase Font Size (+)", command=increase_font, bootstyle="info")
    inc_font_but.pack(side=LEFT, padx=10)

    dec_font_but = tb.Button(row2, text="Decrease Font Size (-)", command=decrease_font, bootstyle="info-outline")
    dec_font_but.pack(side=LEFT, padx=10)

    # --- Section 3: Settings Reset ---
    reset_label = tb.Label(container, text="System Actions", font=("Helvetica", 14, "bold"))
    reset_label.pack(anchor="w", pady=(10, 10))

    row3 = tb.Frame(container)
    row3.pack(fill="x", pady=(0, 20))

    reset_but = tb.Button(row3, text="Reset Settings", command=reset_settings, bootstyle="warning")
    reset_but.pack(side=LEFT, padx=10)

    # --- Section 4: Navigation ---
    row4 = tb.Frame(container)
    row4.pack(fill="x", pady=(20, 0))
    close_but = tb.Button(row4, text="Close", command=accessibility_window.destroy, bootstyle="danger")
    close_but.pack(side=LEFT, padx=10)

def entry_system():
    global main_window
    main_window = tb.Toplevel(frame)
    open_windows['entry_system'] = main_window
    main_window.geometry("%dx%d" % (width, height))
    main_window.title("Accessibility Setup")
    main_window.state('zoomed') 

    container = tb.Frame(main_window, padding=30)
    container.pack(expand=True)

    # Certificate Selection Widgets
    row1 = tb.Frame(container)
    row1.pack(fill="x", pady=5)
    certificates = ["Birth Certificate", "Death Certificate", "Marriage Certificate"]
    certTitle = tb.Label(row1, text="Certificate Type: ", width=LABEL_WIDTH, anchor="w")
    
    global certType
    certType = tb.Combobox(row1, values=certificates, width=ENTRY_WIDTH-3, state='readonly')
    certType.bind("<<ComboboxSelected>>", update_entry)  

    certTitle.pack(side=LEFT)
    certType.pack(side=LEFT, fill="x", expand=True)

    # Action Button Row
    row2 = tb.Frame(container)
    row2.pack(fill="x", pady=20)

    close_but = tb.Button(row2, text="Close", command=main_window.destroy, bootstyle="danger")
    close_but.pack(side=LEFT, padx=10, expand=True)

    test_but = tb.Button(row2, text="Select", command=choice, bootstyle="primary")
    test_but.pack(side=LEFT, padx=10, expand=True)

# Main screen layout structure center-packed
main_container = tb.Frame(frame, padding=20)
main_container.pack(expand=True)

# Entry Selector row
row1 = tb.Frame(main_container)
row1.pack(fill="x", pady=10)
main_button = tb.Button(row1, text="Create New Entry", command=entry_system, bootstyle="primary")
main_button.pack(ipadx=10, ipady=5)

# Accessibility Selector Row
row2 = tb.Frame(main_container)
row2.pack(fill="x", pady=10)
accessibility_but = tb.Button(row2, text="Accessibility Settings", command=accessibility, bootstyle="outline-secondary")
accessibility_but.pack(ipadx=10, ipady=5)

# Run initial font size injection
apply_font_sizes()

frame.mainloop()