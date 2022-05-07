
'''
COPYRIGHT (C) XAM GmbH

MODULE DESCRIPTION:
    shell Logger (QTextEdit) colorizer
'''


class ShellOutputStyler:
    """
    """
    def __init__(self, dlg):
        '''
        '''
        pass

    def IgnoreErrorLine(self, line):
        '''
        '''
        return False

    def IgnoreOutputLine(self, line):
        '''
        '''
        return False

    def ProcessOutputGetLineColor(self, line):
        '''
        '''
        return "blue"

    def ProcessOutputGetLineWeight(self, line):
        '''
        '''
        return "FONTWEIGHT_NORMAL"

    def ProcessOutputGetLineFamily(self, line):
        '''
        '''
        return "FONTFAMILY_DEFAULT"  # default

    def ProcessOutputGetLineStyle(self, line):
        '''
        '''
        return "FONTSTYLE_NORMAL"
