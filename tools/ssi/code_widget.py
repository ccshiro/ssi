from PyQt4 import QtCore, QtGui

class CodeWidget(QtGui.QTextEdit):
    def __init__(self, parent):
        super().__init__(parent)
        self.completer = QtGui.QCompleter()
        self.completer.setWidget(self)
        self.completer.setCompletionMode(QtGui.QCompleter.PopupCompletion)
        self.completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.completer.activated.connect(self.auto_complete)

        model = QtGui.QStringListModel()
        model.setStringList(self.get_toplevel_completers())
        self.completer.setModel(model)

    def auto_complete(self, s):
        """ Insert selected completion (s) at end of current word """
        cursor = self.textCursor()
        cursor.movePosition(QtGui.QTextCursor.Left)
        cursor.movePosition(QtGui.QTextCursor.EndOfWord)
        cursor.insertText(s[len(self.completer.completionPrefix()):])
        self.setTextCursor(cursor)

    def keyPressEvent(self, e):
        # If we have a popup tab means "complete!", escape "go away!"
        if self.completer.popup().isVisible():
            if e.key() == QtCore.Qt.Key_Tab or e.key() == QtCore.Qt.Key_Escape:
                e.ignore()
                return

        # Relay key press to QTextEdit
        super().keyPressEvent(e)

        # Key presses that hide current popup
        if (e.key() == QtCore.Qt.Key_Space or
            e.key() == QtCore.Qt.Key_Enter or
            e.key() == QtCore.Qt.Key_Return):
            if self.completer.popup().isVisible():
                self.completer.popup().hide()
            return

        # Start a new popup if necessary

        # Get currently selected word
        tc = self.textCursor()
        tc.select(QtGui.QTextCursor.WordUnderCursor)
        word = tc.selectedText()

        # Get full context (until previous space)
        tc.select(QtGui.QTextCursor.LineUnderCursor)
        context = tc.selectedText()
        if len(context) > 0:
            context = str.split(context)[-1]
            self.update_completion_list(context)

        # See if ^space was invoked
        forced = False
        if (e.modifiers() & QtCore.Qt.ControlModifier and
            e.key() == QtCore.Qt.Key_Space):
            forced = True

        # Only auto-complete empty lines if ^space was invoked
        if len(context) == 0 and not forced:
            if self.completer.popup().isVisible():
                self.completer.popup().hide()
            return

        # Set completed word and reset popup index if it differs
        if word != self.completer.completionPrefix:
            self.completer.setCompletionPrefix(word)
            self.completer.popup().setCurrentIndex(
                self.completer.completionModel().index(0, 0))

        # Draw completion popup
        cr = self.cursorRect()
        cr.setWidth(self.completer.popup().sizeHintForColumn(0) +
            self.completer.popup().verticalScrollBar().sizeHint().width())
        self.completer.complete(cr)

    def update_completion_list(self, context):
        completers = []
        if '.' not in  context:
            completers = self.get_toplevel_completers()
        elif context.split('.')[-2] == 'spell':
            completers = self.get_spell_completers()

        model = QtGui.QStringListModel()
        model.setStringList(completers)
        self.completer.setModel(model)

    def get_toplevel_completers(self):
        return ['spell']

    def get_spell_completers(self):
        s = ['id', 'name', 'rank']
        return s
