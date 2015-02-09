import os
import urllib.parse
import urllib.request
from PyQt4 import QtCore, QtGui, QtWebKit, uic

class SpellWidget(QtWebKit.QWebView):
    def __init__(self, parent, spell, icons, spells):
        """
        parameters:
           parent: widget
           spell:  spell we're displaying
           icons:  to load icons from wowhead or not
           spells: spell.Spells object
        """
        super().__init__(parent)
        self.spell = spell
        self.icons = icons
        self.spells = spells
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
        icon_path = ''
        if self.icons:
            icon = self.spells.get_icon_path(self.spell).split('\\')[-1]
            icon_path = 'http://static.wowhead.com/images/wow/icons/large/'
            icon_path += icon.lower() + '.jpg'
        else:
            icon_path = urllib.parse.urljoin('file:',
                urllib.request.pathname2url(os.path.abspath('./no_icon.png')))

        self._replace({
            '${NAME}': self.spell.name,
            '${ID}': self.spell.id,
            '${RANK}': self.spell.rank,
            '${ICON}': icon_path,
        })
