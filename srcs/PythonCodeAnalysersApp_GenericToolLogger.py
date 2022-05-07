
'''
COPYRIGHT (C) XAM GmbH

MODULE DESCRIPTION:

'''

import os
import re
import queue
import _thread

from PySide2 import QtWidgets
from PySide2 import QtCore
from PySide2 import QtGui

import PythonCodeAnalysersApp_PyLintOutputStyler
import PythonCodeAnalysersApp_PyFlakesOutputStyler
import PythonCodeAnalysersApp_PyMetricsOutputStyler
import PythonCodeAnalysersApp_ShellOutputStyler

import PythonCodeAnalysersApp_TextEditor

#----------------------------------------------------------------

class LoggerReceiver:
    '''
    '''
    def __init__(self, parent, onreceive):
        self.parent = parent
        self.queue = None  # to be set
        self.onreceive = onreceive
        self.onhold = False

        self.queue = None

        self.lock = _thread.allocate_lock()

    #--------------------------------------------------------------------------
    def start(self):
        # make a timer
        self.timer = QtCore.QTimer(self.parent)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.on_timer)
        self.timer.start()
        self.started = 1

    #-------------------------------------------------------------------------
    def stop(self):
        if self.started:
            self.timer.stop()
            self.started = 0

    def restart(self):
        if not self.started:
            self.timer.start()
            self.started = 1

    #-------------------------------------------------------------------------
    def set_queue(self, queue):
        self.lock.acquire()
        self.queue = queue
        self.lock.release()

    #-------------------------------------------------------------------------
    def has_queue(self):
        self.lock.acquire()
        return self.queue is not None
        self.lock.release()
        
    #-------------------------------------------------------------------------
    def on_timer(self):
        if self.queue is None:
            return

        if self.onhold:
            return

        self.lock.acquire()

        try:  # get data from the queue ...
            action_with_args = self.queue.get_nowait()
            #print "on_timer : %s" % action_with_args
            while action_with_args :
                action, args = action_with_args
                # log
                self.onreceive(action, args)
                # get next
                action_with_args = self.queue.get_nowait()

        except queue.Empty as msg:
            pass
        except Exception as msg:
            raise

        self.lock.release()

# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------

class GenericToolLoggerView(QtWidgets.QTextEdit):
    '''
    '''
    def __init__(self, parent):
        ''' '''
        QtWidgets.QTextEdit.__init__(self, parent)

        # start receiver
        self.olog = LoggerReceiver(self, self.on_receive)
        self.olog.start()

        self.mousePressEvent = self.text_click
        
    def text_click(self, event):
        '''
        callback to jump to the "error" in the file
        '''
        #print "text_click" , self.objectName()
    
        def pylint_click(lines, line, len1, len2, line_no):
            
            def pylint__module_for_line(line_no):
                '''
                '''
                line_text = lines[line_no]
                while ( line_no > 0 and not line_text.startswith("************* Module ") ):
                    line_no = line_no - 1
                    line_text = lines[line_no]
        
                if line_no == 0:
                    module = None
                else:
                    module = lines[line_no].split("************* Module ")[1].strip()
        
                return module
        
            def pylint__file_for_line(line_no):
                '''
                '''
                line_text = line_text = lines[line_no]
                while ( line_no > 0 and not line_text.startswith("************* Module ") ):
                    line_no = line_no - 1
                    line_text = line_text = lines[line_no]
        
                if line_no == 0:
                    module = None
                else:
                    module = line_text = lines[line_no].split("************* Module ")[1].strip()
        
                    # but the module is not with the full path! -> read the cmdline!
                    line_no_module = line_no
        
                    # get the "header" "STARTING PyLint..."
                    while ( line_no > 0 and not line_text.startswith("STARTING PyLint") ):
                        line_no = line_no - 1
                        line_text = lines[line_no]
        
                    cmdline = ""  # is the text between line_no and line_no_module
                    for aline_no in range(line_no + 1, line_no_module):
                        cmdline += lines[aline_no]
        
                    print("cmdline = %s" % cmdline)
                    file = cmdline.split(" ")[-1].strip()
                    print("file = %s" % file)
        
                    # check the module is the file
                    basefile = os.path.basename(file)
                    basemodule = basefile[:-3]  # remove the ".py"
        
                    if not ( basemodule == module or basemodule == module.split(".")[-1] ):
                        print("PyLint.GetRelatedFileForLine ERROR: module %s <=> file %s " % (module, file))
                        file = None
        
                return file
        
            creg_moduleinfo  = re.compile("\*\*\*\*\*\*\*\*\*\*\*\*\* Module (.*)$")
            creg_messageinfo = re.compile("^(.*):( )*([0-9]*),( )*([0-9]*):.*$")

            # is the selected line ok in order to jump to the related file?
            moduleinfo = creg_moduleinfo.search(line)
            if moduleinfo:
                # "header" has been selected
                module = moduleinfo.groups()[0]
                module = module.strip()
    
                # the file path is given by a line above the "header" line
                file   = pylint__file_for_line(line_no)
    
                self.show_file(file)
    
            else:
                messageinfo = creg_messageinfo.search(line)
                # get the analyser and file
                if messageinfo:
                    # valid line has been selected
    
                    # the file path is given by a line above the "header" line
                    file = pylint__file_for_line(line_no)
    
                    if file:
                        error, dummy0, line, dummy1, column = messageinfo.groups()
    
                        error  = error.strip()
                        line   = int(line.strip())
                        column = int(column.strip())
    
                        self.show_file(file, line)
                    
        def pyflakes_click(lines, line, len1, len2, line_no):
            
            creg_header = re.compile("^=== File: (.*) ===$")
            creg1 = re.compile("^(.*):([0-9]*):.*$")          # line is given
            creg2 = re.compile("^(.*):([0-9]*):([0-9]*):.*$") # line & column are given
            creg0 = re.compile("^(.*):.*$") # no line & column are given
    
            # is the selected line ok in order to jump to the related file?
            res0 = creg_header.search(line)
            if res0:
                # "header" has been selected
                file = res0.groups()[0]
    
                file = file.strip()
    
                self.show_file(file)
            else:
                if "problem decoding source" in line:
                    res = creg0.search(line)  
                elif "invalid syntax" in line:
                    res = creg2.search(line)
                else:
                    res = creg1.search(line)
                
                if res:
                    # valid line has been selected
                    if "problem decoding source" in line:
                        file, line = res.groups(), 0
                    elif "invalid syntax" in line:
                        file, line, column = res.groups()
                    else:
                        file, line = res.groups()
    
                    file = file.strip()
                    line = int(line.strip())
    
                    self.show_file(file, line)
  
        def pymetrics_click(lines, line, len1, len2, line_no):
            
            def pymetrics__module_for_line(line_no):
                '''
                '''
                line_text = lines[line_no]
                while ( line_no > 0 and not line_text.startswith("=== File: ") ):
                    line_no = line_no - 1
                    line_text = lines[line_no]
        
                if line_no == 0:
                    module = None
                else:
                    module = lines[line_no].split("===")[1].strip()
                    module = module.split("File:")[-1].strip()
        
                return module
        
            def pymetrics__section_for_line(line_no):
                '''
                '''
                line_text = lines[line_no]
        
                while ( line_no > 0 ):
                    line_no = line_no - 1
                    line_text = lines[line_no]
        
                    isHeader             = line_text.startswith("===")
                    isBasicMetrics       = line_text.startswith("Basic Metrics")
                    isFunctionsDocString = line_text.startswith("Functions DocString")
                    isClassesDocString   = line_text.startswith("Classes DocString")
                    isMcCabeMetric       = line_text.startswith("McCabe Complexity Metric")
                    isSlocMetric         = line_text.startswith("COCOMO 2's SLOC Metric")
                    isHalsteadMetric     = line_text.startswith("Halstead Metrics")
        
                    if isHeader: return "Header"
                    if isBasicMetrics: return "Basic Metrics"
                    if isFunctionsDocString: return "Functions DocString"
                    if isClassesDocString: return "Classes DocString"
                    if isMcCabeMetric: return "McCabe Complexity Metric"
                    if isSlocMetric: return "COCOMO 2's SLOC Metric"
                    if isHalsteadMetric: return "Halstead Metrics"
        
                if line_no == 0:
                    return None
        
            def pymetrics__line_for_declaration(filename, funcpath, item_cat=None):
                '''
                '''
                fp = open(filename, "r")
        
                if not fp:
                    return -1
        
                funcpath = funcpath.split(".")
        
                if item_cat is None :
                    # deduce item_cat fromn the funcpath
                    if len(funcpath) == 1:
                        item_cat = "function"
                    elif len(funcpath) == 2:
                        item_cat = "class.method"   # could be "function.function" or "class.class"
                    elif len(funcpath) == 3:
                        item_cat = "class.class.method"  # could be "class.method.function" or "function.function.function" or ...
                    else:
                        item_cat = "class"  # well, to difficult to search ...
        
        
                if item_cat == "class":
                    creg_classdef  = re.compile("^class %s[ ]*[:\(]" % funcpath[0])
        
                    for k, line in enumerate(fp):
                        if creg_classdef.findall(line):
                            fp.close()
                            return k
        
                if item_cat == "function":
                    creg_functiondef = re.compile("^def %s[ ]*\(" % funcpath[0])
        
                    for k, line in enumerate(fp):
                        if creg_functiondef.findall(line):
                            fp.close()
                            return k
        
                if item_cat == "class.method":
                    creg_classdef  = re.compile("^class %s[ ]*[:\(]" % funcpath[0])
                    creg_methoddef = re.compile("^    def %s[ ]*\(" % funcpath[1])
        
                    in_class = False
                    for k, line in enumerate(fp):
                        if line.startswith("class"):
                            if creg_classdef.findall(line):
                                in_class = True
                            else:
                                in_class = False # bug if line starts with "class XXX" in a commentar!!!:
        
                        if in_class:
                            if creg_methoddef.findall(line):
                                fp.close()
                                return k
        
                if item_cat == "class.class":
                    creg_classdef1 = re.compile("^class %s[ ]*[:\(]" % funcpath[0])
                    creg_classdef2 = re.compile("^    class %s[ ]*[:\(]" % funcpath[1])
        
                    in_class1 = False
                    for k, line in enumerate(fp):
                        if line.startswith("class"):
                            if creg_classdef1.findall(line):
                                in_class1 = True
                            else:
                                in_class1 = False # bug if line starts with "class XXX" in a commentar!!!:
        
                        if in_class1:
                            if creg_classdef2.findall(line):
                                fp.close()
                                return k
        
                if item_cat == "function.function":
                    creg_funcdef1  = re.compile("^def %s[ ]*\(" % funcpath[0])
                    creg_funcdef2 = re.compile("^    def %s[ ]*\(" % funcpath[1])
        
                    in_func = False
                    for k, line in enumerate(fp):
                        if line.startswith("def"):
                            if creg_funcdef1.findall(line):
                                in_func = True
                            else:
                                in_func = False
        
                        if in_func:
                            if creg_funcdef2.findall(line):
                                fp.close()
                                return k
        
                if item_cat == "class.class.method":
                    creg_classdef1 = re.compile("^class %s[ ]*[:\(]" % funcpath[0])
                    creg_classdef2 = re.compile("^    class %s[ ]*[:\(]" % funcpath[1])
                    creg_methoddef = re.compile("^        def %s[ ]*\(" % funcpath[2])
        
                    in_class1 = False
                    in_class2 = False
                    for k, line in enumerate(fp):
                        if line.startswith("class"):
                            if creg_classdef1.findall(line):
                                in_class1 = True
                            else:
                                in_class1 = False  # bug if line starts with "class XXX" in a commentar!!!:
        
                        if in_class1:
                            if line.startswith("    class"):
                                if creg_classdef2.findall(line):
                                    in_class2 = True
                                else:
                                    in_class2 = False
        
                        if in_class1 and in_class2:
                            if creg_methoddef.findall(line):
                                fp.close()
                                return k
        
        
                fp.close()
        
                return -1
            
            # ---------------------------------------------------------------------------------
            # ---------------------------------------------------------------------------------
            
            creg0 = re.compile("^=== File: (.*) ===$")
            # a compiled regexpr to parse a selected line of McCabe Complexity
            creg = re.compile("^ *([0-9]*) *(.*)$")
            # a compiled regexpr to parse a selected line of Halstead Metrics
            creg_h = re.compile("^\((.)\) (.*?) .*$")  # non greedy...

            # compiled regexprs to parse a selected line of the header
            simplereport_modulewithdocstring = re.compile("^Module (.*) is missing a module doc string. Detected at line (.*)$")
            
            
            # is the selected line ok in order to jump to the related file?
            res0 = creg0.search(line)
            if res0:
                # "header" has been selected
                file = res0.groups()[0]
    
                file = file.strip()
    
                self.show_file(file)
    
            else:
                #  an other line than the "header" is selected...
                line_text = lines[line_no]
    
                # the file is given by a line above... starting with "***** Module <file>"
                file = pymetrics__module_for_line(line_no)
                #print "--> ", file
    
                # find in which section we are - one of
                # "Header"
                # "Basic Metrics"
                # "Functions DocString"
                # "Classes DocString"
                # "McCabe Complexity Metric"
                # "COCOMO 2's SLOC Metric"
                # "Halstead Metrics"
                # None
                section = pymetrics__section_for_line(line_no)
                #print "-->section ", section
    
                line_no = -1
    
                if section:
                    if section == "Header":
                        if simplereport_modulewithdocstring.match(line):
                            res = simplereport_modulewithdocstring.findall(line)
                            line_no = int(res[0][1])
                        else:
                            toks = line.strip().split(" ")
                            funcpath = toks[1].strip()
    
                            line_no = pymetrics__line_for_declaration(file, funcpath)
    
                    if section == "Basic Metrics":
                        line_no = 0
                    if section == "Functions DocString":
                        # line of the form "+ <funcpath>"
                        flag, funcpath = line.strip().split(" ")
                        # find the line in the file where the class's method/function is defined...
                        line_no = pymetrics__line_for_declaration(file, funcpath)
                    if section == "Classes DocString":
                        # line of the form "+ <classpath>" or "- <classpath>"
                        flag, classpath = line.strip().split(" ")
                        nb_classes = min(2, len(classpath.split(".")))  # max 2 classes depth to look for...
                        item_class = ".".join( ["class"] * nb_classes )
                        # find the line in the file where the class is defined...
                        line_no = pymetrics__line_for_declaration(file, classpath, item_class)
                    if section == "McCabe Complexity Metric":
                        # line of the form "    <nb>  <funcpath>"
                        res = creg.search(line)
                        if res:
                            nb, funcpath = res.groups()
    
                            nb       = nb.strip()
                            funcpath = funcpath.strip()
                            # find the line in the file where the class's method/function is defined...
                            line_no = pymetrics__line_for_declaration(file, funcpath)
                    if section == "COCOMO 2's SLOC Metric":
                        line_no = 0
                    if section == "Halstead Metrics":
                        # line of the form "<cat>  <classname>.<methodname>  ..."
                        # line of the form "<cat>  <functionname>            ..."
                        res = creg_h.search(line)
                        print(str(res))
                        if res:
                            cat, id = res.groups()
    
                            if cat == 'M':
                                line_no = 0  # open the module itself at the first line
                            if cat == 'C':
                                classname = id.strip()
                                # find the line in the file where the class's is defined...
                                line_no = pymetrics__line_for_declaration(file, classname, "class")
                            if cat == 'F':
                                funcpath = id.strip()
                                # find the line in the file where the class's method/function is defined...
                                line_no = pymetrics__line_for_declaration(file, funcpath)
                else:
                    pass
    
            if line_no != -1:
                self.show_file(file, line_no + 1)
        
        def processes_info_click(lines, line, len1, len2, line_no):
            
            creg = re.compile("^\t analyser is : (.*) for file (.*)\.\.\. .*$")
            
            # jump to the selected logger at the right place (the analysed file)
            res = creg.search(line)
            # get the analyser and file
            if res:
                analyser, file = res.groups()
    
                analyser = analyser.strip()
                file     = file.strip()
    
                if analyser == 'PyLint':
                    file = os.path.basename(file)
                    file = file[:-3]
    
                topframe = self
                while topframe and topframe.parent() is not None:
                    topframe = topframe.parent()

                logger_notebook = topframe.ui.TOOLS_LOGGERS_TAB
    
                pagename_map = { 
                    "TOOL_PYLINT_LOGGER"    : 'PyLint',
                    "TOOL_PYFLAKES_LOGGER"  : 'PyFlakes',
                    "TOOL_PYMETRICS_LOGGER" : 'PyMetrics',
                } 
                
                for i in range(logger_notebook.count()):
                    w = logger_notebook.widget(i)
                    pagename = w.objectName()
                    if pagename_map[w.objectName()] == analyser:
                        logger_notebook.setCurrentWidget(w) # change the selection to the right tool
                        break
    
                text = topframe.loggerviews[analyser].toPlainText()
                alines = text.split('\n')
                nblines = len(alines)
    
                fileflag = {'PyFlakes':"=== File: %s ===",
                            'PyMetrics':"=== File: %s ===",
                            'PyLint':"************* Module %s"
                }
    
                for line_no in range(nblines):
                    aline = alines[line_no]
                    if aline == fileflag[analyser] % file :
                        self.goto_line(topframe.loggerviews[analyser], line_no, select=True)
                        break
        
        # -------------------------------------------------------------------------------------
        # -------------------------------------------------------------------------------------
        
        pos = event.pos()
        
        lines, line, len1, len2, line_no = self.get_selected_lineinfo(pos)
        print("selected line %s" % line)
        
        #start
        # Highlight the Selection
        # self.SetSelection(len1, len2)
            
        if self.objectName() == "PROCESSES_LOGGER":
            processes_info_click(lines, line, len1, len2, line_no)
            
        if self.objectName() == "TOOL_PYLINT_LOGGER_VIEW":
            pylint_click(lines, line, len1, len2, line_no)
            
        if self.objectName() == "TOOL_PYFLAKES_LOGGER_VIEW":
            pyflakes_click(lines, line, len1, len2, line_no)
            
        if self.objectName() == "TOOL_PYMETRICS_LOGGER_VIEW":
            pymetrics_click(lines, line, len1, len2, line_no)
            
        # end
        #self.SetFocus()  # focus can has been lost when opening the new editor
        #self.SetSelection(len1, len2)      

    def set_logging_queue(self, logging_queue):
        '''
        Parameters:
            - logging_queue: queue full of QTextCtrl operations

        Description:
            - pass the logging queue to the QTextCtrl "LoggerReceiver"
        '''
        self.olog.set_queue(logging_queue)

    def flush_logging_queue(self):
        '''
        '''
        self.olog.on_timer()

    def on_receive(self, action, arg):
        '''
        '''
        try:
            if action == "InsertText":
                self.moveCursor(QtGui.QTextCursor.End)
                self.insertPlainText(arg)
                self.moveCursor(QtGui.QTextCursor.End)
            elif  action == "InsertColoredText":
                text, color = arg
                format = QtGui.QTextCharFormat()
                format.setForeground(QtGui.QBrush(QtGui.QColor(color)))
                self.setCurrentCharFormat(format)
                self.insertPlainText(text)
            elif action == "AppendText":
                self.append(arg)
            elif action == "SetLineFontColor":
                color = QtGui.QColor(arg)
                self.setTextColor(color)
            elif action == "SetLineFontWeight":
                '''
                FONTWEIGHT_NORMAL
                FONTWEIGHT_LIGHT
                FONTWEIGHT_BOLD
                FONTWEIGHT_DEMIBOLD
                FONTWEIGHT_BLACK
                '''
                if arg == "FONTWEIGHT_NORMAL":
                    self.setFontWeight(QtGui.QFont.Weight.Normal)
                elif arg == "FONTWEIGHT_LIGHT":
                    self.setFontWeight(QtGui.QFont.Weight.Light)
                elif arg == "FONTWEIGHT_BOLD":
                    self.setFontWeight(QtGui.QFont.Weight.Bold)
                elif arg == "FONTWEIGHT_DEMIBOLD":
                    self.setFontWeight(QtGui.QFont.Weight.DemiBold)
                elif arg == "FONTWEIGHT_BLACK":
                    self.setFontWeight(QtGui.QFont.Weight.Black)
                
            elif action == "SetLineFontFamily":
                ''' 
                FONTFAMILY_DEFAULT
                FONTFAMILY_DECORATIVE
                FONTFAMILY_ROMAN
                FONTFAMILY_SCRIPT
                FONTFAMILY_SWISS
                FONTFAMILY_MODERN
                FONTFAMILY_TELETYPE
                '''
                if arg == "FONTFAMILY_DEFAULT":
                    self.setFontFamily("roman")
                elif arg == "FONTFAMILY_TIMES":
                    self.setFontFamily("Times")
                elif arg == "FONTFAMILY_ROMAN":
                    self.setFontFamily("roman")
                elif arg == "FONTFAMILY_SCRIPT":
                    self.setFontFamily("script")
                elif arg == "FONTFAMILY_SWISS":
                    self.setFontFamily("Helvetica")
                elif arg == "FONTFAMILY_MODERN":
                    self.setFontFamily("modern")
                elif arg == "FONTFAMILY_TELETYPE":
                    self.setFontFamily("courier")
                    
                # hack on windows
                self.setFontFamily("courier")
                #self.setFontSize(14)

            elif action == "SetLineFontStyle":
                '''
                FONTSTYLE_NORMAL
                FONTSTYLE_SLANT
                FONTSTYLE_ITALIC
                '''
                font = self.currentFont()
                if arg == "FONTSTYLE_ITALIC":
                    font.setStyle(QtGui.QFont.Style.StyleItalic)
                elif arg == "FONTSTYLE_SLANT":
                    font.setStyle(QtGui.QFont.Style.StyleOblique)
                elif arg == "FONTSTYLE_NORMAL":
                    font.setStyle(QtGui.QFont.Style.StyleNormal)
                   
                self.setCurrentFont(font)
                     
            else:
                1 / 0
        except Exception as msg:
            print("ERROR: %s" % str(msg))
            raise

    def pause(self, onoff):
        '''
        '''
        self.olog.onhold = onoff

    def get_selected_lineinfo(self, pos):
        '''
        '''
        text = self.toPlainText()

        cursor = self.textCursor()

        cursor = self.cursorForPosition(pos)
        position = cursor.position()
        cursor.setPosition(position)
        self.setTextCursor(cursor)

        lines = text.split('\n')

        lineBoundsList = []
        totallen = 0

        for line in lines:
            xlen = len(line)
            lineBoundsList.append( (totallen, totallen + xlen))
            totallen += (xlen + 1)

        xline = ""
        line_no = 0
        # Get the line
        for len1, len2 in lineBoundsList:
            if len1 <= position and position <= len2:
                xline = lines[line_no]
                break
            line_no += 1

        return (lines, xline, len1, len2, line_no)

    def show_file(self, file, line_no=1):
        '''
        '''
        print("show_file: %s %s" % (file, line_no))

        app = QtCore.QCoreApplication.instance()
        mainwindow = app.mainwindow
    
        FILES_BROWSERS_TABS = mainwindow.ui.FILES_BROWSERS_TABS

        # ------------------------------------------------------
        def check_has_page(file):
            for idx in range(FILES_BROWSERS_TABS.count()):
                if FILES_BROWSERS_TABS.tabText(idx) == file:
                    return idx
            # not found
            return -1
        # ------------------------------------------------------

        page_idx = check_has_page(file)
        
        if page_idx == -1:
            # add page
            w = QtWidgets.QWidget(FILES_BROWSERS_TABS)
            FILES_BROWSERS_TABS.addTab(w, file)
            FILES_BROWSERS_TABS.setCurrentWidget(w)
            
            text_widget = PythonCodeAnalysersApp_TextEditor.LNTextEdit(w, FILES_BROWSERS_TABS, file)
            w.text_widget = text_widget # for later usage
        else:
            # show page
            FILES_BROWSERS_TABS.setCurrentIndex(page_idx)
            w = FILES_BROWSERS_TABS.currentWidget()
            
        # go to line
        self.goto_line(w.text_widget, line_no-1)
            
    def goto_line(self, text_edit, line_no, select=False):
        '''
        '''
        if hasattr(text_edit, "edit"):
            
            text_document = text_edit.edit.document()
            text_block = QtGui.QTextBlock(text_document.findBlockByLineNumber(line_no))
     
            text_cursor = QtGui.QTextCursor(text_edit.edit.textCursor())
            text_cursor.setPosition(text_block.position())    
            text_edit.edit.setFocus()
            text_edit.edit.setTextCursor(text_cursor)
        
            if select:
                text_cursor.select(QtGui.QTextCursor.BlockUnderCursor)
                
        else:
   
            text_document = text_edit.document()
            text_block = QtGui.QTextBlock(text_document.findBlockByLineNumber(line_no))
     
            text_cursor = QtGui.QTextCursor(text_edit.textCursor())
            text_cursor.setPosition(text_block.position())    
            text_edit.setFocus()
            text_edit.setTextCursor(text_cursor)
        
            if select:
                text_cursor.select(QtGui.QTextCursor.BlockUnderCursor)
            
       
                        
