
'''
COPYRIGHT (C) XAM GmbH

MODULE DESCRIPTION:
    The Main Application.
'''

import os
import sys
import time
import argparse
import platform
import functools

from PySide2 import QtCore
from PySide2 import QtWidgets

from PySide2.QtUiTools import QUiLoader
from PySide2 import QtUiTools

import PythonCodeAnalysersAppSettingsDialog
import PythonCodeAnalysersToolsConfigDialog
import PythonCodeAnalysersToolsOutputConfigDialog

import PythonCodeAnalysersApp_LoggingQueue
import PythonCodeAnalysersApp_XProcessesManager

import PythonCodeAnalysersApp_GenericToolLogger


class MainWindow(QtWidgets.QMainWindow):
    '''
    '''
    def __init__(self, options):
        '''
        '''
        super(MainWindow, self).__init__()
 
        if platform.system() == 'Windows':
            self.settings_file = "C:\\PYTHON_TOOLS\\pycodechecker\\srcs\\myapp.ini"
        else:
            self.settings_file = "/Users/xavier/PYTHON_TOOLS/pycodechecker/srcs/myapp.ini"
        
        self.ui = self.loadUi("PythonCodeAnalysersUI.ui")

        # special widgets on toolbars
        self.ui.CHOICE_FILES_DATASET = QtWidgets.QComboBox()
        self.ui.CHOICE_FILES_DATASET.setToolTip("Select File DataSet")
        self.ui.TOOLBAR.insertWidget(self.ui.DUMMY_CHOICE_FILES_DATASET, self.ui.CHOICE_FILES_DATASET)
        
        self.ui.CHOICE_NB_PROCESSES = QtWidgets.QSpinBox()
        self.ui.CHOICE_NB_PROCESSES.setToolTip("Select Nb. Parallel Processes")
        self.ui.TOOLBAR.insertWidget(self.ui.DUMMY_CHOICE_NB_PROCESSES, self.ui.CHOICE_NB_PROCESSES)
        self.ui.CHOICE_NB_PROCESSES.setValue(1)
        
        self.ui.TOOLBAR.removeAction(self.ui.DUMMY_CHOICE_FILES_DATASET)
        self.ui.TOOLBAR.removeAction(self.ui.DUMMY_CHOICE_NB_PROCESSES)
        
        # ui restore
        self.read_settings()
        
        # setup callbacks
        self.ui.TOOLS_CONFIGURATIONS.triggered.connect(self.on_tools_configuration)
        self.ui.TOOLS_OUTPUT_CONFIGURATIONS.triggered.connect(self.on_tools_output_configuration)
        self.ui.FILEINFOSET_EDITOR.triggered.connect(self.on_fileinfoset_editor)
        
        self.dlg_toolsconfig_editor       = PythonCodeAnalysersToolsConfigDialog.ConfigDialog(self)
        self.dlg_toolsoutputconfig_editor = PythonCodeAnalysersToolsOutputConfigDialog.ConfigDialog(self)
        self.dlg_fileinfoset_editor       = PythonCodeAnalysersAppSettingsDialog.ConfigDialog(self)
        
        self.dlg_toolsconfig_editor.hide()
        self.dlg_toolsoutputconfig_editor.hide()
        self.dlg_fileinfoset_editor.hide()
        
        # setup toolbar action callbacks
        self.ui.RUN_TOOLS_ACTION.triggered.connect(self.run_tools_action)
        self.ui.STOP_TOOLS_ACTION.triggered.connect(self.stop_tools_action)
        
        self.ui.ABOUT_ACTION.triggered.connect(self.cb_about)
        self.ui.HELP_ACTION.triggered.connect(self.cb_help)
        
        self.ui.BTN_CLEAR_LOGGERS.clicked.connect(self.cb_clear_loggers)
        self.ui.BTN_PAUSE_LOGGERS.clicked.connect(self.cb_playpause_loggers)
        self.ui.BTN_SAVE_LOGGERS_AS_TEXT.clicked.connect(self.cb_save_loggers_to_text)
        self.ui.BTN_SAVE_LOGGERS_AS_HTML.clicked.connect(self.cb_save_loggers_to_html)

        self.ui.FILES_BROWSERS_TABS.setTabsClosable(True)
        self.ui.FILES_BROWSERS_TABS.tabCloseRequested.connect(self.fileTabCloseRequested)
        self.ui.FILES_BROWSERS_TABS.removeTab(1) # the dummy one
        
        # needed for compiling
        self.stop_processes = False
        self.processesRunner = None

        self.joblist = []

        self.tools = ('PyLint', 'PyFlakes', 'PyCodeStyle', 'PyMetrics')

        self.loggerviews = {
            '-shell-'   : self.ui.PROCESSES_LOGGER,
            'PyLint'    : self.ui.TOOL_PYLINT_LOGGER_VIEW,
            'PyFlakes'  : self.ui.TOOL_PYFLAKES_LOGGER_VIEW,
            'PyMetrics' : self.ui.TOOL_PYMETRICS_LOGGER_VIEW,
        }

        self.loggingqueues = {
            '-shell-'   : PythonCodeAnalysersApp_LoggingQueue.LoggingQueue(),
            'PyLint'    : PythonCodeAnalysersApp_LoggingQueue.LoggingQueue(),
            'PyFlakes'  : PythonCodeAnalysersApp_LoggingQueue.LoggingQueue(),
            'PyMetrics' : PythonCodeAnalysersApp_LoggingQueue.LoggingQueue(),
        }
        

        self.starttime = 0
        # create the timer - to read the processes outputs
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.cb_timer) 
        
        self.timer.start()

        self.enable_run_analyser_button(True)
        self.enable_stop_analyser_button(False)
        self.enable_pause_analyser_button(False)

    #-------------------------------------------------------------------------
    
    def closeEvent(self, event):
        ''' '''
        self.write_settings()
    
    def fileTabCloseRequested(self, index):
        ''' '''
        self.ui.FILES_BROWSERS_TABS.removeTab(index)

    #-------------------------------------------------------------------------
    
    def on_fileinfoset_editor(self):
        '''
        '''
        self.dlg_fileinfoset_editor.show()
        self.dlg_fileinfoset_editor.set_current_infoset(self.ui.CHOICE_FILES_DATASET.currentText())
        
    def on_tools_configuration(self):
        '''
        '''
        self.dlg_toolsconfig_editor.show()
        
    def on_tools_output_configuration(self):
        '''
        '''
        self.dlg_toolsoutputconfig_editor.show()

    def read_settings(self):
        '''
        '''
        self.settings = settings = QtCore.QSettings(self.settings_file, QtCore.QSettings.IniFormat)
        
        settings.beginGroup("mainWindow")
        self.restoreGeometry(settings.value("geometry"))
        self.ui.MAIN_SPLITTER.restoreState(settings.value("MAIN_SPLITTER"))
        settings.endGroup()
        
        settings.beginGroup("toolbar")
        if settings.value("PYLINT") == 'true': 
            self.ui.PYLINT_ACTION.toggle()
        if settings.value("PYFLAKES") == 'true': 
            self.ui.PYFLAKES_ACTION.toggle()
        if settings.value("PYMETRICS") == 'true': 
            self.ui.PYMETRICS_ACTION.toggle()
            
        all_items = settings.value("FILES_DATASET_ITEMS")
        all_items = all_items.split(",")
        for item in all_items:
            self.ui.CHOICE_FILES_DATASET.addItem(item)
        curr_text = settings.value("FILES_DATASET_VALUE")
        curr_idx = all_items.index(curr_text)
            
        self.ui.CHOICE_FILES_DATASET.setCurrentIndex(curr_idx)
            
        nb = int(settings.value("NB_PROCESSES"))
        self.ui.CHOICE_NB_PROCESSES.setValue(nb)
        settings.endGroup()
        
        settings.beginGroup("loggers_notebook")
        nb = int(settings.value("TOOLS_LOGGERS_TAB"))
        self.ui.TOOLS_LOGGERS_TAB.setCurrentIndex(nb)
        settings.endGroup()
    
    def write_settings(self):
        '''
        '''
        settings = QtCore.QSettings(self.settings_file, QtCore.QSettings.IniFormat)
    
        settings.clear()
    
        settings.beginGroup("mainWindow")
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("MAIN_SPLITTER", self.ui.MAIN_SPLITTER.saveState())
        settings.endGroup()
        
        settings.beginGroup("toolbar")
        settings.setValue("PYLINT", self.ui.PYLINT_ACTION.isChecked())
        settings.setValue("PYFLAKES", self.ui.PYFLAKES_ACTION.isChecked())
        settings.setValue("PYMETRICS", self.ui.PYMETRICS_ACTION.isChecked())
        
        all_items = [self.ui.CHOICE_FILES_DATASET.itemText(i) for i in range(self.ui.CHOICE_FILES_DATASET.count())]
        all_items = ",".join(all_items)
        settings.setValue("FILES_DATASET_ITEMS", all_items)
        settings.setValue("FILES_DATASET_VALUE", self.ui.CHOICE_FILES_DATASET.currentText())
                          
        settings.setValue("NB_PROCESSES", self.ui.CHOICE_NB_PROCESSES.value())
        settings.endGroup()
        
        settings.beginGroup("loggers_notebook")
        settings.setValue("TOOLS_LOGGERS_TAB", self.ui.TOOLS_LOGGERS_TAB.currentIndex())
        settings.endGroup()
        
        # settings for the dialogs
        self.dlg_toolsconfig_editor.write_settings(settings)
        self.dlg_toolsoutputconfig_editor.write_settings(settings)
        self.dlg_fileinfoset_editor.write_settings(settings)
        
    def run_tools_action(self):
        '''
        '''
        analysersList = []
        filesList = []

        if self.PYLINT_ACTION.isChecked():       analysersList.append('PyLint')
        if self.PYFLAKES_ACTION.isChecked():     analysersList.append('PyFlakes')
        if self.PYMETRICS_ACTION.isChecked():    analysersList.append('PyMetrics')

        if analysersList == []:
            # error message
            ret = QtWidgets.QMessageBox.warning(self, "Python Code Analyser", "No Analyser selected", QtWidgets.QMessageBox.Ok)
            return
        
        # sort the AnalysersList following the "run_order" settings
        ###################################################################
        def tools_ordering(x, y):
            '''
            compare function passed to "sort" method of a list
            '''
            PYLINT_ORDER    = self.dlg_fileinfoset_editor.TOOL_PYLINT_RUN_ORDER.value()
            PYFLAKES_ORDER  = self.dlg_fileinfoset_editor.TOOL_PYFLAKES_RUN_ORDER.value()
            PYMETRICS_ORDER = self.dlg_fileinfoset_editor.TOOL_PYMETRICS_RUN_ORDER.value()

            dd = { 'PyLint'    : PYLINT_ORDER ,
                   'PyFlakes'  : PYFLAKES_ORDER,
                   'PyMetrics' : PYMETRICS_ORDER,
            }

            if dd[x] > dd[y] :
                return 1
            elif dd[x] < dd[y]:
                return -1
            else:
                return 0
        ####################################################################
        #analysersList.sort(cmp=tools_ordering)
        analysersList.sort(key=functools.cmp_to_key(tools_ordering))

        NBSLOTS_PROCESSES = self.ui.CHOICE_NB_PROCESSES.value()
        ACTIVE_FILESINFOSET  = self.ui.CHOICE_FILES_DATASET.currentText()

        filesinfoset = self.dlg_fileinfoset_editor.get_infoset_data(ACTIVE_FILESINFOSET)
        
        if filesinfoset:
            filesList = filesinfoset.get_selected_paths()
        else:
            filesList = []

        if filesList == []:
            # error message
            ret = QtWidgets.QMessageBox.warning(self, "Python Code Analyser", "No infoset/files selected", QtWidgets.QMessageBox.Ok)
            return
    
        analysersExe = {
            'PyLint'    : self.get_tool_executable_path('PyLint'),
            'PyFlakes'  : self.get_tool_executable_path('PyFlakes'),
            'PyMetrics' : self.get_tool_executable_path('PyMetrics'),
        }
    
        analysersOpt = {
            'PyLint'    : self.dlg_toolsconfig_editor.get_command_options("pylint"),
            'PyFlakes'  : self.dlg_toolsconfig_editor.get_command_options("pyflakes"),
            'PyMetrics' : self.dlg_toolsconfig_editor.get_command_options("pymetrics"),
        }
         
        first_pymetrics_run = True
        #########################################################################
        # a small hack for PyMetrics so that the db of token is not overwriten at each process run
        def fix_pymetrics_cmdlineopts(first_pymetrics_run, analyserOpt):
            if first_pymetrics_run == False and '--noold' in analyserOpt :  # remove option -noold for the next run of PyMetrics
                analyserOptAsList = analyserOpt.split()
                analyserOptAsList.remove("--noold")
                return " ".join(analyserOptAsList)
            else:
                return analyserOpt
        #########################################################################
    
        # and build the jobList
        self.joblist = []
        # FILE_PER_FILE or TOOL_PER_TOOL ?
        if self.dlg_fileinfoset_editor.RB_FILE_PER_FILE.isChecked(): # FILE_PER_FILE
            for afile in filesList :
                for tool in analysersList:
                    analyserExe = analysersExe[tool]
                    analyserOpt = analysersOpt[tool]
                    
                    if tool == 'PyMetrics':
                        analyserOpt = fix_pymetrics_cmdlineopts(first_pymetrics_run, analyserOpt)
                        
                    self.joblist.append( {'tool':tool, 'analyserExe':analyserExe, 'analyserOpt':analyserOpt, 'file':afile} )
                    
                    if tool == 'PyMetrics':
                        first_pymetrics_run = False
                        
        else:  # TOOL_PER_TOOL
            for tool in analysersList:
                analyserExe = analysersExe[tool]
                analyserOpt = analysersOpt[tool]
                        
                for afile in filesList[:1] :
                    self.joblist.append( {'tool':tool, 'analyserExe':analyserExe, 'analyserOpt':analyserOpt, 'file':afile} )
                    
                if tool == 'PyMetrics':
                    first_pymetrics_run = False
                    analyserOpt = fix_pymetrics_cmdlineopts(first_pymetrics_run, analyserOpt)
                    
                for afile in filesList[1:] :
                    self.joblist.append( {'tool':tool, 'analyserExe':analyserExe, 'analyserOpt':analyserOpt, 'file':afile} )

        self.stop_processes = False

        self.starttime = time.time()

        self.enable_run_analyser_button(False)
        self.enable_stop_analyser_button(True)
        self.enable_pause_analyser_button(True)
        
        # start logging
        queue = PythonCodeAnalysersApp_LoggingQueue.LoggingQueue()
        queue.SetLineFontColor('blue')
        queue.SetLineFontWeight("FONTWEIGHT_NORMAL")
        queue.AppendText("OnStartAnalysers...")
        self.loggerviews['-shell-'].set_logging_queue(queue)
        self.loggerviews['-shell-'].flush_logging_queue()

        #return

        # process analysers
        self.processesRunner = PythonCodeAnalysersApp_XProcessesManager.ProcessesRunner(self.joblist, poolsize=NBSLOTS_PROCESSES)
        self.processesRunner.set_parent_widget(self)
        self.processesRunner.start_run()
         
    def stop_tools_action(self):
        '''
        '''
        if self.processesRunner:
            self.processesRunner.StopAnalysers()

        self.stop_processes = True
          
    def get_tool_executable_path(self, tool):
        '''
        '''
        PYTHONSCRIPTS = os.environ["PYTHONSCRIPTS"]
        PYTHONSCRIPTS = ""
        PYTHONEXEC    = os.environ["PYTHONEXEC"]

        if platform.system() == 'Windows':
            SCRIPT = tool
        else:  # 'Linux', 'Darwin', ...
            SCRIPT = tool.lower()

        analyserExe = "%s -m %s" % (PYTHONEXEC, os.path.join(PYTHONSCRIPTS, SCRIPT))

        return analyserExe

    def cb_help(self):
        '''
        '''
        import webbrowser
        filePath = os.path.join(os.environ['PYANALYSERS_HOME'], 'html', 'Documentation.html')
        webbrowser.open(filePath)

    def cb_about(self):
        '''
        display the current tools versions
        '''
        msg = ""
        for tool in self.tools:
            analyserExe = self.get_tool_executable_path(tool)
            cmdline = analyserExe + " --version"

            self.loggingqueues['-shell-'].SetLineFontColor('blue')
            self.loggingqueues['-shell-'].SetLineFontWeight("FONTWEIGHT_NORMAL")
            self.loggingqueues['-shell-'].AppendText("about: running \"" + cmdline + "\" ...\n")

            v = os.popen(cmdline + ' 2>&1')
            output = v.read()
            res = v.close()

            msg += "%s: \n" % tool
            if not res:
                msg += str(output)
            else:
                msg += cmdline
                msg += "\n"
                msg += "-failed to query-"
                msg += "\n%s\n" % output
            msg += "\n"

        # First we create and fill the info object
        info = """
        PythonCodeAnalysersApp   version 1.9.5
            
        (C) 2015 XAMSOFT"
        
        
Tested with:
============
        - PyLint 1.4.3 (astroid 1.3.6 common 0.61.0)
        - PyFlakes 2.1.0.1
        - PyMetrics 0.8.1 and 0.8.2.1


Running:
========
        %(running)s 

    """  % { "running": msg }
        

        # Then we call wx.AboutBox giving it that info object
        QtWidgets.QMessageBox.information(self, "PythonCodeAnalysersApp", info)
        
        self.loggerviews['-shell-'].set_logging_queue(self.loggingqueues['-shell-'])
        self.loggerviews['-shell-'].flush_logging_queue()

    # main menu callbacks-------------------------------------------------------

    def enable_run_analyser_button(self, value):
        '''
        '''
        self.ui.RUN_TOOLS_ACTION.setEnabled(value)

    def enable_pause_analyser_button(self, value):
        '''
        '''
        pass

    def enable_stop_analyser_button(self, value):
        '''
        '''
        self.ui.STOP_TOOLS_ACTION.setEnabled(value)

    def cb_process_end(self):
        '''
        callback on qt qprocess end
        '''
        p = self.sender()

        if self.processesRunner:
            self.processesRunner.HandleProcessTermination(p)

    def cb_timer(self):
        '''
        '''
        #print "tick..."
        if self.processesRunner:
            self.processesRunner.ParseRunningProcesses()
            self.processesRunner.AssignLoggingQueuesToLoggerViews()
 
            if self.processesRunner.IsFinished():
                # last log
                self.finish_log()
                self.processesRunner = None
                
    def finish_log(self):
        if self.stop_processes:
            self.aborted_analysers_shelllog()
        else:
            self.finished_analysers_shelllog()
    
    def finished_analysers_shelllog(self):
        '''
        '''
        dT = time.time() - self.starttime

        minutes = int(dT) / 60
        hours   = minutes / 60
        minutes = minutes - hours * 60
        seconds = dT - hours * 360 - minutes * 60

        queue = PythonCodeAnalysersApp_LoggingQueue.LoggingQueue()
        queue.SetLineFontColor('blue')
        queue.SetLineFontWeight("FONTWEIGHT_NORMAL")
        queue.AppendText("Analysers Finished! (Time: %.2f[s] = %d'%d''%.2fs.)\n" % (dT, hours, minutes, seconds) )
        self.loggerviews['-shell-'].set_logging_queue(queue)

        self.enable_run_analyser_button(True)
        self.enable_stop_analyser_button(False)
        self.enable_pause_analyser_button(False)
        
    def aborted_analysers_shelllog(self):
        '''
        '''
        dT = time.time() - self.starttime

        minutes = int(dT) / 60
        hours   = minutes / 60
        minutes = minutes - hours * 60
        seconds = dT - hours * 360 - minutes * 60

        queue = PythonCodeAnalysersApp_LoggingQueue.LoggingQueue()
        queue.SetLineFontColor('blue')
        queue.SetLineFontWeight("FONTWEIGHT_NORMAL")
        queue.AppendText("Analysers Aborted! (Time: %.2f[s]) = %d'%d''%.2fs.)\n" % (dT, hours, minutes, seconds) )
        self.loggerviews['-shell-'].set_logging_queue(queue)

        self.enable_run_analyser_button(True)
        self.enable_stop_analyser_button(False)
        self.enable_pause_analyser_button(False)

    def cb_clear_loggers(self):
        '''
        '''
        for loggerview in self.loggerviews.values():
            loggerview.clear()

    def cb_playpause_loggers(self):
        '''
        '''
        def pause():
            ''' '''
            for loggerview in self.loggerviews.values():
                loggerview.pause(1)
            
            self.ui.BTN_PAUSE_LOGGERS.setToolTip("Run Loggers")
    
        def play():
            ''' '''
            for loggerview in self.loggerviews.values():
                loggerview.pause(0)
        
            self.ui.BTN_PAUSE_LOGGERS.setToolTip("Pause Loggers")
        
        state = self.ui.BTN_PAUSE_LOGGERS.isChecked()
         
        if state == True :
            pause()
        else:
            play()
    
    def cb_save_loggers_to_text(self):
        '''
        '''
        xtime = time.gmtime()

        YYYY = '%o4d' % xtime[0]
        MO   = '%02d' % xtime[1]
        DD   = '%02d' % xtime[2]
        HH   = '%02d' % xtime[3]
        MM   = '%02d' % xtime[4]
        SS   = '%02d' % xtime[5]

        timestamp = YYYY + MO + DD + "_" + HH + MM + SS

        # create default filename & ask user
        defFile = "pycodeanalysers_%s.log" % timestamp
        defDir  = "/tmp/"
        try:
            if sys.platform == 'win32':
                defDir = os.environ['TEMP']
        except Exception as msg:
            msg = QtWidgets.QMessageBox.warning(self, "Please set the environment variable TEMP", 'PythonCodeAnalysers Error')
            defDir = "."

        # ??? cannot specify a file name ???
        #path, _  = QtWidgets.QFileDialog.getSaveFileName(self, caption="save to text", dir=defDir)

        #if not path :  # canceled
        #    return
        
        dlg = QtWidgets.QFileDialog(self)
        dlg.setFileMode( QtWidgets.QFileDialog.AnyFile )
        dlg.selectFile(defFile)
        dlg.setAcceptMode( QtWidgets.QFileDialog.AcceptSave )
        rc  = dlg.exec_()
        
        if not rc :  # canceled
            return

        path = dlg.selectedFiles()[0]

        if os.path.exists(path):
            os.remove(path)

        fp = open(path, "a+")
        fp.write("saving %s...\n\n" % self.__class__.__name__)
        
        # write to file
        for tool, loggerview in self.loggerviews.items():
            fp.write(loggerview.toPlainText())

        fp.write("\n\n")
        fp.close()
        
        # inform the user
        dlg = QtWidgets.QMessageBox.information(self, "Logger content saved in %s" % path, "Save Output")

    def cb_save_loggers_to_html(self):
        '''
        '''
        xtime = time.gmtime()

        YYYY = '%o4d' % xtime[0]
        MO   = '%02d' % xtime[1]
        DD   = '%02d' % xtime[2]
        HH   = '%02d' % xtime[3]
        MM   = '%02d' % xtime[4]
        SS   = '%02d' % xtime[5]

        timestamp = YYYY + MO + DD + "_" + HH + MM + SS

        # create default filename & ask user
        defFile = "pycodeanalysers_%s.html" % timestamp
        defDir  = "/tmp/"
        try:
            if sys.platform == 'win32':
                defDir = os.environ['TEMP']
        except Exception as msg:
            msg = QtWidgets.QMessageBox.warning(self, "Please set the environment variable TEMP", 'PythonCodeAnalysers Error')
            defDir = "."

        # ??? cannot specify a file name ???
        #path, _  = QtWidgets.QFileDialog.getSaveFileName(self, caption="save to html", dir=defDir)
        
        #if not path :  # canceled
        #    return
        
        dlg = QtWidgets.QFileDialog(self)
        dlg.setFileMode( QtWidgets.QFileDialog.AnyFile ) # also non existing file!
        dlg.selectFile(defFile)
        dlg.setAcceptMode( QtWidgets.QFileDialog.AcceptSave )
        rc  = dlg.exec_()
        
        if not rc:
            return
        
        path = dlg.selectedFiles()[0]
        

        if os.path.exists(path):
            os.remove(path)

        fp = open(path, "w")
        fp.write("<html><body>\n")
        # write to file
        for tool, loggerview in self.loggerviews.items():
            fp.write(loggerview.toHtml())
        fp.write("</body></html>\n")
        fp.close()
        
        # inform the user
        dlg = QtWidgets.QMessageBox.information(self, "Python Code Analyser", "Logger content saved in %s" % path, QtWidgets.QMessageBox.Ok)

    def loadUi(self, uifile):
        '''
        '''
        class UiLoader(QUiLoader):
            """
            Subclass :class:`~PySide.QtUiTools.QUiLoader` to create the user interface
            in a base instance.
        
            Unlike :class:`~PySide.QtUiTools.QUiLoader` itself this class does not
            create a new instance of the top-level widget, but creates the user
            interface in an existing instance of the top-level class.
        
            This mimics the behaviour of :func:`PyQt4.uic.loadUi`.
            """
        
            def __init__(self, baseinstance):
                """
                Create a loader for the given ``baseinstance``.
        
                The user interface is created in ``baseinstance``, which must be an
                instance of the top-level class in the user interface to load, or a
                subclass thereof.
        
                ``parent`` is the parent object of this loader.
                """
                QUiLoader.__init__(self, baseinstance)
                self.baseinstance = baseinstance
        
            def createWidget(self, class_name, parent=None, name=''):
                widget = None
                
                if parent is None and self.baseinstance:
                    # supposed to create the top-level widget, return the base instance
                    # instead
                    return self.baseinstance
                else:
                    if class_name in QtUiTools.QUiLoader.availableWidgets(self):
                        # create a new widget for child widgets
                        widget = QUiLoader.createWidget(self, class_name, parent, name)
                    else:
                        classes = {
                           'GenericToolLoggerView' : PythonCodeAnalysersApp_GenericToolLogger.GenericToolLoggerView
                        }
                        widget_class = classes.get(class_name, None)
        
                        if widget_class:
                            widget = widget_class(parent)
                        else:
                            pass
                            # raise KeyError("Unknown widget '%s'" % className)
                        # else:
                        #    raise AttributeError("Trying to load custom widget '%s', but base instance '%s' does not specify custom widgets." % (className, repr(self.baseinstance)))
        
                    if widget and self.baseinstance is not None:
                        # set an attribute for the new child widget on the base
                        # instance, just like PyQt4.uic.loadUi does.
                        setattr(self.baseinstance, name, widget)
                    
                    return widget
            
        loader = UiLoader(self)
        widget = loader.load(uifile)
        #QMetaObject.connectSlotsByName(widget)
        return widget 

# -------------------------------------------------------------------    
# -------------------------------------------------------------------    

def main():
    '''
    '''
    os.environ['PYTHONEXEC'] = "/Library/Frameworks/Python.framework/Versions/3.7/bin/python3"
    
    if platform.system() == 'Windows':
        os.environ['PYTHONSCRIPTS']  = os.path.join(os.environ['PYTHONEXEC'], 'Scripts')
    elif platform.system() == 'Linux':
        os.environ['PYTHONSCRIPTS']  = os.path.join(os.environ['PYTHONEXEC'], 'Scripts')
    elif platform.system() == 'Darwin':
        os.environ['PYTHONSCRIPTS']  = "/Library/Frameworks/Python.framework/Versions/3.7/bin"
    else:
        pass  
           
    parser = argparse.ArgumentParser()

    # options
    parser.add_argument("-d", "--debug", action="store_false", default=False, dest="debug", help="open with debug window")
    parser.add_argument("-F", "--config", default=None, dest="config", help="config file")

    options = parser.parse_args()

    app = QtWidgets.QApplication([])
    
    xMainWindow = MainWindow(options)
    app.mainwindow = xMainWindow

    xMainWindow.show()
    
    sys.exit(app.exec_())

# -------------------------------------------------------------------

if __name__ == '__main__':

    main()

# -------------------------------------------------------------------
