import ttkbootstrap as tb
import os


class OtherPage(tb.Frame):

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
            text="Other page",
            font=titlefont
        ).pack(anchor="w")

        tb.Label(
            headerframe,
            text="Heading",
            font=ourfont
        ).pack(anchor="w")