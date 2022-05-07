
'''
COPYRIGHT (C) XAM GmbH

MODULE DESCRIPTION:
    PyLint Logger (QTextEdit) colorizer
'''

import re


class PyLintOutputStyler:
    """
    """
    creg_cmdline = re.compile("^python (.*) PyLint ")

    creg_fatal_msg      = re.compile("F([0-9]*)\(.*\):.*")
    creg_error_msg      = re.compile("E([0-9]*)\(.*\):.*")
    creg_warning_msg    = re.compile("W([0-9]*)\(.*\):.*")
    creg_info_msg       = re.compile("I([0-9]*)\(.*\):.*")
    creg_convention_msg = re.compile("C([0-9]*)\(.*\):.*")
    creg_refactor_msg   = re.compile("R([0-9]*)\(.*\):.*")

    def __init__(self, dlg):
        '''
        '''
        # setup attributes
        self.in_report = False

        self.GCONF_COLOR_FATAL       = dlg.ui.PYLINT_FATAL_COLOR.color()
        self.GCONF_COLOR_ERROR       = dlg.ui.PYLINT_ERROR_COLOR.color()
        self.GCONF_COLOR_WARNING     = dlg.ui.PYLINT_WARNING_COLOR.color()
        self.GCONF_COLOR_INFORMATION = dlg.ui.PYLINT_INFORMATION_COLOR.color()
        self.GCONF_COLOR_CONVENTION  = dlg.ui.PYLINT_CONVENTION_COLOR.color()
        self.GCONF_COLOR_REFACTOR    = dlg.ui.PYLINT_REFACTOR_COLOR.color()

    def Reset(self):
        '''
        '''
        pass

    def IgnoreErrorLine(self, line):
        '''
        '''
        if line.startswith("pylint: error:"):
            return False

        if "No config file found, using default configuration" in line:
            return True

        return True  # ignore all sonce!

    def IgnoreOutputLine(self, line):
        '''
        '''
        return False

    def ProcessOutputGetLineColor(self, line):
        '''
        '''
        color = 'black'  # default

        if line.startswith("python "):
            color = "blue"

        if line.startswith("pylint: error:"):
            color = 'magenta'

        if line == "STARTING PyLint ...":
            color = 'blue'
        if line.startswith("PyLint Done - Exitcode:"):
            color = 'blue'
        if self.creg_cmdline.match(line):
            color = 'blue'

        if line.startswith("PyLint: error: "):
            color = 'magenta'

        # LINE "HEADER" DEPENDS ON GCONF! (PYLINT.REPORT.msg_template)

        if line.startswith("F") :
            if len(line) > 5 and line[5] == ":":
                color = self.GCONF_COLOR_FATAL
            elif len(line) > 1 and line[1] == ":":
                color = self.GCONF_COLOR_FATAL
            else:
                if self.creg_fatal_msg.search(line) :
                    color = self.GCONF_COLOR_FATAL

        elif line.startswith("E"):
            if len(line) > 5 and line[5] == ":":
                color = self.GCONF_COLOR_ERROR
            elif len(line) > 1 and line[1] == ":":
                color = self.GCONF_COLOR_ERROR
            else:
                if self.creg_error_msg.search(line) :
                    color = self.GCONF_COLOR_ERROR

        elif line.startswith("W") :
            if len(line) > 5 and line[5] == ":":
                color = self.GCONF_COLOR_WARNING
            elif len(line) > 1 and line[1] == ":":
                color = self.GCONF_COLOR_WARNING
            else:
                if self.creg_warning_msg.search(line) :
                    color = self.GCONF_COLOR_WARNING

        elif line.startswith("I") :
            if len(line) > 5 and line[5] == ":":
                color = self.GCONF_COLOR_INFORMATION
            elif len(line) > 1 and line[1] == ":":
                color = self.GCONF_COLOR_INFORMATION
            else:
                if self.creg_info_msg.search(line) :
                    color = self.GCONF_COLOR_INFORMATION

        elif line.startswith("C") :
            if len(line) > 5 and line[5] == ":":
                color = self.GCONF_COLOR_CONVENTION
            elif len(line) > 1 and line[1] == ":":
                color = self.GCONF_COLOR_CONVENTION
            else:
                if self.creg_convention_msg.search(line) :
                    color = self.GCONF_COLOR_CONVENTION

        elif line.startswith("R") :
            if len(line) > 5 and line[5] == ":":
                color = self.GCONF_COLOR_REFACTOR
            elif len(line) > 1 and line[1] == ":":
                color = self.GCONF_COLOR_REFACTOR
            else:
                if self.creg_refactor_msg.search(line) :
                    color = self.GCONF_COLOR_REFACTOR

        return color

    def ProcessOutputGetLineWeight(self, line):
        '''
        '''
        if line.startswith("pylint: error:"):
            weight = "FONTWEIGHT_BOLD"
        elif line.startswith("************* Module"):
            weight = "FONTWEIGHT_BOLD"
        else:
            weight = "FONTWEIGHT_NORMAL"

        return weight

    def ProcessOutputGetLineFamily(self, line):
        '''
        '''
        if line.startswith("Report"):
            self.in_report = True
        #if line.startswith("Global evaluation"):
        #    self.in_report = False
        #if line.startswith("Duplication"):
        #    self.in_report = True
        if line.startswith("PyLint Done - Exitcode:"):
            self.in_report = False
        if line.startswith("************* Module"):
            self.in_report = False

        if self.in_report:
            family = "FONTFAMILY_DECORATIVE"
            family = "FONTFAMILY_TELETYPE"
        else:
            family = "FONTFAMILY_DEFAULT"  # default

        return family

    def ProcessOutputGetLineStyle(self, line):
        '''
        '''
        return "FONTSTYLE_NORMAL"
