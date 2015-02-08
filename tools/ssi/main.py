#!/usr/bin/env python3

import main_window
from PyQt4 import QtGui
import os
import sys
import sip

app = QtGui.QApplication(sys.argv)
wnd = main_window.main_window()

def main():
    sip.setdestroyonexit(False)
    wnd.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
