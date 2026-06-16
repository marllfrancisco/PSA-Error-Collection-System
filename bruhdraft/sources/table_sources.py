import csv
import os

# finds file within script location/folder
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def get_path(filename):
    return os.path.join(SCRIPT_DIR, filename)

path_csv_disc_entries = get_path('discrepancy_entries.csv')

# from csv file within "source" folder

with open(path_csv_disc_entries, newline='', encoding='utf-8') as file:
    csvreader = csv.reader(file)
    c_disc_entries = next(csvreader)    # Column headers
    r_disc_entries = list(csvreader)    # Data rows