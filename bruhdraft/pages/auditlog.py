import ttkbootstrap as tb
from ttkbootstrap.constants import *
from sources.table_sources import c_dis_entry_audit, r_dis_entry_audit
import os


class AuditLogPage(tb.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)

        titlefont = ("Arial", 18, "bold")
        ourfont = ("Arial", 12)

        # ---------------------------------------------------
        # MAIN FRAME
        # ---------------------------------------------------

        mainframe = tb.Frame(self)
        mainframe.pack(fill="both", expand=True)

        # ---------------------------------------------------
        # HEADER FRAME
        # ---------------------------------------------------

        headerframe = tb.Frame(mainframe)
        headerframe.pack(fill="x", padx=20, pady=10)

        tb.Label(
            headerframe,
            text="Audit Logs",
            font=titlefont
        ).pack(anchor="w")

        tb.Label(
            headerframe,
            text="Modifications made by employees",
            font=ourfont
        ).pack(anchor="w")
        
        # ---------------------------------------------------
        # TABLE FRAME
        # ---------------------------------------------------

        tableframe = tb.Frame(mainframe)
        tableframe.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )

        self.dv = tb.tableview.Tableview(
            master=tableframe,
            paginated=True,
            searchable=True,
            bootstyle=SUCCESS,
            pagesize=10,
            height=10,
        )
        self.dv.grid(row=0, column=0, padx=5, pady=5)  # Tableview is placed

        # Integrate the data source to Tableview
        self.dv.build_table_data(c_dis_entry_audit, r_dis_entry_audit)  # adding column and row data
        self.dv.load_table_data()  # refresh the table view with data
        self.dv.autofit_columns()  # Adjust with available space
        self.dv.autoalign_columns()  # String left and Numbers to right