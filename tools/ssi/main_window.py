import code_widget
import spell_widget
import os
import sys
from PyQt4 import QtCore, QtGui, uic

sys.path.append(os.path.relpath('../../'))
import spell

class main_window(QtGui.QMainWindow):
    def __init__(self):
        super().__init__(None)
        ui = uic.loadUi('ssi.ui', self)

        # Results behavior
        self.results.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.results.horizontalHeader().setStretchLastSection(True)
        self.results.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.results.setColumnWidth(0, 60)

        # UI connections
        self.exec_btn.clicked.connect(self.exec_btn_clicked)
        self.code_btn.clicked.connect(self.code_btn_clicked)
        self.tabs.tabCloseRequested.connect(self.tab_closed)
        self.results.itemSelectionChanged.connect(self.preview_spell)
        self.results.itemDoubleClicked.connect(self.open_spell)
        # Menu connections
        self.version_boxes = [self.action_vers_1_12_1, self.action_vers_2_4_3,
            self.action_vers_3_3_5]
        for action in self.version_boxes:
            action.toggled.connect(self.set_vers)

    def _query(self, query):
        try:
            res = self.spells.iter(query)
        except Exception as e:
            msg_box = QtGui.QMessageBox()
            msg_box.setText(str(e))
            msg_box.exec()
            return
        self.results.setSortingEnabled(False)
        self.results.setRowCount(0)
        for i in range(0, len(res)):
            self.results.insertRow(i)
            id_item = QtGui.QTableWidgetItem()
            id_item.setData(QtCore.Qt.DisplayRole, res[i].id)
            name_item = QtGui.QTableWidgetItem()
            name_item .setText(str(res[i].name))
            self.results.setItem(i, 0, id_item)
            self.results.setItem(i, 1, name_item)
        self.results.setSortingEnabled(True)
        self.results_updated()
    
    def _find_tab(self, name):
        for i in range(0, self.tabs.count()):
            if self.tabs.tabText(i) == name:
                return self.tabs.widget(i)
        return None

    def preview_spell(self):
        if len(self.sender().selectedItems()) == 0:
            return

        id = int(self.sender().selectedItems()[0].text())
        spell = next(s for s in self.spells.spell_dbc.table if s.id == id)

        prev = self._find_tab('Preview')
        if not prev:
            widget = spell_widget.SpellWidget(self.tabs, spell)
            self.tabs.setCurrentIndex(self.tabs.addTab(widget, 'Preview'))
        else:
            index = self.tabs.indexOf(prev)
            self.tabs.removeTab(index)
            self.tabs.insertTab(index, prev, 'Preview')
            self.tabs.setCurrentIndex(index)

    def open_spell(self, index):
        id = int(self.results.item(index.row(), 0).text())
        spell = next(s for s in self.spells.spell_dbc.table if s.id == id)

        prev = self._find_tab('Preview')
        if prev:
            index = self.tabs.indexOf(prev)
            self.tabs.removeTab(index)
        else:
            index = self.tabs.rowCount()

        widget = spell_widget.SpellWidget(self.tabs, spell)
        self.tabs.insertTab(index, widget, widget.preferred_title())
        self.tabs.setCurrentIndex(index)

    def results_updated(self):
        # Set results found in title
        count = self.results.rowCount()
        if count == 0:
            self.setWindowTitle("Shiro's Spell Inspector") 
        else:
            self.setWindowTitle("Shiro's Spell Inspector (" + str(count) +
                ' results)')

    def exec_btn_clicked(self):
        quick = self.quick_search
        code = self._find_tab('Code')

        # Quick search
        if len(quick.text()) > 0:
            text = quick.text()
            if text.isdigit():
                self._query('spell.id == ' + text)
            else:
                text = text.replace('"', '\"').lower()
                self._query('"' + text + '" in spell.name.lower()')
        # Code search
        elif code and len(code.toPlainText()) > 0:
            self._query(code.toPlainText())
        # No input
        else:
            self.results.setRowCount(0)

    def code_btn_clicked(self):
        widget = code_widget.CodeWidget(self.tabs)
        self.tabs.insertTab(0, widget, 'Code')
        self.tabs.setCurrentIndex(0)
        self.code_btn.setEnabled(False)
        self.quick_search.clear()

    def tab_closed(self, index):
        if self.tabs.tabText(index) == 'Code':
            self.code_btn.setEnabled(True)
        self.tabs.removeTab(index)

    def set_vers(self, checked):
        if not checked:
            return

        # Uncheck other than this
        for a in self.version_boxes:
            if a != self.sender():
                a.setChecked(False)
        # Remove results, tabs and toggle code and exec button
        self.results.setRowCount(0)
        self.tabs.clear()
        self.exec_btn.setEnabled(False)
        self.code_btn.setEnabled(True)

        vers = self.sender().objectName()[len('action_vers_'):]
        vers = vers.replace('_', '.')
        try:
            self.spells = spell.Spells(vers)
            self.exec_btn.setEnabled(True)
        except Exception as e:
            self.sender().setChecked(False)
            err = QtGui.QMessageBox(self)
            err.setText(str(e))
            err.exec()
