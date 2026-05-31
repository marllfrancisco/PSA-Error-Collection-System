import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import messagebox

frame = tk.Tk()
frame.geometry("450x400")
frame.configure(bg="#E6CBE5")

#checkbutton and radiobutton variable initialization
labFee_var = IntVar()
regisCard_var = IntVar()
catalyst_var = IntVar()
scouncil_var = IntVar()
sID_var = IntVar()
miscellaneous_var = IntVar()
scholarship_var = IntVar()
scholarship_var.set(1)

#computes year level fee
def compute_yrlvl():
  if yrlvl_combo.get() == "1st Year":
    return 100
  elif yrlvl_combo.get() == "2nd Year":
    return 200
  elif yrlvl_combo.get() == "3rd Year":
    return 300
  elif yrlvl_combo.get() == "4th Year":
    return 400
  else:
    return 500

#computes other fees on top of year level fee
def compute_fees():
  total = 0
  if labFee_var.get() == 1:
    total += 200
  if regisCard_var.get() == 1:
    total += 50
  if catalyst_var.get() == 1:
    total += 50
  if scouncil_var.get() == 1:
    total += 50
  if sID_var.get() == 1:
    total += 50
  if miscellaneous_var.get() == 1:
    total += 100
  return total

#computes scholarship grants on top of other fees and year level fee
def compute_scholarship():
  units = int(units_entry.get())
  fees = int(compute_fees())
  if scholarship_var.get() == 1:
    return ((units*10)+fees+compute_yrlvl())
  elif scholarship_var.get() == 2:
    return 0
  elif scholarship_var.get() == 3:
    return (((units*10)+fees+compute_yrlvl())/2)

#returns all total amounts computed with error messages for invalid inputs
def compute_total():
  if sname_entry.get() == "" or units_entry.get() == "" or yrlvl_combo.get() == "":
    messagebox.showerror("Missing Input", "Please fill in all fields.")
    return
  else:
    try:
      units = int(units_entry.get())
      if units <= 0:
        messagebox.showerror("Error", "Units must be a positive number.")
        return
    except ValueError:
      messagebox.showerror("Error", "Units must be a valid number.")
      return

  total_entry.config(state='normal')
  total_entry.delete(0, END)
  total_entry.insert(0, f"PHP{compute_scholarship():,.2f}")
  total_entry.config(state='readonly')

#clears all fields
def Clear():
    sname_entry.delete(0, END)
    units_entry.delete(0, END)
    yrlvl_combo.set("")
    total_entry.config(state='normal')
    total_entry.delete(0, END)
    total_entry.config(state='readonly')
    labFee_var.set(0)
    regisCard_var.set(0)
    catalyst_var.set(0)
    scouncil_var.set(0)
    sID_var.set(0)
    miscellaneous_var.set(0)
    scholarship_var.set(1)

#creation of all widgets
sname_lbl = tk.Label(frame, text="Student Name:", font=('Times New Roman', 10), bg="#E6CBE5")
sname_entry = tk.Entry(frame, font=('Times New Roman', 10), bd=2, width=40)
units_lbl = tk.Label(frame, text="Units Enrolled:", font=('Times New Roman', 10), bg="#E6CBE5")
units_entry = tk.Entry(frame, font=('Times New Roman', 10), bd=2, width=40)
yrlvl_lbl = tk.Label(frame, text="Year Level:", font=('Times New Roman', 10), bg="#E6CBE5")
yrlvl_combo = ttk.Combobox(frame, values=["1st Year", "2nd Year", "3rd Year", "4th Year"], state="readonly")
fees_lbl = tk.Label(frame, text="Other Fees:", font=('Times New Roman', 10), bg="#E6CBE5")
labFee_check = Checkbutton(frame, text = "Laboratory Fee", variable=labFee_var, command=compute_fees, bg="#E6CBE5")
labFeePrice_lbl = tk.Label(frame, text="P200", font=('Times New Roman', 10), bg="#E6CBE5")
regisCard_check = Checkbutton(frame, text = "Registration Card", variable=regisCard_var, command=compute_fees, bg="#E6CBE5")
regisCardPrice_lbl = tk.Label(frame, text="P50", font=('Times New Roman', 10), bg="#E6CBE5")
catalyst_check = Checkbutton(frame, text = "Catalyst", variable=catalyst_var, command=compute_fees, bg="#E6CBE5")
catalystPrice_lbl = tk.Label(frame, text="P50", font=('Times New Roman', 10), bg="#E6CBE5")
scouncil_check = Checkbutton(frame, text = "Student Council", variable=scouncil_var, command=compute_fees, bg="#E6CBE5")
scouncilPrice_lbl = tk.Label(frame, text="P50", font=('Times New Roman', 10), bg="#E6CBE5")
sID_check = Checkbutton(frame, text = "Student ID", variable=sID_var, command=compute_fees, bg="#E6CBE5")
sIDPrice_lbl = tk.Label(frame, text="P50", font=('Times New Roman', 10), bg="#E6CBE5")
miscellaneous_check = Checkbutton(frame, text = "Other Miscellaneous", variable=miscellaneous_var, command=compute_fees, bg="#E6CBE5")
miscellaneousPrice_lbl = tk.Label(frame, text="P100", font=('Times New Roman', 10), bg="#E6CBE5")
scholarship_lbl = tk.Label(frame, text="Scholarship Grants:", font=('Times New Roman', 10), bg="#E6CBE5")
nonScholar_radio = tk.Radiobutton(frame, text="Non-Scholar", variable=scholarship_var, value=1, bg="#E6CBE5")
fullScholar_radio = tk.Radiobutton(frame, text="Full Scholar", variable=scholarship_var, value=2, bg="#E6CBE5")
partialScholar_radio = tk.Radiobutton(frame, text="Partial Scholar", variable=scholarship_var, value=3, bg="#E6CBE5")
total_lbl = tk.Label(frame, text="Total Amount:", font=('Times New Roman', 10), bg="#E6CBE5")
total_entry = tk.Entry(frame, font=('Times New Roman', 10), bd=2, width=40, justify='center', state='readonly')
compute_btn = tk.Button(frame, text="COMPUTE", command=compute_total, bd=4, width=10)
clear_btn = tk.Button(frame, text="CLEAR", command=Clear, bd=4, width=10)

#displays all widgets
sname_lbl.place(x=25, y=20)
sname_entry.place(x=150, y=20)
units_lbl.place(x=25, y=50)
units_entry.place(x=150, y=50)
yrlvl_lbl.place(x=25, y=80)
yrlvl_combo.place(x=150, y=80)
fees_lbl.place(x=25, y=110)
labFee_check.place(x=45, y=140)
labFeePrice_lbl.place(x=170, y=140)
regisCard_check.place(x=45, y=170)
regisCardPrice_lbl.place(x=170, y=170)
catalyst_check.place(x=45, y=200)
catalystPrice_lbl.place(x=170, y=200)
scouncil_check.place(x=220, y=140)
scouncilPrice_lbl.place(x=355, y=140)
sID_check.place(x=220, y=170)
sIDPrice_lbl.place(x=355, y=170)
miscellaneous_check.place(x=220, y=200)
miscellaneousPrice_lbl.place(x=355, y=200)
scholarship_lbl.place(x=20, y=230)
nonScholar_radio.place(x=150, y=230)
fullScholar_radio.place(x=150, y=260)
partialScholar_radio.place(x=150, y=290)
total_lbl.place(x=25, y=320)
total_entry.place(x=150, y=320)
compute_btn.place(x=100, y=355)
clear_btn.place(x=250, y=355)

frame.mainloop()