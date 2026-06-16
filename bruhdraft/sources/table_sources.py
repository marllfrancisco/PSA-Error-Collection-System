'''
# ================= FOR CSV FILES
import csv
import os
# finds file within script location/folder
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def get_path(filename):
    return os.path.join(SCRIPT_DIR, filename)

path_csv_disc_entries = get_path('discrepancy_audit.csv')
# from csv file within "source" folder
with open(path_csv_disc_entries, newline='', encoding='utf-8') as file:
    csvreader = csv.reader(file)
    c_disc_entries = next(csvreader)    # Column headers
    r_disc_entries = list(csvreader)    # Data rows
'''

# Needs (mysql-connector-python)
# included in required.txt
# ===> pip install -r required.txt <====

import mysql.connector
# Establish connection with your credentials
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="password", #enter your db password here!! ⚠️
    database="ecorrectdb" # .db filename
)
cursor = conn.cursor()

# ==== Execute your target query
cursor.execute("SELECT * FROM discrepancy_entries_audit")

# ==== Column Headers dynamically from cursor description
c_dis_entry_audit = [desc[0] for desc in cursor.description]

# ==== Extract Row Data as a list of lists/tuples
r_dis_entry_audit = cursor.fetchall()

# Close connections
cursor.close()
conn.close()