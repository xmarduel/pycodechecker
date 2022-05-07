
'''
COPYRIGHT (C) XAM GmbH

MODULE DESCRIPTION:
    PyMetrics Logger (QTextEdit) colorizer
'''

import re


class PyMetricsOutputStyler:
    """
    """
    creg_cmdline = re.compile("^python (.*) PyMetrics ")

    # compiled regexprs to parse a selected line of the header
    simplereport_modulewithdocstring = re.compile("^Module (.*) is missing a module doc string. Detected at line (.*)$")
    # extra exits
    extra_exits  = re.compile("^function (.*) has (.*) extra exit[s]* at line[s]*")

    # 100.00 %ClassesHavingDocStrings
    #  12.93 %Comments
    #   1.80 %CommentsInline
    #  40.59 %FunctionsHavingDocStrings
    basic_classeswithdocstring   =  re.compile("^(.*) \%ClassesHavingDocStrings")
    basic_comments               =  re.compile("^(.*) \%Comments")
    basic_commentsinline         =  re.compile("^(.*) \%CommentsInline")
    basic_functionswithdocstring =  re.compile("^(.*) \%FunctionsHavingDocStrings")

    #    1    maxBlockDepth
    #    2    numBlocks
    #  109    numCharacters
    basic_numbers_nums           =  re.compile("^ *([0-9]*) *num(.*)$")
    basic_numbers_maxs           =  re.compile("^ *([0-9]*) *max(.*)$")

    have_docstring               = re.compile("^ *\+ .*$")
    have_no_docstring            = re.compile("^ *\- .*$")

    def __init__(self, dlg):
        '''
        '''
        # setup attributes
        self.in_header             = False
        self.in_basicmetrics       = False
        self.in_functionsdocstring = False
        self.in_classesdocstring   = False
        self.in_mccabe             = False
        self.in_sloc               = False
        self.in_halstead           = False

        self.GCONF_HEADER_MODULE_WITHOUT_DOCSTRING_COLOR      = dlg.ui.PYMETRICS_HEADER_MODULE_NO_DOCSTRING_COLOR.color()

        self.GCONF_HEADER_EXTRAEXITS_SMALLER_LOWERLIMIT_COLOR = dlg.ui.PYMETRICS_HEADER_EXTRAEXITS_SMALLER_LOWERLIMIT_COLOR.color()
        self.GCONF_HEADER_EXTRAEXITS_BETWEENLIMITS_COLOR      = dlg.ui.PYMETRICS_HEADER_EXTRAEXITS_BETWEENLIMITS_COLOR.color()
        self.GCONF_HEADER_EXTRAEXITS_BIGGER_UPPERLIMIT_COLOR  = dlg.ui.PYMETRICS_HEADER_EXTRAEXITS_BIGGER_UPPERLIMIT_COLOR.color()
        self.GCONF_HEADER_EXTRAEXITS_LOWERLIMIT               = dlg.ui.PYMETRICS_HEADER_EXTRAEXITS_LOWERLIMIT_SLIDER.value()
        self.GCONF_HEADER_EXTRAEXITS_UPPERLIMIT               = dlg.ui.PYMETRICS_HEADER_EXTRAEXITS_UPPERLIMIT_SLIDER.value()

        self.GCONF_BASIC_NUMBERS_COLOR                        = dlg.ui.PYMETRICS_BASIC_NUMBERS_COLOR.color()

        self.GCONF_BASIC_DOCSTRINGS_PERCENTAGE_LOWERLIMIT_COLOR    = dlg.ui.PYMETRICS_BASIC_DOCSTRINGS_PERCENTAGE_LOWERLIMIT_COLOR.color()
        self.GCONF_BASIC_DOCSTRINGS_PERCENTAGE_BETWEENLIMITS_COLOR = dlg.ui.PYMETRICS_BASIC_DOCSTRINGS_PERCENTAGE_BETWEENLIMITS_COLOR.color()
        self.GCONF_BASIC_DOCSTRINGS_PERCENTAGE_UPPERLIMIT_COLOR    = dlg.ui.PYMETRICS_BASIC_DOCSTRINGS_PERCENTAGE_UPPERLIMIT_COLOR.color()
        self.GCONF_BASIC_DOCSTRINGS_LOWERLIMIT                     = dlg.ui.PYMETRICS_BASIC_DOCSTRINGS_LOWERLIMIT_SLIDER.value()
        self.GCONF_BASIC_DOCSTRINGS_UPPERLIMIT                     = dlg.ui.PYMETRICS_BASIC_DOCSTRINGS_UPPERLIMIT_SLIDER.value()
        self.GCONF_BASIC_COMMENTS_PERCENTAGE_LOWERLIMIT_COLOR      = dlg.ui.PYMETRICS_BASIC_COMMENTS_PERCENTAGE_LOWERLIMIT_COLOR.color()
        self.GCONF_BASIC_COMMENTS_PERCENTAGE_BETWEENLIMITS_COLOR   = dlg.ui.PYMETRICS_BASIC_COMMENTS_PERCENTAGE_BETWEENLIMITS_COLOR.color()
        self.GCONF_BASIC_COMMENTS_PERCENTAGE_UPPERLIMIT_COLOR      = dlg.ui.PYMETRICS_BASIC_COMMENTS_PERCENTAGE_UPPERLIMIT_COLOR.color()
        self.GCONF_BASIC_COMMENTS_LOWERLIMIT                       = dlg.ui.PYMETRICS_BASIC_COMMENTS_PERCENTAGE_LOWERLIMIT_SLIDER.value()
        self.GCONF_BASIC_COMMENTS_UPPERLIMIT                       = dlg.ui.PYMETRICS_BASIC_COMMENTS_PERCENTAGE_UPPERLIMIT_SLIDER.value()

        self.GCONF_DOCSTRING_YES_COLOR        = dlg.ui.PYMETRICS_DOCSTRING_YES_COLOR.color()
        self.GCONF_DOCSTRING_NO_COLOR         = dlg.ui.PYMETRICS_DOCSTRING_NO_COLOR.color()

        self.GCONF_SLOC_LOWERLIMIT_COLOR      = dlg.ui.PYMETRICS_SLOC_LOWERLIMIT_COLOR.color()
        self.GCONF_SLOC_BETWEENLIMITS_COLOR   = dlg.ui.PYMETRICS_SLOC_BETWEENLIMITS_COLOR.color()
        self.GCONF_SLOC_UPPERLIMIT_COLOR      = dlg.ui.PYMETRICS_SLOC_UPPERLIMIT_COLOR.color()
        self.GCONF_SLOC_LOWERLIMIT            = dlg.ui.PYMETRICS_SLOC_LOWERLIMIT_SLIDER.value()
        self.GCONF_SLOC_UPPERLIMIT            = dlg.ui.PYMETRICS_SLOC_UPPERLIMIT_SLIDER.value()

        self.GCONF_MCCABE_LOWERLIMIT_COLOR    = dlg.ui.PYMETRICS_MCCABE_LOWERLIMIT_COLOR.color()
        self.GCONF_MCCABE_BETWEENLIMITS_COLOR = dlg.ui.PYMETRICS_MCCABE_BETWEENLIMITS_COLOR.color()
        self.GCONF_MCCABE_UPPERLIMIT_COLOR    = dlg.ui.PYMETRICS_MCCABE_UPPERLIMIT_COLOR.color()
        self.GCONF_MCCABE_LOWERLIMIT          = dlg.ui.PYMETRICS_MCCABE_LOWERLIMIT_SLIDER.value()
        self.GCONF_MCCABE_UPPERLIMIT          = dlg.ui.PYMETRICS_MCCABE_UPPERLIMIT_SLIDER.value()

    def Reset(self):
        '''
        '''
        pass

    def IgnoreErrorLine(self, line):
        '''
        '''
        if line.startswith("Invalid character"):  # duplicated with InputLine
            return True

        return False

    def IgnoreOutputLine(self, line):
        '''
        '''
        return False

    def SetupInProperty(self, prop=None):
        '''
        '''
        # all to 'False'
        self.in_header             = False
        self.in_basicmetrics       = False
        self.in_functionsdocstring = False
        self.in_classesdocstring   = False
        self.in_mccabe             = False
        self.in_sloc               = False
        self.in_halstead           = False

        # but
        if prop : setattr(self, prop, True)

    def ProcessOutputGetLineColor(self, line):
        '''
        '''
        color = 'black'  # default

        if line.startswith("python "):
            color = "blue"

        if line.startswith("[Errno 2] No such file or directory: "):
            color = 'magenta'

        if line.startswith("Invalid character"):
            color = 'magenta'

        if line == "STARTING PyMetrics ...":
            color = 'blue'
        if line.startswith("PyMetrics Done - Exitcode:"):
            color = 'blue'
        if self.creg_cmdline.match(line):
            color = 'blue'

        if line.startswith("==="):
            self.SetupInProperty('in_header')
        if line.startswith("Basic Metrics"):
            self.SetupInProperty('in_basicmetrics')
        if line.startswith("Functions DocString"):
            self.SetupInProperty('in_functionsdocstring')
        if line.startswith("Classes DocString"):
            self.SetupInProperty('in_classesdocstring')
        if line.startswith("McCabe Complexity Metric"):
            self.SetupInProperty('in_mccabe')
        if line.startswith("COCOMO 2's SLOC Metric"):
            self.SetupInProperty('in_sloc')
        if line.startswith("Halstead Metrics"):
            self.SetupInProperty('in_halstead')

        if self.in_header:
            if self.extra_exits.findall(line):
                res =  self.extra_exits.findall(line)
                function, nbextra_exits = res[0]

                color = self.GCONF_HEADER_EXTRAEXITS_SMALLER_LOWERLIMIT_COLOR
                if int(nbextra_exits) > self.GCONF_HEADER_EXTRAEXITS_LOWERLIMIT :  # 10:
                    color = self.GCONF_HEADER_EXTRAEXITS_BETWEENLIMITS_COLOR
                if int(nbextra_exits) > self.GCONF_HEADER_EXTRAEXITS_UPPERLIMIT :  # 20
                    color = self.GCONF_HEADER_EXTRAEXITS_BIGGER_UPPERLIMIT_COLOR

            if self.simplereport_modulewithdocstring.match(line):
                color = self.GCONF_HEADER_MODULE_WITHOUT_DOCSTRING_COLOR


            # these percents can be here (--nobasic) or in the "Basic Metrics section too !

            # 100.00 %ClassesHavingDocStrings
            #  12.93 %Comments
            #   1.80 %CommentsInline
            #  40.59 %FunctionsHavingDocStrings
            if self.basic_classeswithdocstring.match(line):
                res = self.basic_classeswithdocstring.findall(line)
                color = self.GCONF_BASIC_DOCSTRINGS_PERCENTAGE_LOWERLIMIT_COLOR
                if float(res[0]) >= self.GCONF_BASIC_DOCSTRINGS_LOWERLIMIT:
                    color = self.GCONF_BASIC_DOCSTRINGS_PERCENTAGE_BETWEENLIMITS_COLOR
                if float(res[0]) >= self.GCONF_BASIC_DOCSTRINGS_UPPERLIMIT:
                    color = self.GCONF_BASIC_DOCSTRINGS_PERCENTAGE_UPPERLIMIT_COLOR

            if self.basic_functionswithdocstring.match(line):
                res = self.basic_functionswithdocstring.findall(line)
                color = self.GCONF_BASIC_DOCSTRINGS_PERCENTAGE_LOWERLIMIT_COLOR
                if float(res[0]) >= self.GCONF_BASIC_DOCSTRINGS_LOWERLIMIT:
                    color = self.GCONF_BASIC_DOCSTRINGS_PERCENTAGE_BETWEENLIMITS_COLOR
                if float(res[0]) >= self.GCONF_BASIC_DOCSTRINGS_UPPERLIMIT:
                    color = self.GCONF_BASIC_DOCSTRINGS_PERCENTAGE_UPPERLIMIT_COLOR

            if self.basic_comments.match(line):
                res = self.basic_comments.findall(line)
                color = self.GCONF_BASIC_COMMENTS_PERCENTAGE_LOWERLIMIT_COLOR
                if float(res[0]) >= self.GCONF_BASIC_COMMENTS_LOWERLIMIT :
                    color = self.GCONF_BASIC_COMMENTS_PERCENTAGE_BETWEENLIMITS_COLOR
                if float(res[0]) <= self.GCONF_BASIC_DOCSTRINGS_UPPERLIMIT :
                    color = self.GCONF_BASIC_COMMENTS_PERCENTAGE_UPPERLIMIT_COLOR

            if self.basic_commentsinline.match(line):
                res = self.basic_commentsinline.findall(line)
                color = self.GCONF_BASIC_COMMENTS_PERCENTAGE_LOWERLIMIT_COLOR
                if float(res[0]) >= self.GCONF_BASIC_COMMENTS_LOWERLIMIT :
                    color = self.GCONF_BASIC_COMMENTS_PERCENTAGE_BETWEENLIMITS_COLOR
                if float(res[0]) >= self.GCONF_BASIC_COMMENTS_UPPERLIMIT :
                    color = self.GCONF_BASIC_COMMENTS_PERCENTAGE_UPPERLIMIT_COLOR


        if self.in_basicmetrics:

            if self.basic_numbers_nums.match(line):
                res = self.basic_numbers_nums.findall(line)
                val   = res[0][0]
                ident = res[0][1]
                # do we do colors here ?
                color = self.GCONF_BASIC_NUMBERS_COLOR

            if self.basic_numbers_maxs.match(line):
                res = self.basic_numbers_maxs.findall(line)
                val   = res[0][0]
                ident = res[0][1]
                # do we do colors here ?
                color = self.GCONF_BASIC_NUMBERS_COLOR

            # 100.00 %ClassesHavingDocStrings
            #  12.93 %Comments
            #   1.80 %CommentsInline
            #  40.59 %FunctionsHavingDocStrings
            if self.basic_classeswithdocstring.match(line):
                res = self.basic_classeswithdocstring.findall(line)
                color = self.GCONF_BASIC_DOCSTRINGS_PERCENTAGE_LOWERLIMIT_COLOR
                if float(res[0]) >= self.GCONF_BASIC_DOCSTRINGS_LOWERLIMIT:
                    color = self.GCONF_BASIC_DOCSTRINGS_PERCENTAGE_BETWEENLIMITS_COLOR
                if float(res[0]) >= self.GCONF_BASIC_DOCSTRINGS_UPPERLIMIT:
                    color = self.GCONF_BASIC_DOCSTRINGS_PERCENTAGE_UPPERLIMIT_COLOR

            if self.basic_functionswithdocstring.match(line):
                res = self.basic_functionswithdocstring.findall(line)
                color = self.GCONF_BASIC_DOCSTRINGS_PERCENTAGE_LOWERLIMIT_COLOR
                if float(res[0]) >= self.GCONF_BASIC_DOCSTRINGS_LOWERLIMIT:
                    color = self.GCONF_BASIC_DOCSTRINGS_PERCENTAGE_BETWEENLIMITS_COLOR
                if float(res[0]) >= self.GCONF_BASIC_DOCSTRINGS_UPPERLIMIT:
                    color = self.GCONF_BASIC_DOCSTRINGS_PERCENTAGE_UPPERLIMIT_COLOR

            if self.basic_comments.match(line):
                res = self.basic_comments.findall(line)
                color = self.GCONF_BASIC_COMMENTS_PERCENTAGE_LOWERLIMIT_COLOR
                if float(res[0]) >= self.GCONF_BASIC_COMMENTS_LOWERLIMIT :
                    color = self.GCONF_BASIC_COMMENTS_PERCENTAGE_BETWEENLIMITS_COLOR
                if float(res[0]) <= self.GCONF_BASIC_DOCSTRINGS_UPPERLIMIT :
                    color = self.GCONF_BASIC_COMMENTS_PERCENTAGE_UPPERLIMIT_COLOR

            if self.basic_commentsinline.match(line):
                res = self.basic_commentsinline.findall(line)
                color = self.GCONF_BASIC_COMMENTS_PERCENTAGE_LOWERLIMIT_COLOR
                if float(res[0]) >= self.GCONF_BASIC_COMMENTS_LOWERLIMIT :
                    color = self.GCONF_BASIC_COMMENTS_PERCENTAGE_BETWEENLIMITS_COLOR
                if float(res[0]) >= self.GCONF_BASIC_COMMENTS_UPPERLIMIT :
                    color = self.GCONF_BASIC_COMMENTS_PERCENTAGE_UPPERLIMIT_COLOR

        if self.in_functionsdocstring:
            color = 'black'
            if self.have_no_docstring.match(line):
                color = self.GCONF_DOCSTRING_NO_COLOR
            if self.have_docstring.match(line):
                color = self.GCONF_DOCSTRING_YES_COLOR

        if self.in_classesdocstring:
            color = 'black'
            if self.have_no_docstring.match(line):
                color = self.GCONF_DOCSTRING_NO_COLOR
            if self.have_docstring.match(line):
                color = self.GCONF_DOCSTRING_YES_COLOR

        if self.in_mccabe:
            # parse line of the form  "  %d %s"
            try:
                res = line.strip().split(" ")
                #print "res = ",str(res)
                complexity, function = int(res[0]), res[-1]

                color = self.GCONF_MCCABE_LOWERLIMIT_COLOR

                if complexity >= self.GCONF_MCCABE_LOWERLIMIT :
                    color = self.GCONF_MCCABE_BETWEENLIMITS_COLOR
                if complexity >= self.GCONF_MCCABE_UPPERLIMIT :
                    color = self.GCONF_MCCABE_UPPERLIMIT_COLOR
            except Exception as msg:
                #print  str(msg),  line
                color = 'black'

        if self.in_sloc:
            # parse line of the form  "  %d %s"
            try:
                res = line.strip().split(" ")
                #print "res = ",str(res)
                complexity, function = int(res[0]), res[-1]

                color = self.GCONF_SLOC_LOWERLIMIT_COLOR

                if complexity >= self.GCONF_SLOC_LOWERLIMIT :
                    color = self.GCONF_SLOC_BETWEENLIMITS_COLOR
                if complexity >= self.GCONF_SLOC_UPPERLIMIT :
                    color = self.GCONF_SLOC_UPPERLIMIT_COLOR
            except Exception as msg:
                #print  str(msg),  line
                color = 'black'

        if self.in_halstead:
            if line.startswith("*** Processed"):
                color = 'black'
            else:
                try:
                    if line.startswith("Halstead Metrics") or line.startswith("-" * 20):
                        color = 'black'
                    else:
                        # line of the form
                        #hdr1 = "Cat Identifier                                         D         E              N     N1     N2 V         avgE      avgV          n    n1  n2"
                        #hdr2 = "--- -------------------------------------------------- --------- --------- ------ ------ ------ --------- --------- --------- ----- ----- ---"
                        #        (F) PyMetricsLogger.toto                               1.89e+002 1.09e+005     77     41     36 5.79e+002 1.21e+007 1.15e+004   184   168  16
                        data = line.strip().split()
                        try:
                            Cat, Identifier, D, E, N, N1, N2, V, avgE, avgV, n, n1, n2 = data

                            coeff = 1
                            if Cat == '(M)':
                                coeff = 100
                            elif Cat == '(C)':
                                coeff = 10
                            elif Cat == '(F)':
                                coeff = 1
                            else:
                                coeff = 1

                            if float(D) > 1000.0 * coeff:
                                color = 'red'
                            elif float(D) > 100.0  * coeff:
                                color = 'orange'
                            else:
                                color = 'blue'
                        except Exception as msg:
                            color = 'blue'
                except Exception as msg:
                    #print  str(msg),  line
                    color = 'black'

        return color

    def ProcessOutputGetLineWeight(self, line):
        '''
        '''
        if line.startswith("=== File:"):
            weight = "FONTWEIGHT_BOLD"
        else:
            weight = "FONTWEIGHT_NORMAL"

        return weight

    def ProcessOutputGetLineFamily(self, line):
        '''
        '''
        if self.in_halstead and not (line.startswith("Halstead Metrics") or line.startswith("-" * 20)) :
            family = "FONTFAMILY_TELETYPE"
        else:
            family = "FONTFAMILY_DEFAULT"  # default

        return family

    def ProcessOutputGetLineStyle(self, line):
        '''
        '''
        return "FONTSTYLE_NORMAL"
