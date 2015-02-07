#!/usr/bin/env python3

import main_window
from PyQt4 import QtGui
import os
import sys

def main():
    app = QtGui.QApplication(sys.argv)

    wnd = main_window.main_window()
    wnd.show()

    sys.exit(app.exec())

if __name__ == '__main__':
    main()
