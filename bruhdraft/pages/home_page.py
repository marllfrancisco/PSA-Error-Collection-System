import ttkbootstrap as tb


class HomePage(tb.Frame):

    def __init__(self, parent, controller):

        super().__init__(parent)
        # keep the frame inside
        # >>>>>

        titlefont = ("Arial", 25, "bold")
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
            text="Home Page",
            font=titlefont
        ).pack()

        tb.Label(
            headerframe,
            text="Heading",
            font=ourfont
        ).pack()