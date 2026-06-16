import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.tableview import Tableview

# more info about ttkbootstrap https://ttkbootstrap.readthedocs.io/en/latest/styleguide/

from pages.home_page import HomePage
from pages.auditlog import AuditLogPage
from pages.other_page import OtherPage

from sources.table_sources import c_dis_entry_audit, r_dis_entry_audit
# imports from source\table_sources.py

class App(tb.Window):

    def __init__(self):
        super().__init__(themename="profesh") #the custom ttkbootstrap theme: "profesh(ional)" 

        self.title("PSA Error Correction System")

        # normal size before fullscreen
        self.geometry("1100x500")

        # fullscreen at run
        self.state("zoomed")

        # ==========================
        # TOP NAVIGATION BAR
        # ==========================

        nav = tb.Frame(self, bootstyle="WARNING") #frame color highlighted
        nav.pack(
            fill="x",
            pady=10
        )


        # Nav Buttons ==========================
        tb.Button(
            nav,
            text="Home",
            bootstyle=PRIMARY,
            command=lambda: self.show_page("HomePage")
        ).pack(
            side="left",
            padx=5
        )

        tb.Button(
            nav,
            text="Audit Logs",
            bootstyle=INFO,
            command=lambda: self.show_page("AuditLogPage")
        ).pack(
            side="left",
            padx=5
        )

        tb.Button(
            nav,
            text="Extra Page",
            bootstyle=SUCCESS,
            command=lambda: self.show_page("OtherPage")
        ).pack(
            side="left",
            padx=5
        )


        # ==========================
        # PAGE AREA BELOW NAVBAR
        # ==========================

        self.page_container = tb.Frame(self)

        self.page_container.pack(
            fill="both",
            expand=True
        )


        self.pages = {}


        for Page in (
            HomePage,
            AuditLogPage,
            OtherPage
        ):

            frame = Page(
                self.page_container,
                self
            )

            self.pages[Page.__name__] = frame

            frame.place(
                relx=0,
                rely=0,
                relwidth=1,
                relheight=1
            )


        self.show_page("HomePage")


    def show_page(self, page):
        self.pages[page].tkraise()



if __name__ == "__main__":
    app = App()
    app.mainloop()