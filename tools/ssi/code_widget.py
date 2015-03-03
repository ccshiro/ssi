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

from PyQt4 import QtCore, QtGui

class CodeWidget(QtGui.QTextEdit):
    def __init__(self, parent, completion_type, spells):
        """completion_type: 'full', 'key' or 'none'"""
        super().__init__(parent)
        self.completer = QtGui.QCompleter()
        self.completer.setWidget(self)
        self.completer.setCompletionMode(QtGui.QCompleter.PopupCompletion)
        self.completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.completer.activated.connect(self.auto_complete)

        self.completion_type = completion_type
        self.spells = spells

        model = QtGui.QStringListModel()
        model.setStringList(self.get_toplevel_completers())
        self.completer.setModel(model)

        # Set code-friendly monospace font
        font = QtGui.QFont()
        font.setFamily('Monospace');
        font.setStyleHint(QtGui.QFont.Monospace)
        font.setFixedPitch(True)
        font.setPointSize(12)
        self.setFont(font)

        # Set tab stop to be the length of 4 spaces
        metrics = QtGui.QFontMetrics(font)
        self.setTabStopWidth(4 * metrics.width(' '))

        # Convert rich text to plain text
        self.setAcceptRichText(False)

    def set_completion_type(self, t):
        self.completion_type = t

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

        # See if ^space was invoked
        forced = False
        if (e.modifiers() & QtCore.Qt.ControlModifier and
            e.key() == QtCore.Qt.Key_Space):
            forced = True

        # Relay key press to QTextEdit
        if not forced:
            super().keyPressEvent(e)

        # Insert indentation if necessary when enter is pressed
        if e.key() == QtCore.Qt.Key_Enter or e.key() == QtCore.Qt.Key_Return:
            store = self.textCursor()
            self.moveCursor(QtGui.QTextCursor.Up)
            self.moveCursor(QtGui.QTextCursor.End, QtGui.QTextCursor.KeepAnchor)
            prev_line = self.textCursor().selectedText()
            self.setTextCursor(store)
            for s in prev_line:
                if s != '\t':
                    break
                self.insertPlainText('\t')

        # Key presses that hide current popup
        if (e.key() == QtCore.Qt.Key_Space or
            e.key() == QtCore.Qt.Key_Enter or
            e.key() == QtCore.Qt.Key_Return):
            if self.completer.popup().isVisible():
                self.completer.popup().hide()
                return

        if self.completion_type == 'none':
            return

        # Start a new popup if necessary

        # Get currently selected word
        tc = self.textCursor()
        tc.select(QtGui.QTextCursor.WordUnderCursor)
        word = tc.selectedText()

        # Get full context (from previous space to cursor)
        saved = self.textCursor()
        self.moveCursor(QtGui.QTextCursor.StartOfLine,
            QtGui.QTextCursor.KeepAnchor)
        context = self.textCursor().selectedText()
        self.setTextCursor(saved)
        if len(context) > 0:
            try:
                context = str.split(context)[-1]
                self.update_completion_list(context)
            except IndexError:
                return

        if self.completion_type == 'key' and not forced:
            return

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
        try:
            if '.' not in context:
                completers = self.get_toplevel_completers()
            elif context.split('.')[-2] == 'spell':
                completers = self.get_spell_completers()
            elif context.split('.')[-2] == 'spells':
                member_id = context.split('.')[-1]
                # Enumerations
                if ']' in member_id:
                    pass
                elif '[' in member_id:
                    member = getattr(self.spells, member_id[:-2]) # [ and ' or "
                    for key, _ in member.items():
                        completers.append(key)
                # Spells member
                else:
                    completers = self.get_spells_completers()
        except (IndexError, AttributeError):
            return

        model = QtGui.QStringListModel()
        model.setStringList(completers)
        self.completer.setModel(model)

    def get_toplevel_completers(self):
        return ['spell', 'spells']

    def get_spell_completers(self):
        s = [ 'id', 'category', 'dispel', 'mechanic', 'attr', 'stances',
              'stances_not', 'target_mask', 'cast_time_index', 'cooldown',
              'category_cooldown', 'interrupt_flags', 'aura_interrupt_flags',
              'channel_interrupt_flags', 'proc_flags', 'proc_chance',
              'proc_charges', 'max_level', 'base_level', 'level',
              'duration_index', 'power_type', 'power', 'range_index',
              'item_class', 'item_subclass', 'inv_slot', 'effect',
              'die_sides', 'base_dice', 'real_points_per_level',
              'base_points', 'mechanic_effect', 'target_a', 'target_b',
              'radius_index', 'aura', 'amplitude', 'multiple_value', 'chain',
              'misc_a', 'misc_b', 'trigger', 'points_per_cp', 'icon_id',
              'name', 'rank', 'tooltip', 'gcd_category', 'gcd',
              'max_target_level', 'spell_family', 'spell_mask', 'max_targets',
              'spell_class', 'prevention', 'dmg_multiplier', 'school_mask' ]
        return s

    def get_spells_completers(self):
              # Methods
        s = [ 'cast_time', 'duration', 'formula', 'icon_path', 'power_type',
              'radius', 'range', 'schools',
              # Attributes
              'attr0', 'attr1', 'attr2', 'attr3', 'attr4', 'attr5', 'attr6',
              'auras', 'aura_interrupts', 'channel_interrupts', 'dispels',
              'effects', 'families', 'interrupts', 'inv_slots', 'item_class',
              'mechanics', 'preventions', 'proc_flags', 'spell_class',
              'stances', 'targets' ]
        return s
