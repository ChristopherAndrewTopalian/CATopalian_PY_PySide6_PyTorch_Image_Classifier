# create_dark_palette.py

from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtMultimedia import *

# DARK THEME FUNCTION
def create_dark_palette(app):
    """Sets the application colors to our preferred dark theme."""
    darkPalette = app.palette()
    # Utilizing our preferred 30, 30, 30 background
    bg_color = QColor(30, 30, 30) 
    darkPalette.setColor(QPalette.Window, bg_color)
    darkPalette.setColor(QPalette.WindowText, Qt.white)
    darkPalette.setColor(QPalette.Button, QColor(53, 53, 53))
    darkPalette.setColor(QPalette.ButtonText, Qt.white)
    darkPalette.setColor(QPalette.Base, QColor(20, 20, 20))
    darkPalette.setColor(QPalette.AlternateBase, bg_color)
    darkPalette.setColor(QPalette.Text, Qt.white)
    return darkPalette

####

# Dedicated to God the Father
# All Rights Reserved Christopher Andrew Topalian Copyright 2000-2026
# https://github.com/ChristopherTopalian
# https://github.com/ChristopherAndrewTopalian
# https://sites.google.com/view/CollegeOfScripting

