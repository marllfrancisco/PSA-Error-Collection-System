# EVERY WIDGET MUST REGISTER TO THIS THEME
# use: from SysTheme import psatheme
# or:  import SysTheme as st

from ttkbootstrap.style import ThemeDefinition

# psatheme - for more notable theme name
psatheme = ThemeDefinition(
    name="psa",
    themetype="light",
    colors={
        "primary": "#0C66AB",
        "secondary": "#81ACC9",
        "success": "#2E8B57",
        "info": "#1565C0",
        "warning": "#E0AA49",
        "danger": "#C62828",
        "light": "#FFFFFF",
        "dark": "#222222",
        "bg": "#DDE5F6",
        "fg": "#222222",
        "selectbg": "#0C66AB",
        "selectfg": "#FFFFFF",
        "border": "#E5E5E5",
        "inputfg": "#424882",
        "inputbg": "#f4faff",
        "active": "#b8b8c9",
    }
)

# FONT HIERARCHY
titlefont = ("Segoe UI", 25, 'bold')
subtitlefont = ("Segoe UI", 15, 'bold')
ourfont = ("Poppins", 15)
navfont = ("Poppins", 12) # navigation links

# SPACING SYSTEM
    # padx & pady - spaces between widgets (x-axis or y-axis)
    # always use AT LEAST 5padx and 5pady

# OTHERS (CSS Equivalent)
""" 
    If using NAvigation Bar:
        background: #FFFFFF;
        height: 80px;
        border-bottom: 1px solid #E5E5E5;

    If using Hero Section:
        background: linear-gradient(
        135deg,
        #0C66AB,
        #1565C0
    );

    If using Cards:
        background: #FFFFFF;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        padding: 32px;

"""
