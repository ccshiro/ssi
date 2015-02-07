import os
from PyQt4 import QtCore, QtGui, QtWebKit, uic

class SpellWidget(QtWebKit.QWebView):
    def __init__(self, parent, spell):
        super().__init__(parent)
        self.spell = spell
        self.load_html() 
        self.setHtml(self.html)
        # Note: The documentation says that external css should be located
        #       relative to baseUrl, but even when it is, it's not loaded. Not
        #       sure why not. We get around that like this
        path = QtCore.QUrl.fromLocalFile('template.css')
        self.settings().setUserStyleSheetUrl(path)

    def preferred_title(self):
        return str(self.spell.id)

    def load_html(self):
        """Load template and replace placeholders"""
        self.html = ''
        page = open('template.html')
        for line in page.readlines():
            self.html += line
        self.expand_placeholders()

    def _replace(self, dic):
        for i, j in dic.items():
            self.html = self.html.replace(i, str(j))

    def expand_placeholders(self):
        """Parses HTML, replacing placeholders"""
        self._replace({
            '${NAME}': self.spell.name,
            '${ID}': self.spell.id,
            '${RANK}': self.spell.rank,
        })
