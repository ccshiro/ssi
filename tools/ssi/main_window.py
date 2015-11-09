# Copyright 2015 shiro <shiro@worldofcorecraft.com>
# This file is part of SSI.

# SSI is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# SSI is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with SSI.  If not, see <http://www.gnu.org/licenses/>.

import code_widget
import spell_widget
import configparser
import os
import sys
from PyQt4 import QtCore, QtGui, QtWebKit, uic

sys.path.append(os.path.relpath('../../'))
import spell

class main_window(QtGui.QMainWindow):
    def __init__(self):
        super().__init__(None)
        ui = uic.loadUi('ssi.ui', self)

        self.loader_obj = None

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

        # Version menu connections
        self.version_boxes = [self.action_vers_1_12_1, self.action_vers_2_0_3,
            self.action_vers_2_4_3, self.action_vers_3_3_5]
        for action in self.version_boxes:
            action.toggled.connect(self.set_vers)
        # Code completion menu connection
        self.action_code_always.toggled.connect(self.set_auto_complete)
        self.action_code_space.toggled.connect(self.set_auto_complete)
        self.action_code_never.toggled.connect(self.set_auto_complete)
        # Icon menu connection
        self.action_icons.toggled.connect(self.icons_toggled)
        # Help and Exit menu connetions
        self.action_help.triggered.connect(self.show_help)
        self.action_exit.triggered.connect(self.exit_program)

        # Config
        # Version
        opts = self.parse_config()
        if opts['version'] == '1.12.1':
            self.action_vers_1_12_1.setChecked(True)
        elif opts['version'] == '2.0.3':
            self.action_vers_2_0_3.setChecked(True)
        elif opts['version'] == '2.4.3':
            self.action_vers_2_4_3.setChecked(True)
        elif opts['version'] == '3.3.5':
            self.action_vers_3_3_5.setChecked(True)
        # Code completion
        self.auto_complete = opts['auto_complete']
        if self.auto_complete == 'full':
            self.action_code_always.setChecked(True)
        elif self.auto_complete == 'key':
            self.action_code_space.setChecked(True)
        elif self.auto_complete == 'none':
            self.action_code_never.setChecked(True)
        # Icons
        if opts['icons']:
            self.action_icons.setChecked(True)

    def _query(self, query):
        # Query spell dbc
        try:
            res = self.spells.iter(query)
        except Exception as e:
            msg_box = QtGui.QMessageBox()
            msg_box.setText(str(e))
            msg_box.exec()
            return
        self._display_results(res)

    def _exec(self, code):
        # Uses exec() instead of query's eval()
        try:
            res = self.spells.execute(code, 'res')
        except Exception as e:
            msg_box = QtGui.QMessageBox()
            msg_box.setText(str(e))
            msg_box.exec()
            return
        self._display_results(res)

    def _query_name(self, name):
        name = name.replace('"', '\"').lower()
        res = self.spells.iter('"' + name + '" in spell.name.lower()')
        self._display_results(res)

    def _query_id(self, id):
        # Query spell dbc
        try:
            res = [self.spells.spell_dbc.table[id]]
        except KeyError:
            res = []
        self._display_results(res)

    def _display_results(self, res):
        # Clear current preview
        self.results.clearSelection()
        prev = self._find_tab('Preview')
        if prev:
            self.tabs.removeTab(self.tabs.indexOf(prev))
        # Put data into UI
        self.results.setSortingEnabled(False)
        self.results.setRowCount(len(res))
        for i in range(0, len(res)):
            id_item = QtGui.QTableWidgetItem()
            id_item.setData(QtCore.Qt.DisplayRole, res[i].id)
            name_item = QtGui.QTableWidgetItem()
            name = res[i].name
            if len(res[i].rank) > 0:
                name += ' (' + res[i].rank + ')'
            name_item.setText(name)
            self.results.setItem(i, 0, id_item)
            self.results.setItem(i, 1, name_item)
        self.results.setSortingEnabled(True)
        self.results_updated()
        # For exactly one item, preview it as well
        if len(res) == 1:
            self.results.selectRow(0)
    
    def _find_tab(self, name):
        for i in range(0, self.tabs.count()):
            if self.tabs.tabText(i) == name:
                return self.tabs.widget(i)
        return None

    def preview_spell(self):
        if len(self.sender().selectedItems()) == 0:
            return

        id = int(self.sender().selectedItems()[0].text())
        spell = self.spells.spell_dbc.table[id]

        prev = self._find_tab('Preview')
        if not prev:
            widget = spell_widget.SpellWidget(self.tabs, spell,
                self.action_icons.isChecked(), self.spells)
            self.tabs.setCurrentIndex(self.tabs.addTab(widget, 'Preview'))
        else:
            index = self.tabs.indexOf(prev)
            self.tabs.removeTab(index)
            widget = spell_widget.SpellWidget(self.tabs, spell,
                self.action_icons.isChecked(), self.spells)
            self.tabs.insertTab(index, widget, 'Preview')
            self.tabs.setCurrentIndex(index)

    def open_spell(self, index):
        id = int(self.results.item(index.row(), 0).text())
        spell = self.spells.spell_dbc.table[id]

        prev = self._find_tab('Preview')
        if prev:
            index = self.tabs.indexOf(prev)
            self.tabs.removeTab(index)
        else:
            index = self.tabs.rowCount()

        widget = spell_widget.SpellWidget(self.tabs, spell,
            self.action_icons.isChecked(), self.spells)
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
                self._query_id(int(text))
            else:
                self._query_name(text)
        # Code search
        elif code and len(code.toPlainText()) > 0:
            text = code.toPlainText()
            if text.startswith('res = []'):
                self._exec(text)
            else:
                self._query(code.toPlainText())
        # No input
        else:
            self.results.setRowCount(0)
            self.results_updated()

    def code_btn_clicked(self):
        widget = code_widget.CodeWidget(self.tabs, self.auto_complete,
            self.spells)
        self.tabs.insertTab(0, widget, 'Code')
        self.tabs.setCurrentIndex(0)
        self.code_btn.setEnabled(False)
        self.quick_search.clear()

    def tab_closed(self, index):
        if self.tabs.tabText(index) == 'Code':
            self.code_btn.setEnabled(True)
        self.tabs.removeTab(index)

    def set_vers(self, checked):
        if self.loader_obj:
            return

        if not checked:
            return

        # Uncheck other than this
        for a in self.version_boxes:
            if a != self.sender():
                a.setChecked(False)
        # Remove results, tabs and toggle code and exec button
        self.results.setRowCount(0)
        self.results_updated()
        self.tabs.clear()
        self.exec_btn.setEnabled(False)
        self.code_btn.setEnabled(True)

        vers = self.sender().objectName()[len('action_vers_'):]
        vers = vers.replace('_', '.')
        self.set_config_opt('version', vers)

        # Spawn worker thread to not block UI (loading and parsing DBC is slow)
        self.loader_obj = SpellLoader(vers)
        self.thread = QtCore.QThread()
        self.loader_obj.moveToThread(self.thread)
        self.loader_obj.finished.connect(self.thread.quit)
        self.thread.started.connect(self.loader_obj.work)
        self.thread.finished.connect(self.on_loaded)
        self.thread.start()
        self.setWindowTitle("Shiro's Spell Inspector (Loading DBC...)")
        
    def on_loaded(self):
        if self.loader_obj.err != None:
            for box in self.version_boxes:
                box.setChecked(False)
            err = QtGui.QMessageBox(self)
            err.setText(str(self.loader_obj.err))
            err.exec()
            self.loader_obj = None
            return

        self.spells = self.loader_obj.data
        self.exec_btn.setEnabled(True)
        self.fill_qs_completer()
        self.loader_obj = None
        self.setWindowTitle("Shiro's Spell Inspector")

    def set_auto_complete(self, checked):
        if not checked:
            return

        # Uncheck other boxes
        v = [self.action_code_always, self.action_code_space,
            self.action_code_never]
        for a in v:
            if a != self.sender():
                a.setChecked(False)

        if self.sender() == self.action_code_always:
            t = 'full'
        elif self.sender() == self.action_code_space:
            t = 'key'
        # NOTE: none is probably superfluous given how rare accidentally
        #       hitting ^space is
        elif self.sender() == self.action_code_never:
            t = 'none'

        # Switch completion style
        self.set_config_opt('auto_complete', t)
        self.auto_complete = t

        # Update code tab
        code = self._find_tab('Code')
        if code:
            code.set_completion_type(t)

    def icons_toggled(self, checked):
        self.set_config_opt('wowheadicons', checked)

    def show_help(self):
        widget = QtWebKit.QWebView()
        csspath = os.path.join('..', os.path.join('..',
            os.path.join('bootstrap', os.path.join('css'),
            os.path.join('bootstrap.min.css'))))
        css_url = QtCore.QUrl.fromLocalFile(os.path.abspath(csspath))
        html = ''
        page = open('help.html')
        for line in page.readlines():
            line = line.replace('${BOOTSTRAP_CSS}', css_url.toString())
            html += line
        page.close()
        widget.setHtml(html)
        widget.settings().setUserStyleSheetUrl(css_url)
        self.tabs.setCurrentIndex(self.tabs.addTab(widget, 'Help'))

    def exit_program(self):
        sys.exit(0)

    def parse_config(self):
        config = configparser.ConfigParser()
        dir_path = os.path.expanduser('~/.ssi/')
        path = os.path.expanduser('~/.ssi/.ssirc')
        if os.path.exists(path):
            try:
                config.read(path)
                return {'version': config['SSI']['version'],
                    'icons': True if
                        config['SSI']['wowheadicons'] == 'True' else False,
                    'auto_complete': config['SSI']['auto_complete']}
            except:
                pass # Write a new config if current is invalid

        os.makedirs(dir_path, exist_ok = True)

        config['SSI'] = {'version': 'None',
                         'wowheadicons': True,
                         'auto_complete': 'full'}
        with open(path, 'w') as f:
            config.write(f)

        return {'version': config['SSI']['version'],
            'icons': True if config['SSI']['wowheadicons'] == 'True' else False,
            'auto_complete': config['SSI']['auto_complete']}

    def set_config_opt(self, opt, val):
        """We made sure config exited at startup, if user deleted it in the
           mean-time, that's their problem."""
        config = configparser.ConfigParser()
        path = os.path.expanduser('~/.ssi/.ssirc')
        config.read(path)
        config['SSI'][opt] = str(val)
        with open(path, 'w') as f:
            config.write(f)

    def fill_qs_completer(self):
        """Provide auto-completion for spell names in quick-search"""
        c = QtGui.QCompleter()
        c.setCompletionMode(QtGui.QCompleter.PopupCompletion)
        c.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        model = QtGui.QStringListModel()
        # Fill with spell names
        names = set()
        for _, s in self.spells.spell_dbc.table.items():
            names.add(s.name)
        model.setStringList(list(names))
        c.setModel(model)
        self.quick_search.setCompleter(c)

class SpellLoader(QtCore.QObject):
    finished = QtCore.pyqtSignal()

    def __init__(self, vers):
        super().__init__()
        self.vers = vers
        self.err = None
        self.data = None

    def work(self):
        try:
            self.data = spell.Spells(self.vers)
        except RuntimeError as e:
            self.err = str(e)
        self.finished.emit()
