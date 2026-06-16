
# Chatline:
"""  - gumamit ako ng tree.insert (which is mandatory) to insert records to the treetable
     - inserted a dummy record here 
     - NEEDED TO DO: 
          - is to beautify our UI design
          - integrate our db to this UI

     - and according to my research, to make this connect to db, we use:
     - import mysql.connector
     - alternative method: gagamitin ang auditlog(discrepancy_entry) table csv
     - gagamit ng file handling keme nyan. 
"""


# -------------------------------------------------------------------------------
# ABOUT PSA AUDIT LOG UI 
"""  has window tk, then mainframe;
     has 4 frame parts:
     1. Header Frame
          - title label
          - description label
     2. Filter Frame
          - Report ID Search Bar 
          - Employee ID Search Bar
          - Error field Search bar
          - Date Picker
     3. Table Frame
          Header
          - discrepancy_entry ID
          - Report ID
          - explanation
          - Field Changed
          - Original Value
          - Revised value
          - Employee 
          - Date Modified
          Data
          - discrepancy_entry records
          - in treeview
          - scrollbar
"""


# -------------------------------------------------------------------------------
# DEFINED PREREQUISITES 
from tkinter import *
from tkinter import ttk

titlefont = ("Arial", 18, 'bold')
ourfont = ("Arial", 12)

# padx & pady - spaces between widgets (x-axis or y-axis)


# -------------------------------------------------------------------------------
# ROOT FRAME - APPLICATION WINDOW
root = Tk()

# getting screen width and height of display
width = root.winfo_screenwidth()
height = root.winfo_screenheight()

# setting tkinter window size
root.geometry("%dx%d" % (width, height))
root.title("PSA Error Collection")


# -------------------------------------------------------------------------------
# MAIN FRAME - CONTAINER FOR ALL OTHER FRAMES
mainframe = Frame(root)
mainframe.pack(fill="both",expand=True)


# -------------------------------------------------------------------------------
# HEADER FRAME 
headerframe = Frame(mainframe)
headerframe.pack(fill="x",padx=20,pady=10)

lbl_title = Label(
     headerframe, text= "Audit Logs", font= titlefont).pack(anchor="w")
lbl_desc = Label(
     headerframe, text='Modifications made by employees', font=ourfont).pack(anchor="w")


# -------------------------------------------------------------------------------
# FILTER FRAME 
filterframe = Frame(mainframe)
filterframe.pack(fill="x",padx=20,pady=10)

# report id search
lbl_report = Label(filterframe, text= "Report ID", font= ourfont).grid(row=0, column=0)
ntry_report_search = Entry(filterframe, width= 30).grid(row=1, column=0, padx=5)
btn_report = Button(filterframe, text="Search").grid(row=1, column=1, padx=5)

# employee id search
lbl_employee = Label(filterframe, text= "Employee ID", font= ourfont).grid(row=0, column=2)
ntry_employee_search = Entry(filterframe, width= 30).grid(row=1, column=2, padx=5)
btn_employee = Button(filterframe, text="Search").grid(row=1, column=3, padx=5)

# error field search
lbl_error = Label(filterframe, text= "Error Field", font= ourfont).grid(row=0, column=4)
ntry_error_search = Entry(filterframe, width= 30).grid(row=1, column=4, padx=5)
btn_error = Button(filterframe, text="Search").grid(row=1, column=5, padx=5)

# date search (modifications on that date)
lbl_date = Label(filterframe, text= "Date Modified", font= ourfont).grid(row=0, column=6)
ntry_date_search = Entry(filterframe, width= 30).grid(row=1, column=6, padx=5)
btn_date = Button(filterframe, text="Search").grid(row=1, column=7, padx=5)


# -------------------------------------------------------------------------------
# TABLE FRAME 
tableheadframe = Frame(mainframe) # width=900, height=600)
tableheadframe.pack(fill="x",padx=20,pady=10)
# tableheadframe.pack_propagate(0) # prevents frame from resizing to fit content

# treeview for table
tree = ttk.Treeview(tableheadframe, 
                    columns= ("discrepancy_entry_id", "report_id", "explanation", 
                              "error_field", "original_value", "revised_value", 
                              "modified_by", "modified_date"), 
                    show="headings",
                    height=27)

# define columns names
tree.heading("discrepancy_entry_id", text="Discrepancy Entry ID")
tree.heading("report_id", text="Report ID")
tree.heading("explanation", text="Explanation")
tree.heading("error_field", text="Field Changed")
tree.heading("original_value", text="Original Value")
tree.heading("revised_value", text="Revised Value")
tree.heading("modified_by", text="Employee")
tree.heading("modified_date", text="Date")

# formatting colmuns
tree.column("discrepancy_entry_id", width=150, stretch=True)
tree.column("report_id", width=150, stretch=True)
tree.column("explanation", width=150, stretch=True)
tree.column("error_field", width=150, stretch=True)
tree.column("original_value", width=150, stretch=True)
tree.column("revised_value", width=150, stretch=True)
tree.column("modified_by", width=150, stretch=True)
tree.column("modified_date", width=150, stretch=True)

# scrollbar for treeview
scrollbar = Scrollbar(tableheadframe, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)

# grid layout - treeview on left, scrollbar on right
tree.grid(row=0, column=0, sticky="nsew")
scrollbar.grid(row=0, column=1, sticky="ns")

# allow treeview to expand
tableheadframe.grid_columnconfigure(0, weight=1)
tableheadframe.grid_rowconfigure(0, weight=1)

# try inserting dummy record
tree.insert("", "end", 
            values=("E-0199", "BC-26-04-12344", "wrong birth order", "birth_order",
                     4, 2,"EMP-002","6/13/2026")       
)

mainframe.mainloop()