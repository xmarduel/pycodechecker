
'''
COPYRIGHT (C) XAM GmbH

MODULE DESCRIPTION:
    A queue that is filled with QTextEdit messages

    The QTextEdit has a pointer to the queue and is written from the data
    contained in the queue
'''

import queue

# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------

class LoggingQueue(queue.Queue):
    '''
    '''
    def __init__(self):
        '''
        '''
        queue.Queue.__init__(self)

    def LoggerActionAndArgs(self, action, args):
        '''
        Arguments:
            action: an unbounded method
            args: a tuple of arguments for the action
        '''
        self.put_nowait( (action, args) )  # allow the stop/restart the output

    def InitLogging(self, tool):
        '''
        '''
        self.SetLineFontColor('blue')
        self.SetLineFontFamily("FONTFAMILY_DEFAULT")
        self.SetLineFontWeight("FONTWEIGHT_NORMAL")
        self.AppendText("\n")
        self.AppendText("STARTING %s ..." % tool)

    def StartLogging(self, analyser, fileToAnalyse):
        '''
        '''
        if analyser == 'PyFlakes' :
            self.SetLineFontColor('black')
            self.SetLineFontWeight("FONTWEIGHT_BOLD")
            self.AppendText("=== File: %s ===\n" % fileToAnalyse)

    def AppendText(self, text):
        '''
        '''
        self.LoggerActionAndArgs("AppendText", text)
        
    def InsertText(self, text):
        '''
        '''
        self.LoggerActionAndArgs("InsertText", text)

    def SetLineFontColor(self, color):
        '''
        '''
        self.LoggerActionAndArgs("SetLineFontColor", color)

    def SetLineFontFamily(self, family):
        '''
        wx.FONTFAMILY_DEFAULT
        wx.FONTFAMILY_DECORATIVE
        wx.FONTFAMILY_ROMAN
        wx.FONTFAMILY_SCRIPT
        wx.FONTFAMILY_SWISS
        wx.FONTFAMILY_MODERN
        wx.FONTFAMILY_TELETYPE
        '''
        self.LoggerActionAndArgs("SetLineFontFamily", family)

    def SetLineFontStyle(self, style):
        '''
        wx.FONTSTYLE_NORMAL
        wx.FONTSTYLE_SLANT
        wx.FONTSTYLE_ITALIC
        '''
        self.LoggerActionAndArgs("SetLineFontStyle", style)

    def SetLineFontWeight(self, weight):
        '''
        wx.FONTWEIGHT_NORMAL
        wx.FONTWEIGHT_LIGHT
        wx.FONTWEIGHT_BOLD
        '''
        self.LoggerActionAndArgs("SetLineFontWeight", weight)
        
    def InsertColoredText(self, text, color):
        '''
        '''
        self.LoggerActionAndArgs("InsertColoredText", (text, color))
