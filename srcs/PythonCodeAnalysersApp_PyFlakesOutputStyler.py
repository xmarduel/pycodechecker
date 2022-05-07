
'''
COPYRIGHT (C) XAM GmbH

MODULE DESCRIPTION:
    PyFlakes Logger (QTextEdit) colorizer
'''

import re


class PyFlakesOutputStyler:
    """
    """
    # compile regexpr to parse the selected line
    messages =  {
        # PyFlakes-2.1.0 messages
        'UNUSEDIMPORT'             : { "msg" : re.compile("imported module (.*) not used")},
        'REDEFINEDWHILEUNUSED'     : { "msg" : re.compile('redefinition of unused (.*) from line (.*)')},
        'REDEFINEDINLISTCOMP'      : { "msg" : re.compile("list comprehension redefines (.*) from line (.*)")},
        'IMPORTSHADOWED'           : { "msg" : re.compile("import (.*) shadowed by loop variable")},
        'IMPORTSTARNOTPERMITTED'   : { "msg" : re.compile("'from (.*) import \*' only allowed at module level")},
        'IMPORTSTARUSED'           : { "msg" : re.compile("'from (.*) import \*' used; unable to detect undefined names")},
        'IMPORTSTARUSAGE'          : { "msg" : re.compile("(.*) may be undefined, or defined from star imports: (.*)")},
        'UNDEFINEDNAME'            : { "msg" : re.compile("undefined name (.*)")},
        'DOCTESTSYNTAXERROR'       : { "msg" : re.compile('syntax error in doctest')},
        'UNDEFINEDEXPORT'          : { "msg" : re.compile('undefined name (.*) in __all__')},
        'UNDEFINEDLOCAL'           : { "msg" : re.compile("local variable '(.*)' referenced before assignment")},
        'DUPLICATEDARG'            : { "msg" : re.compile("duplicate argument (.*) in function definition")},
        'MULTIVALUEREPEATEDKEYLIT' : { "msg" : re.compile("dictionary key (.*) repeated with different values")},
        'MULTIVALUEREPEATEDKEYVAR' : { "msg" : re.compile("dictionary key (.*) variable repeated with different values")},
        'LATEFUTUREIMPORT'         : { "msg" : re.compile("from __future__ imports must occur at the beginning of the file")},
        'FUTURENOTDEFINED'         : { "msg" : re.compile("future feature (.*) is not defined")},
        'UNUSEDVARIABLE'           : { "msg" : re.compile("local variable (.*) is assigned to but never used")},
        'RETURNWITHARGSINSIDEGEN'  : { "msg" : re.compile('\'return\' with argument inside generator')},
        'RETURNOUTSIDEFUNCTION'    : { "msg" : re.compile('\'return\' outside function')},
        'YIELDNOUTSIDEFUNCTION'    : { "msg" : re.compile('\'yield\' outside function')},
        'CONTINUEOUTSIDELOOP'      : { "msg" : re.compile('\'continue\' not properly in loop')},
        'BREAKOUTSIDELOOP'         : { "msg" : re.compile('\'break\' not properly in loop')},
        'CONTINUEINFINALLY'        : { "msg" : re.compile('\'continue\' not supported inside \'finally\' clause')},
        'DEFAULTEXCEPTIONLAST'     : { "msg" : re.compile('default \'except:\' must be last')},
        'TWOSTARREDEXPRESSIONS'    : { "msg" : re.compile('two starred expressions in assignment')},
        'TOOMANYEXPRINSTARREDASS'  : { "msg" : re.compile('too many expressions in star-unpacking assignment')},
        'ASSERTTUPLE'              : { "msg" : re.compile('assertion is always true, perhaps remove parentheses?')},
        'FORWARDANNOTATIONERROR'   : { "msg" : re.compile('syntax error in forward annotation (.*)')},
        'COMMENTANNOTATIONERROR'   : { "msg" : re.compile('syntax error in type comment (.*)')},
        'RAISENOTIMPLEMENTED'      : { "msg" : re.compile("raise NotImplemented' should be 'raise NotImplementedError'")},
        'INVALIDPRINTSYNTAX'       : { "msg" : re.compile('use of >> is invalid with print function')},
         # XAM extra messages
        'UNUSEDFUNCTIONARG'        : { "msg" : re.compile("function parameter (.*) not used")},
        'BADINDENTATION'           : { "msg" : re.compile("bad indentation (.*)")}
    }
        
    creg_cmdline = re.compile("^python (.*) PyFlakes ")

    def __init__(self, dlg, dlg2):
        '''
        '''
        # setup attributes
        self.inInvalidSyntaxError = False

        self.GCONF_COLOR_FATAL       = dlg.ui.PYFLAKES_FATAL_COLOR.color()
        self.GCONF_COLOR_ERROR       = dlg.ui.PYFLAKES_ERROR_COLOR.color()
        self.GCONF_COLOR_WARNING     = dlg.ui.PYFLAKES_WARNING_COLOR.color()
        self.GCONF_COLOR_INFORMATION = dlg.ui.PYFLAKES_INFORMATION_COLOR.color()

        # message severity in configuration
        for message in self.messages:
            try:
                self.messages[message]["severity"] = dlg2.pyflakes_get_feature_level(message).upper()
            except Exception as msg:
                self.messages[message]["severity"] = "ERROR"

    def Reset(self):
        '''
        '''
        self.inInvalidSyntaxError = False

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
        color = 'black'  # default

        colormap = {
            "FATAL":   self.GCONF_COLOR_FATAL,  # 'magenta'
            "ERROR":   self.GCONF_COLOR_ERROR,  # 'red'
            "WARNING": self.GCONF_COLOR_WARNING,  # 'orange'
            "INFO":    self.GCONF_COLOR_INFORMATION,  # 'green'
            "DEBUG":   'black',
        }

        if line.startswith("python "):
            color = "blue"

        if line.strip().endswith(": No such file"):
            color = self.GCONF_COLOR_FATAL
        elif line.strip().endswith(": No such file or directory"):
            color = self.GCONF_COLOR_FATAL
        elif line.strip().endswith(": invalid syntax"):
            color = self.GCONF_COLOR_FATAL
        elif line.strip().endswith(": unexpected indent"):
            color = self.GCONF_COLOR_FATAL
        elif line.strip().endswith(": could not compile"):
            color = self.GCONF_COLOR_FATAL
        elif line.strip().endswith(": checker exception"):
            color = self.GCONF_COLOR_FATAL
        elif line.strip().endswith(": unindent does not match any outer indentation level"):
            color = self.GCONF_COLOR_FATAL
        elif line.strip().endswith("problem decoding source"):
            color = self.GCONF_COLOR_FATAL


        if line == "STARTING PyFlakes ...":
            color = 'blue'
        if line.startswith("PyFlakes Done - Exitcode:"):
            color = 'blue'
        if self.creg_cmdline.match(line):
            color = 'blue'

        for key in self.messages:
            if self.messages[key]["msg"].search(line) is not None:
                color = colormap.get(self.messages[key]["severity"], 'black')
                break

        return color

    def ProcessOutputGetLineWeight(self, line):
        '''
        '''
        if line.strip().endswith(": No such file"):
            weight = "FONTWEIGHT_BOLD"
        if line.strip().endswith(": No such file or directory"):
            weight = "FONTWEIGHT_BOLD"
        elif line.strip().endswith(": invalid syntax"):
            weight = "FONTWEIGHT_BOLD"
        elif line.strip().endswith(": unexpected indent"):
            weight = "FONTWEIGHT_BOLD"
        elif line.strip().endswith(": could not compile"):
            weight = "FONTWEIGHT_BOLD"
        elif line.strip().endswith(": checker exception"):
            weight = "FONTWEIGHT_BOLD"
        elif line.strip().endswith(": unindent does not match any outer indentation level"):
            weight = "FONTWEIGHT_BOLD"
        elif line.strip().endswith("problem decoding source"):
            weight = "FONTWEIGHT_BOLD"
        elif line.startswith("=== File:"):
            weight = "FONTWEIGHT_BOLD"
        else:
            weight = "FONTWEIGHT_NORMAL"

        return weight

    def ProcessOutputGetLineFamily(self, line):
        '''
        '''
        if line.startswith("PyFlakes Done - Exitcode:"):
            self.inInvalidSyntaxError = False
        if line.startswith("=== File:"):
            self.inInvalidSyntaxError = False

        if self.inInvalidSyntaxError:
            family = "FONTFAMILY_TELETYPE"
        else:
            family = "FONTFAMILY_DEFAULT"

        if line.strip().endswith(": invalid syntax"):
            self.inInvalidSyntaxError = True
        if line.strip().endswith(": unexpected indent"):
            self.inInvalidSyntaxError = True

        return family

    def ProcessOutputGetLineStyle(self, line):
        '''
        '''
        return "FONTSTYLE_NORMAL"
