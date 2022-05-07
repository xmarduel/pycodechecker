
from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

# -----------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------

def format(color, style=''):
    """Return a QTextCharFormat with the given attributes.
    """
    _color = QtGui.QColor()
    _color.setNamedColor(color)

    _format = QtGui.QTextCharFormat()
    _format.setForeground(_color)
    if 'bold' in style:
        _format.setFontWeight(QtGui.QFont.Bold)
    if 'italic' in style:
        _format.setFontItalic(True)

    return _format

# Syntax styles that can be shared by all languages
STYLES = {
    'keyword': format('blue'),
    'operator': format('red'),
    'brace': format('darkGray'),
    'defclass': format('black', 'bold'),
    'string': format('magenta'),
    'string2': format('darkMagenta'),
    'comment': format('darkGreen', 'italic'),
    'self': format('black', 'italic'),
    'numbers': format('brown'),
}


class PythonHighlighter (QtGui.QSyntaxHighlighter):
    """Syntax highlighter for the Python language.
    """
    # Python keywords
    keywords = [
        'and', 'assert', 'break', 'class', 'continue', 'def',
        'del', 'elif', 'else', 'except', 'exec', 'finally',
        'for', 'from', 'global', 'if', 'import', 'in',
        'is', 'lambda', 'not', 'or', 'pass', 'print',
        'raise', 'return', 'try', 'while', 'yield',
        'None', 'True', 'False',
    ]

    # Python operators
    operators = [
        '=',
        # Comparison
        '==', '!=', '<', '<=', '>', '>=',
        # Arithmetic
        '\+', '-', '\*', '/', '//', '\%', '\*\*',
        # In-place
        '\+=', '-=', '\*=', '/=', '\%=',
        # Bitwise
        '\^', '\|', '\&', '\~', '>>', '<<',
    ]

    # Python braces
    braces = [
        '\{', '\}', '\(', '\)', '\[', '\]',
    ]
    def __init__(self, document):
        QtGui.QSyntaxHighlighter.__init__(self, document)

        # Multi-line strings (expression, flag, style)
        # FIXME: The triple-quotes in these two lines will mess up the
        # syntax highlighting from this point onward
        self.tri_single = (QtCore.QRegExp("'''"), 1, STYLES['string2'])
        self.tri_double = (QtCore.QRegExp('"""'), 2, STYLES['string2'])

        rules = []

        # Keyword, operator, and brace rules
        rules += [(r'\b%s\b' % w, 0, STYLES['keyword'])
            for w in PythonHighlighter.keywords]
        rules += [(r'%s' % o, 0, STYLES['operator'])
            for o in PythonHighlighter.operators]
        rules += [(r'%s' % b, 0, STYLES['brace'])
            for b in PythonHighlighter.braces]

        # All other rules
        rules += [
            # 'self'
            (r'\bself\b', 0, STYLES['self']),

            # Double-quoted string, possibly containing escape sequences
            (r'"[^"\\]*(\\.[^"\\]*)*"', 0, STYLES['string']),
            # Single-quoted string, possibly containing escape sequences
            (r"'[^'\\]*(\\.[^'\\]*)*'", 0, STYLES['string']),

            # 'def' followed by an identifier
            (r'\bdef\b\s*(\w+)', 1, STYLES['defclass']),
            # 'class' followed by an identifier
            (r'\bclass\b\s*(\w+)', 1, STYLES['defclass']),

            # From '#' until a newline
            (r'#[^\n]*', 0, STYLES['comment']),

            # Numeric literals
            (r'\b[+-]?[0-9]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b', 0, STYLES['numbers']),
        ]

        # Build a QRegExp for each pattern
        self.rules = [(QtCore.QRegExp(pat), index, fmt)
            for (pat, index, fmt) in rules]


    def highlightBlock(self, text):
        """Apply syntax highlighting to the given block of text.
        """
        # Do other syntax formatting
        for expression, nth, format in self.rules:
            index = expression.indexIn(text, 0)

            while index >= 0:
                # We actually want the index of the nth match
                index = expression.pos(nth)
                length = len(expression.cap(nth))
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)

        # Do multi-line strings
        in_multiline = self.match_multiline(text, *self.tri_single)
        if not in_multiline:
            in_multiline = self.match_multiline(text, *self.tri_double)


    def match_multiline(self, text, delimiter, in_state, style):
        """Do highlighting of multi-line strings. ``delimiter`` should be a
        ``QRegExp`` for triple-single-quotes or triple-double-quotes, and
        ``in_state`` should be a unique integer to represent the corresponding
        state changes when inside those strings. Returns True if we're still
        inside a multi-line string when this function is finished.
        """
        # If inside triple-single quotes, start at 0
        if self.previousBlockState() == in_state:
            start = 0
            add = 0
        # Otherwise, look for the delimiter on this line
        else:
            start = delimiter.indexIn(text)
            # Move past this match
            add = delimiter.matchedLength()

        # As long as there's a delimiter match on this line...
        while start >= 0:
            # Look for the ending delimiter
            end = delimiter.indexIn(text, start + add)
            # Ending delimiter on this line?
            if end >= add:
                length = end - start + add + delimiter.matchedLength()
                self.setCurrentBlockState(0)
            # No; multi-line string
            else:
                self.setCurrentBlockState(in_state)
                length = len(text) - start + add
            # Apply formatting
            self.setFormat(start, length, style)
            # Look for the next match
            start = delimiter.indexIn(text, start + length)

        # Return True if still inside a multi-line string, False otherwise
        if self.currentBlockState() == in_state:
            return True
        else:
            return False
        
        
        
        
        
'''
Text widget with support for line numbers
'''
 
class LNTextEdit(QtWidgets.QFrame):
 
    class NumberBar(QtWidgets.QWidget):
 
        def __init__(self, edit):
            QtWidgets.QWidget.__init__(self, edit)
 
            self.edit = edit
            #self.setFixedWidth(150)
            self.adjustWidth(1)
            
            pal = QtGui.QPalette()
            pal.setColor(QtGui.QPalette.Background, QtCore.Qt.green);
 
            self.setPalette(pal)

        def paintEvent(self, event):
            self.edit.numberbarPaint(self, event)
            QtWidgets.QWidget.paintEvent(self, event)
 
        def adjustWidth(self, count):
            width = self.fontMetrics().width("%d" % count)
            if self.width() != width:
                self.setFixedWidth(width)
 
        def updateContents(self, rect, scroll):
            if scroll:
                self.scroll(0, scroll)
            else:
                # It would be nice to do
                # self.update(0, rect.y(), self.width(), rect.height())
                # But we can't because it will not remove the bold on the
                # current line if word wrap is enabled and a new block is
                # selected.
                self.update()

 
    class PlainTextEdit(QtWidgets.QPlainTextEdit):
 
        def __init__(self, parent, *args):
            QtWidgets.QPlainTextEdit.__init__(self, parent)
            
            self.parent = parent
            
            #self.setFrameStyle(QtWidgets.QFrame.NoFrame)
            self.setFont("courier")

            highlight = PythonHighlighter(self.document())
 
            self.setFrameStyle(QtWidgets.QFrame.NoFrame)
            self.highlight()
            #self.setLineWrapMode(QPlainTextEdit.NoWrap)
 
            self.cursorPositionChanged.connect(self.highlight)
        
        def highlight(self):
            hi_selection = QtWidgets.QTextEdit.ExtraSelection()
 
            hi_selection.format.setBackground(self.palette().alternateBase())
            hi_selection.format.setProperty(QtGui.QTextFormat.FullWidthSelection, True)
            hi_selection.cursor = self.textCursor()
            hi_selection.cursor.clearSelection()
 
            self.setExtraSelections([hi_selection])
 
        def numberbarPaint(self, number_bar, event):
            font_metrics = self.fontMetrics()
            current_line = self.document().findBlock(self.textCursor().position()).blockNumber() + 1
 
            block = self.firstVisibleBlock()
            line_count = block.blockNumber()
            painter = QtGui.QPainter(number_bar)
            #painter.fillRect(event.rect(), self.palette().base())
            painter.fillRect(event.rect(), QtGui.QColor(220,220,220))
 
            # Iterate over all visible text blocks in the document.
            while block.isValid():
                line_count += 1
                block_top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
 
                # Check if the position of the block is out side of the visible
                # area.
                if not block.isVisible() or block_top >= event.rect().bottom():
                    break
 
                # We want the line number for the selected line to be bold.
                if line_count == current_line:
                    font = painter.font()
                    font.setBold(True)
                    painter.setFont(font)
                else:
                    font = painter.font()
                    font.setBold(False)
                    painter.setFont(font)
 
                # Draw the line number right justified at the position of the line.
                paint_rect = QtCore.QRect(0, block_top, number_bar.width(), font_metrics.height())
                painter.drawText(paint_rect, QtCore.Qt.AlignRight, "%d" % line_count)
 
                block = block.next()
 
            painter.end()

        def keyPressEvent(self, event):
            if event.matches(QtGui.QKeySequence.Save):
                return self.parent.save_content()
            else:
                return QtWidgets.QPlainTextEdit.keyPressEvent(self, event)
            
 

    def __init__(self, parent, tab_widget, path):
        '''
        '''
        QtWidgets.QFrame.__init__(self, parent)
 
        self.setFrameStyle(QtWidgets.QFrame.StyledPanel | QtWidgets.QFrame.Sunken)
 
        self.edit = self.PlainTextEdit(self)
        self.number_bar = self.NumberBar(self.edit)
 
        hbox = QtWidgets.QHBoxLayout(self)
        hbox.setSpacing(0)
        #hbox.setMargin(0)
        hbox.addWidget(self.number_bar)
        hbox.addWidget(self.edit)
 
        parent.setLayout(hbox)
 
        self.edit.blockCountChanged.connect(self.number_bar.adjustWidth)
        self.edit.updateRequest.connect(self.number_bar.updateContents)
        
        fp = open(path, 'r')
        self.setText(fp.read())
        fp.close()
        
        
        self.parent_widget = parent
        self.tab_widget = tab_widget # strane, this is not the parent() ???
        
        self.path = path
        
        idx =  self.get_tab_index()
        
        self.tabTitle = self.tab_widget.tabText(idx)
        
        # for editing
        self.edit.textChanged.connect(self.cb_textchanged)
        
    def cb_textchanged(self):
        self.setModified(True)
 
    def getText(self):
        return self.edit.toPlainText()
 
    def setText(self, text):
        self.edit.setPlainText(text)
 
    def isModified(self):
        return self.edit.document().isModified()
 
    def setModified(self, modified):
        self.edit.document().setModified(modified)
        
        self.tab_widget.setTabText(self.get_tab_index(), "*" + self.tabTitle)
 
    def setLineWrapMode(self, mode):
        self.edit.setLineWrapMode(mode)
        
    def get_tab_index(self):
        ''' '''
        return self.tab_widget.indexOf(self.parent())
    
    def save_content(self):
        ''' '''
        if self.isModified():
            fp = open(self.path, "w")
            fp.write(self.edit.toPlainText())
            fp.close()
            self.setModified(False)
            self.tab_widget.setTabText(self.get_tab_index(), self.tabTitle)
            return 1
        return 0
