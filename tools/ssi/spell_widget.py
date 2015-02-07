from PyQt4 import QtCore, QtGui, uic

class SpellWidget(QtGui.QWidget):
    def __init__(self, parent, spell):
        super().__init__(parent)
        self.spell = spell

    def preferred_title(self):
        return str(self.spell.id)
