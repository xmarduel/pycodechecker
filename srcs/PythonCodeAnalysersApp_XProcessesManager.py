
'''
COPYRIGHT (C) XAM GmbH

MODULE DESCRIPTION:
    The manager for all processes created and their output to the loggers
'''

import time
import threading

from PySide2 import QtWidgets
from PySide2 import QtCore
from PySide2 import QtGui

import PythonCodeAnalysersApp_PyLintOutputStyler
import PythonCodeAnalysersApp_PyFlakesOutputStyler
import PythonCodeAnalysersApp_PyMetricsOutputStyler

import PythonCodeAnalysersApp_LoggingQueue


HANDLED_IN_VIEW     = 0
NOT_HANDLED_IN_VIEW = 1


class LoggerViewsSetup(threading.Thread):
    '''
    Example:
        for a logview (a QTextCtrl), a whole bunch of job can write into the view
        
        but infact, the output of the job is put in a "log queue".
        
        to display the content of the "log queue", the queue must be "attached" to the view
        
        the queue is "detached" from the view when the process ends. Then the log queue of the
        next job is attached to the view and so on until all the jobs' log queue are processed
        
        Note that the jobs can be finished in any order (because of multiprocessing, pool of size > 1):
            job1  FINISHED  -> log queue fully read and displayed in the view
            job2  RUNNING   -> log queue is being filled by the process, being displayed in the view in real time
            job3  FINISHED  -> log queue full, process FINISHED, not yet displayed in the view
            job4  FINISHED  -> log queue full, process FINISHED, not yet displayed in the view
            job5  RUNNING   -> log queue is being filled by the process, not yet displayed in the view
    '''
    def __init__(self, processesRunner):
        ''' '''
        threading.Thread.__init__(self)

        self.processesRunner = processesRunner

    def run(self):
        '''
        must handle all the queues of all the jobs in the processesRunner for this tool
        '''
        while True:
            self.processesRunner.AssignLoggingQueuesToLoggerViews()
            time.sleep(0.1)
            
            if self.processesRunner.IsFinished():
                # last log
                try:
                    self.processesRunner.parent_widget.FinishLog()
                    self.processesRunner = None
                except Exception as msg:
                    a = str(msg)
    
    
class ProcessesRunner:
    '''
    '''
    def __init__(self, jobList, poolsize):
        '''
        '''
        self.parent_widget = None
        # list of XProcesses that are run/are running and which output need to be logged/are beeing logged
        self.logging_processes = {
            "-shell-"   : [],
            "PyLint"    : [],
            "PyFlakes"  : [],
            "PyMetrics" : [],
        }

        self.jobList = jobList

        self.ProcessPool = ProcessPool(poolsize)
        self.ProcessPool.SetProcessesRunner(self)

        self.nb_processes_started = 0
        
    def set_parent_widget(self, parent_widget):
        '''
        Parameter:
            - parent_widget: a widget
            
        Description:
           - set the qt widget parent. It it needed so that a when a qprocess ended, an event is sent to the widget_parent
        '''
        self.parent_widget = parent_widget
        
    def start_run(self):
        '''
        
        Description:
            - starts <poolsize> processes at the beginning of the "run"
        '''
        for k in range(self.ProcessPool.size):
            self.continue_run()

    def continue_run(self):
        '''
        Description:
            - start a new process. A free slot in the pool should be available.
            
        Exceptions:
            - raise an exception when jobList is empty
        '''
        # start the next process
        idx = self.ProcessPool.GetFreeSlotIndex()
        self.nb_processes_started += 1
        try:
            job = self.jobList.pop(0)
            self.ProcessPool.ActivateJob(self.nb_processes_started, job, idx)
        except IndexError as msg:
            print("finished")
        except Exception as msg:
            raise
        
    def GetXProcess(self, process):
        '''
        Parameter:
            - process: a qt process
            
        Description:
            - get the XProcess instance of a process which pid is <pid>
            The process should be in the list of running processes "self.logging_processes['-shell-']"
        '''
        pp = [ xprocess for xprocess in self.logging_processes['-shell-'] if xprocess.process == process ]
        if pp:
            return pp[0]
        else:
            return None
        #return filter( lambda x: x.process == process, self.logging_processes['-shell-'] )[0]
    
    def ParseRunningProcesses(self):
        '''
        Description:
            - parse the output of the processes being actually run (i.e. those in the pool)
            - assign logging queues to the logger views
            
        called for wx processes on the OnTimer of the main window
        '''
        for xprocess in self.ProcessPool.Slots:
            if xprocess and xprocess.process:
                xprocess.ProcessOutput()
    
    def AssignLoggingQueuesToLoggerViews(self):
        '''
        Description:
            - catch the first process which queues status are NOT_HANDLED_IN_VIEW,
            set their status to HANDLED_IN_VIEW and assign them to the related view
            
        Note:
            - a process is removed from the list "self.logging_processes"  when it is finished (wx.process is None)
            and its logging queues are empty and were "in use".
        '''
        for xprocess in self.logging_processes['-shell-']:
            if xprocess.process is None and xprocess.loggingqueues_status['-shell-'] == HANDLED_IN_VIEW and xprocess.logging_queues['-shell-'].empty():
                self.logging_processes['-shell-'].remove(xprocess)  # removed "used" queues of finished processes
                break

        for xprocess in self.logging_processes['-shell-']:
            if xprocess.loggingqueues_status['-shell-'] == HANDLED_IN_VIEW:
                break
            if xprocess.loggingqueues_status['-shell-'] == NOT_HANDLED_IN_VIEW:
                xprocess.loggingqueues_status['-shell-'] = HANDLED_IN_VIEW
                self.parent_widget.loggerviews['-shell-'].set_logging_queue(xprocess.logging_queues['-shell-'])
                #print "%s shell queue in use ..." % xprocess
                break


        for tool in self.logging_processes:
            if tool == '-shell-':
                continue
            for xprocess in self.logging_processes[tool]:
                if xprocess.process is None and xprocess.loggingqueues_status[tool] == HANDLED_IN_VIEW and xprocess.logging_queues[tool].empty():
                    self.logging_processes[tool].remove(xprocess)  # removed "used" queues of finished processes
                    break

        for tool in self.logging_processes:
            if tool == '-shell-':
                continue
            for xprocess in self.logging_processes[tool]:
                if xprocess.loggingqueues_status[tool] == HANDLED_IN_VIEW:
                    break
                if xprocess.loggingqueues_status[tool] == NOT_HANDLED_IN_VIEW:
                    xprocess.loggingqueues_status[tool] = HANDLED_IN_VIEW
                    self.parent_widget.loggerviews[tool].set_logging_queue(xprocess.logging_queues[tool])
                    #print "%s tool queue in use ..." % xprocess
                    break
            
    def IsFinished(self):
        '''
        Description:
            - the processesRunner is finished when a all jobs are run AND all logging_processes are done
        '''
        if self.jobList == [] :
            for tool in self.logging_processes:
                if self.logging_processes[tool]:
                    return False
            return True
        else:
            return False
        
    def AbortedShellLogs(self):
        '''
        '''
        for xprocess in self.ProcessPool.Slots:
            if xprocess is not None:
                xprocess.AbortedShellLog()

    def StopAnalysers(self):
        '''
        '''
        self.AbortedShellLogs()

        self.jobList = []
        for k in range(self.ProcessPool.size):
            if self.ProcessPool.Slots[k] and self.ProcessPool.Slots[k].process:
                self.ProcessPool.Slots[k].process.kill() # kill a qt process
                
    def HandleProcessTermination(self, process):
        '''
        called from "cb_timer" for qt processes
        '''         
        xprocess = self.GetXProcess(process)

        #print "%s ENDED..." % xprocess
                
        xprocess.ProcessOutput()
        xprocess.process.kill()
        
        exCode = xprocess.process.exitCode() 
        
        xprocess.process = None
                
        # free slot occupied by this process
        xprocess.pool.FreeSlot(xprocess.pool_idx)
            
        xprocess.FinishLog(exCode)
        xprocess.FinishedShellLog(exCode)

        if not self.parent_widget.stop_processes:
            # the next one
            self.continue_run()


class ProcessPool:
    '''
    '''
    def __init__(self, size):
        self.processesRunner = None
        self.size    = size
        self.Slots   = [ None ] * size
        
    def SetProcessesRunner(self, processesRunner):
        '''
        '''
        self.processesRunner = processesRunner
    
    def ActivateJob(self, k, jobInfo, idx):
        '''
        '''
        self.Slots[idx] = XProcess(jobInfo, self, idx)
        
    def HasFreeSlot(self):
        '''
        '''
        return None in self.Slots
    
    def GetFreeSlotIndex(self):
        '''
        '''
        for k, process in enumerate(self.Slots):
            if process is None:
                return k
        return -1
    
    def FreeSlot(self, idx):
        '''
        '''
        self.Slots[idx] = None


class XProcess:
    '''
    A structure containing
        - a QProcess
        - the process "pid"
        
        - the "logging queue" where the process output is stored
        - ...
        
        - a pointer to the ProcessPool
        - it place (idx) in the ProcessPool
        
    '''
    def  __init__(self, jobInfo, pool, pool_idx):
        '''
        '''
        main_window = pool.processesRunner.parent_widget
        
        self.stylers = {
            'PyLint'    : PythonCodeAnalysersApp_PyLintOutputStyler.PyLintOutputStyler(main_window.dlg_toolsoutputconfig_editor),
            'PyFlakes'  : PythonCodeAnalysersApp_PyFlakesOutputStyler.PyFlakesOutputStyler(main_window.dlg_toolsoutputconfig_editor, main_window.dlg_toolsconfig_editor),
            'PyMetrics' : PythonCodeAnalysersApp_PyMetricsOutputStyler.PyMetricsOutputStyler(main_window.dlg_toolsoutputconfig_editor),
        }
            
        self.jobInfo = jobInfo  # a dictionary with keys "tool", "analyserExe", "analyserOpt" and "file"

        self.pool     = pool
        self.pool_idx = pool_idx  # position in the pool

        self.tool = jobInfo['tool']
        self.cmdl = jobInfo['analyserExe'] + " " + jobInfo['analyserOpt'] + " " + jobInfo['file']
        self.file = jobInfo['file']

        self.starttime = time.time()
        self.totaltime = ""

        self.process = QtCore.QProcess(pool.processesRunner.parent_widget)
        self.process.finished.connect(pool.processesRunner.parent_widget.cb_process_end)
            
        self.outs = ''
        self.errs = ''

        self.pid = 0
        self.returncode = 0
        
        self.errs_rest_line = ''
        self.outs_rest_line = ''

        self.logging_queues = {
            self.tool : PythonCodeAnalysersApp_LoggingQueue.LoggingQueue(),  # the process writes on this queue
            '-shell-' : PythonCodeAnalysersApp_LoggingQueue.LoggingQueue(),  # the app writes on this queue
        }

        self.loggingqueues_status = {
            self.tool : NOT_HANDLED_IN_VIEW,  # or HANDLED_IN_VIEW
            '-shell-' : NOT_HANDLED_IN_VIEW,  # or HANDLED_IN_VIEW
        }

        self.StartShellLog()
        self.StartLog()

        # this process is now logging (it its queues)
        self.pool.processesRunner.logging_processes['-shell-'].append( self )
        self.pool.processesRunner.logging_processes[self.tool].append( self )

        self.Execute()
    
    def SetLoggingQueueStatus(self, status):
        '''
        '''
        self.loggingqueues_status[self.tool] = status
        self.loggingqueues_status['-shell-'] = status
    
    def HandleTermination(self):
        '''
        '''
        self.pool.processesRunner.HandleProcessTermination(self.pid, self.returncode)

    def Execute(self):
        '''
        ''' 
        retval = self.process.start(self.cmdl)

        if 1:
            self.pid = -1
            
            #self.outs = self.process.readAllStandardOutput()
            #self.errs = self.process.readAllStandardError()
            
        else:
            self.pid = 0
            self.logging_queues['-shell-'].SetLineFontColor('red')
            self.logging_queues['-shell-'].AppendText("failed to start process : %s" % self.cmdl)
            #self.process.Destroy()
            self.process = None
            
            self.outs = None
            self.errs = None
            
        #print "%s STARTED..." % self

    def StartShellLog(self):
        '''
        '''
        self.logging_queues['-shell-'].SetLineFontColor('blue')
        self.logging_queues['-shell-'].SetLineFontWeight("FONTWEIGHT_NORMAL")
        self.logging_queues['-shell-'].AppendText("\t analyser is : %s   for file %s...  - " % (self.tool, self.file) )

    def FinishedShellLog(self, exCode):
        '''
        '''
        shelltext = " Exitcode: %d (Time: %.2f[s])" % (exCode, self.totaltime)

        # different color on same line
        colorMap = { 0: 'blue'} # and red if exCode != 0
        self.logging_queues['-shell-'].InsertColoredText(shelltext, colorMap.get(exCode, 'red'))
        
    def AbortedShellLog(self):
        '''
        '''
        self.logging_queues['-shell-'].SetLineFontColor('red')
        self.logging_queues['-shell-'].SetLineFontWeight("FONTWEIGHT_NORMAL")
        self.logging_queues['-shell-'].InsertText(" ... aborting the current analyser and exit \n")

    def StartLog(self):
        '''
        '''
        self.logging_queues[self.tool].InitLogging(self.tool)
        self.logging_queues[self.tool].AppendText(self.cmdl + '\n')
        self.logging_queues[self.tool].StartLogging(self.tool, self.file)
        
    def FinishLog(self, exCode):
        '''
        '''
        self.totaltime =  time.time() - self.starttime

        loggertext = "\n%s Done - Exitcode: %d (Time: %.2f[s])" % (self.tool, exCode, self.totaltime)
        self.logging_queues[self.tool].SetLineFontFamily("FONTFAMILY_DEFAULT")
        self.logging_queues[self.tool].SetLineFontColor('blue')
        self.logging_queues[self.tool].AppendText(loggertext)
                
    def GetOutput(self):
        '''
        Description:
            get stdout/stderr of a subprocess instance
        '''  
        outs = self.process.readAllStandardOutput()
        errs = self.process.readAllStandardError()
               
        return (errs, outs)
        
    def ProcessOutput(self):
        '''
        '''
        def print_errs(errs_lines, unfinished_last_line=False):
            ''' '''
            if unfinished_last_line:
                # do not print it in this run ...
                errs_rest_line = errs_lines[-1]
                errs_lines = errs_lines[:-1]
            else:
                errs_rest_line = ''
            
            for line in errs_lines: 
                    
                if line == '\xff':
                    continue

                # append if some rest was there
                if self.errs_rest_line:
                    line = self.errs_rest_line + line
                    self.errs_rest_line = ''

                if self.stylers[self.tool].IgnoreErrorLine(line):
                    continue

                color  = self.stylers[self.tool].ProcessOutputGetLineColor(line)
                family = self.stylers[self.tool].ProcessOutputGetLineFamily(line)
                style  = self.stylers[self.tool].ProcessOutputGetLineStyle(line)
                weight = self.stylers[self.tool].ProcessOutputGetLineWeight(line)

                self.logging_queues[self.tool].SetLineFontColor(color)
                self.logging_queues[self.tool].SetLineFontFamily(family)
                self.logging_queues[self.tool].SetLineFontStyle(style)
                self.logging_queues[self.tool].SetLineFontWeight(weight)

                self.logging_queues[self.tool].AppendText(line)
                
            # ... but at the next run
            self.errs_rest_line = errs_rest_line
 
        def print_outs(outs_lines, unfinished_last_line=False):
            ''' '''
            if unfinished_last_line:
                # do not print it in this run ...
                outs_rest_line = outs_lines[-1]
                outs_lines = outs_lines[:-1]
            else:
                outs_rest_line = ''
                    
            for line in outs_lines:
                   
                if line == '\xff':
                    continue

                # append if some rest was there
                if self.outs_rest_line:
                    line = self.outs_rest_line + line
                    self.outs_rest_line = ''

                if self.stylers[self.tool].IgnoreOutputLine(line):
                    continue

                color  = self.stylers[self.tool].ProcessOutputGetLineColor(line)
                family = self.stylers[self.tool].ProcessOutputGetLineFamily(line)
                style  = self.stylers[self.tool].ProcessOutputGetLineStyle(line)
                weight = self.stylers[self.tool].ProcessOutputGetLineWeight(line)

                self.logging_queues[self.tool].SetLineFontColor(color)
                self.logging_queues[self.tool].SetLineFontFamily(family)
                self.logging_queues[self.tool].SetLineFontStyle(style)
                self.logging_queues[self.tool].SetLineFontWeight(weight)

                # windows
                if line[-1] == '\r':
                    line = line[0:-1]

                self.logging_queues[self.tool].AppendText(line)
                
            # ... but at the next run
            self.outs_rest_line = outs_rest_line

        # --------------------------------------------------------------------
        # --------------------------------------------------------------------

        errs, outs = self.GetOutput()  # QByteArray
            
        errs = errs.data().decode('utf-8')
        outs = outs.data().decode('utf-8')
        
        if errs:
            errs_lines = errs.split('\n')
            
            if errs[-1] == '\n':
                errs_lines = errs_lines[:-1]
                unfinished_last_line = False
            else:
                unfinished_last_line = True
                    
            print_errs(errs_lines, unfinished_last_line)

        if outs:
        
            outs_lines = outs.split('\n')
            
            if outs[-1] == '\n':
                outs_lines = outs_lines[:-1]
                unfinished_last_line = False
            else:
                unfinished_last_line = True
                
            print_outs(outs_lines, unfinished_last_line)
            
