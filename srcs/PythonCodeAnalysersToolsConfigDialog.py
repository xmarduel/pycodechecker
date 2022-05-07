
'''
COPYRIGHT (C) XAM GmbH

MODULE DESCRIPTION:
    The Configuration Dialog for the different Tools.
'''

from PySide2 import QtCore
from PySide2 import QtWidgets

from PySide2.QtUiTools import QUiLoader
from PySide2 import QtUiTools

#----------------------------------------------------------------

class ConfigDialog(QtWidgets.QDialog):
    '''
    Description:
    '''
    pyflakes_features = {
        "UNUSEDIMPORT"                   : { "default" : "WARNING" },
        "REDEFINEDWHILEUNUSED"           : { "default" : "WARNING" },
        "REDEFINEDINLISTCOMP"            : { "default" : "WARNING" },
        "SHADOWINGIMPORT"                : { "default" : "WARNING" },
        "IMPORTSTARNOTPERMITTED"         : { "default" : "WARNING" },
        "IMPORTSTARUSED"                 : { "default" : "WARNING" },
        "IMPORTSTARUSAGE"                : { "default" : "WARNING" },
        "UNDEFINEDNAME"                  : { "default" : "ERROR" },
        "DOCTESTSYNTAXERROR"             : { "default" : "WARNING" },
        "UNDEFINEDEXPORT"                : { "default" : "WARNING" },
        "UNDEFINEDLOCAL"                 : { "default" : "WARNING" },
        "DUPLICATEDARG"                  : { "default" : "ERROR" },
        "LATEFUTUREIMPORT"               : { "default" : "WARNING" },
        "UNUSEDVARIABLE"                 : { "default" : "INFO" },
        "RETURNWITHARGSINSIDEGEN"        : { "default" : "ERROR" },
        "RETURNOUTSIDEFUNCTION"          : { "default" : "INFO" },
        "COMMENTANNOTATIONERROR"         : { "default" : "ERROR" },
        "RAISENOTIMPLEMENTED"            : { "default" : "WARNING" },
        "INVALIDPRINTSYNTAX"             : { "default" : "ERROR" },  
        # XAM
        "UNUSEDFUNCTIONARG"              : { "default" : "INFO" },
        "BADINDENTATION"                 : { "default" : "ERROR" },
    }
    
    pylint_features = {
        "FATAL"       : ("0001","0002","0003","0004","0202","0220","0321","0401"),
        "ERROR"       : ("0001","0011","0012","0100","0101","0102","0103","0104","0105","0106","0107","0108","0202","0203","0211","0213","0221","0222","0401","0503","0601","0602","0603","0604","0611","0701","0702","0703","0710","0711","0712","1001","1002","1003","1004","1101","1102","1103","1111","1120","1121","1122","1123","1124","1200","1201","1205","1206","1300","1301","1302","1303","1304","1305","1306","1310" ),
        "WARNING"     : ("0101","0102","0104","0105","0106","0107","0108","0109","0110","0120","0122","0141","0142","0150","0199","0201","0211","0212","0221","0222","0223","0231","0232","0233","0301","0311","0312","0331","0332","0333","0401","0402","0403","0404","0406","0410","0511","0601","0602","0603","0604","0611","0612","0613","0614","0621","0622","0631","0701","0702","0703","0704","0710","0711","1001","1111","1201","1202","1300","1301","1302","1303","1304","1305","1306","1307","1401","1402" ),
        "CONVENTION"  : ("0102","0103","0111","0112","0121","0202","0203","0204","0301","0302","0303","0304","0321","0322","0323","0324","0325","0326","0330","1001" ),
        "INFORMATION" : ("0001","0010","0011","0012","0013"),
        "REFACTOR"    : ("0201","0401","0801","0901","0902","0903","0904","0911","0912","0913","0914","0915","0921","0922","0923","0924"),
        "REPORT"      : ("0001","0002","0003","0004","0101","0401","0402","0801","0701"),
    }

    
    def __init__(self, parent):
        '''
        '''
        super(ConfigDialog, self).__init__(parent)

        # dialog content
        self.make_ui()
        # setup callbacks
        self.set_callbacks()
        # initialize content
        self.set_setting(parent.settings)
        
        # special ui behavior
        self.update_ui()
        
    def make_ui(self):
        '''
        '''
        self.ui = self.loadUi("PythonCodeAnalysersToolsConfigDialogUI.ui")

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(self.ui)
        
        self.setLayout(mainLayout)
        
    def update_ui(self, tool=None):
        '''
        '''
        def pylint_update_ui():
            ''' '''
            self.ui.PYLINT_MASTER_PROFILE.setEnabled(False)
            self.ui.PYLINT_REPORT_MSG_TEMPLATE.setEnabled(False)
            self.ui.PYLINT_REPORT_EVALUATION.setEnabled(False)
            
            self.ui.PYLINT_MESSAGES_SETUP__ENABLE_CHECKERS_IDS.setEnabled(False)
            self.ui.PYLINT_MESSAGES_SETUP__DISABLE_CHECKERS_IDS.setEnabled(False)
    
            self.ui.PYLINT_MESSAGES_SETUP__ENABLE_MSGCATEGORIES_IDS.setEnabled(True)
            self.ui.PYLINT_MESSAGES_SETUP__DISABLE_MSGCATEGORIES_IDS.setEnabled(True)
    
            self.ui.PYLINT_MESSAGES_SETUP__ENABLE_MSG_IDS.setEnabled(False)
            self.ui.PYLINT_MESSAGES_SETUP__DISABLE_MSG_IDS.setEnabled(False)
    
            self.ui.PYLINT_REPORTS_ENABLE_LINEEDIT.setEnabled(False)
            self.ui.PYLINT_REPORTS_DISABLE_LINEEDIT.setEnabled(False)
            
            # "REPORT"
            selected_items = []
            for nb in self.pylint_features["REPORT"]:
                cb = getattr(self.ui, "PYLINT_REPORT_%s" % nb)
                if cb.isChecked():
                    selected_items.append("RP"+nb)
                
            if self.ui.PYLINT_REPORTS_ENABLE_RB.isChecked():
                self.ui.PYLINT_REPORTS_ENABLE_LINEEDIT.setText(",".join(selected_items))
                self.ui.PYLINT_REPORTS_DISABLE_LINEEDIT.setText("")
            if self.ui.PYLINT_REPORTS_DISABLE_RB.isChecked():
                self.ui.PYLINT_REPORTS_ENABLE_LINEEDIT.setText("")
                self.ui.PYLINT_REPORTS_DISABLE_LINEEDIT.setText(",".join(selected_items))
                    
            # "MSGS"
            selected_items = []
            for f in ("FATAL", "ERROR" , "WARNING", "CONVENTION", "INFORMATION", "REFACTOR"):
                for nb in self.pylint_features[f]:
                    cb = getattr(self.ui, "PYLINT_%s_%s" % (f, nb))
                    if cb.isChecked():
                        selected_items.append(f[0]+nb)
                
            if self.ui.PYLINT_MESSAGES_SETUP__ENABLE_MSG_IDS_RADIOBTN.isChecked():
                self.ui.PYLINT_MESSAGES_SETUP__ENABLE_MSG_IDS.setText(",".join(selected_items))
                self.ui.PYLINT_MESSAGES_SETUP__DISABLE_MSG_IDS.setText("")
            if self.ui.PYLINT_MESSAGES_SETUP__DISABLE_MSG_IDS_RADIOBTN.isChecked():
                self.ui.PYLINT_MESSAGES_SETUP__ENABLE_MSG_IDS.setText("")
                self.ui.PYLINT_MESSAGES_SETUP__DISABLE_MSG_IDS.setText(",".join(selected_items))

        def pymetrics_update_ui():
            ''' '''
            # CSV
            if self.ui.PYMETRICS_OUTPUT_NOCSV.isChecked():
                self.ui.PYMETRICS_OUTPUT_CSV_FILENAME.setEnabled(False)
                self.ui.PYMETRICS_OUTPUT_CSV_NOHEADINGS.setEnabled(False)
            else:
                self.ui.PYMETRICS_OUTPUT_CSV_FILENAME.setEnabled(True)
                self.ui.PYMETRICS_OUTPUT_CSV_NOHEADINGS.setEnabled(True)
    
            # SQL
            if self.ui.PYMETRICS_OUTPUT_NOSQL.isChecked():
                self.ui.PYMETRICS_OUTPUT_SQL_FILENAME.setEnabled(False)
                self.ui.PYMETRICS_OUTPUT_SQL_TOKENTABLE.setEnabled(False)
                self.ui.PYMETRICS_OUTPUT_SQL_METRICSTABLE.setEnabled(False)
                self.ui.PYMETRICS_OUTPUT_SQL_EXISTS.setEnabled(False)
                self.ui.PYMETRICS_OUTPUT_SQL_NOOLD.setEnabled(False)
            else:
                self.ui.PYMETRICS_OUTPUT_SQL_FILENAME.setEnabled(True)
                self.ui.PYMETRICS_OUTPUT_SQL_TOKENTABLE.setEnabled(True)
                self.ui.PYMETRICS_OUTPUT_SQL_METRICSTABLE.setEnabled(True)
                self.ui.PYMETRICS_OUTPUT_SQL_EXISTS.setEnabled(True)
                self.ui.PYMETRICS_OUTPUT_SQL_NOOLD.setEnabled(True)
            
            # CUSTOM_EXTRAMODULES
            if self.ui.PYMETRICS_CUSTOM_EXTRAMODULES.isChecked():
                self.ui.PYMETRICS_CUSTOM_EXTRAMODULES_TEXT.setEnabled(True)
            else:
                self.ui.PYMETRICS_CUSTOM_EXTRAMODULES_TEXT.setEnabled(False)
    
            # CUSTOM_EXTRAMETRICS
            if self.ui.PYMETRICS_CUSTOM_EXTRAMETRICS.isChecked():
                self.ui.PYMETRICS_CUSTOM_EXTRAMETRICS_TEXT.setEnabled(True)
            else:
                self.ui.PYMETRICS_CUSTOM_EXTRAMETRICS_TEXT.setEnabled(False)
    
            # CUSTOM_USERDEFINEDLIBNAME
            if self.ui.PYMETRICS_CUSTOM_USERDEFINEDLIBNAME.isChecked():
                self.ui.PYMETRICS_CUSTOM_USERDEFINEDLIBNAME_TEXT.setEnabled(True)
            else:
                self.ui.PYMETRICS_CUSTOM_USERDEFINEDLIBNAME_TEXT.setEnabled(False)     
    
        def pyflakes_update_ui():
            pass

        # ---------------------------------------------------------------------------
        # ---------------------------------------------------------------------------
        
        if tool is None:
            # update all tool 
            pylint_update_ui()
            pymetrics_update_ui()
            pyflakes_update_ui()
        elif tool == 'PyLint':
            pylint_update_ui()
        elif tool == 'PyMetrics':
            pymetrics_update_ui()
        elif tool == 'PyFlakes':
            pyflakes_update_ui() 

    def pyflakes_get_feature_level(self, pyflakes_feature):
        ''' '''
        btngroup_name = "PYFLAKES_%s_BTNGROUP" % pyflakes_feature
        btngroup = getattr(self.ui, btngroup_name)
        for btn in btngroup.buttons():
            if btn.isChecked():
                return btn.text()
        return "??"

    def write_settings(self, settings):
        '''
        '''
        def settings_pyflakes():
            ''' '''
            settings.beginGroup("dialog_toolsconfig_pyflakes")
            
            for pyflakes_feature in self.pyflakes_features:
                btngroup_name = "PYFLAKES_%s_BTNGROUP" % pyflakes_feature
                settings.setValue(btngroup_name, self.pyflakes_get_feature_level(pyflakes_feature))
            
            settings.endGroup()
        
        def settings_pymetrics():
            ''' '''
            settings.beginGroup("dialog_toolsconfig_pymetrics")
            
            settings.setValue("PYMETRICS_BASIC", self.ui.PYMETRICS_BASIC.checkState())
            settings.setValue("PYMETRICS_SIMPLE", self.ui.PYMETRICS_SIMPLE.checkState())
            settings.setValue("PYMETRICS_MCCABE", self.ui.PYMETRICS_MCCABE.checkState())
            settings.setValue("PYMETRICS_SLOC", self.ui.PYMETRICS_SLOC.checkState())
            
            settings.setValue("PYMETRICS_OUTPUT_NOCSV", self.ui.PYMETRICS_OUTPUT_NOCSV.checkState())
            settings.setValue("PYMETRICS_OUTPUT_NOSQL", self.ui.PYMETRICS_OUTPUT_NOSQL.checkState())
            settings.setValue("PYMETRICS_OUTPUT_ZERO", self.ui.PYMETRICS_OUTPUT_ZERO.checkState())
            settings.setValue("PYMETRICS_OUTPUT_QUIET", self.ui.PYMETRICS_OUTPUT_QUIET.checkState())
            settings.setValue("PYMETRICS_OUTPUT_QUIETMODULEDOCSTRING", self.ui.PYMETRICS_OUTPUT_QUIETMODULEDOCSTRING.checkState())
            settings.setValue("PYMETRICS_OUTPUT_VERBOSE", self.ui.PYMETRICS_OUTPUT_VERBOSE.checkState())
            settings.setValue("PYMETRICS_OUTPUT_NOKWCNT", self.ui.PYMETRICS_OUTPUT_NOKWCNT.checkState())
            
            settings.setValue("PYMETRICS_OUTPUT_CSV_FILENAME", self.ui.PYMETRICS_OUTPUT_CSV_FILENAME.text())
            settings.setValue("PYMETRICS_OUTPUT_CSV_NOHEADINGS", self.ui.PYMETRICS_OUTPUT_CSV_NOHEADINGS.checkState())
            settings.setValue("PYMETRICS_OUTPUT_SQL_FILENAME", self.ui.PYMETRICS_OUTPUT_SQL_FILENAME.text())
            settings.setValue("PYMETRICS_OUTPUT_SQL_TOKENTABLE", self.ui.PYMETRICS_OUTPUT_SQL_TOKENTABLE.text()) 
            settings.setValue("PYMETRICS_OUTPUT_SQL_METRICSTABLE", self.ui.PYMETRICS_OUTPUT_SQL_METRICSTABLE.text())
            settings.setValue("PYMETRICS_OUTPUT_SQL_EXISTS", self.ui.PYMETRICS_OUTPUT_SQL_EXISTS.checkState())
            settings.setValue("PYMETRICS_OUTPUT_SQL_NOOLD", self.ui.PYMETRICS_OUTPUT_SQL_NOOLD.checkState())
            
            settings.setValue("PYMETRICS_CUSTOM_EXTRAMODULES", self.ui.PYMETRICS_CUSTOM_EXTRAMODULES.checkState())
            settings.setValue("PYMETRICS_CUSTOM_EXTRAMETRICS", self.ui.PYMETRICS_CUSTOM_EXTRAMETRICS.checkState())
            settings.setValue("PYMETRICS_CUSTOM_USERDEFINEDLIBNAME", self.ui.PYMETRICS_CUSTOM_USERDEFINEDLIBNAME.checkState())
            
            settings.setValue("PYMETRICS_CUSTOM_EXTRAMODULES_TEXT", self.ui.PYMETRICS_CUSTOM_EXTRAMODULES_TEXT.text())
            settings.setValue("PYMETRICS_CUSTOM_EXTRAMETRICS_TEXT", self.ui.PYMETRICS_CUSTOM_EXTRAMETRICS_TEXT.text())
            settings.setValue("PYMETRICS_CUSTOM_USERDEFINEDLIBNAME_TEXT", self.ui.PYMETRICS_CUSTOM_USERDEFINEDLIBNAME_TEXT.text())
            
            settings.endGroup()
        
        def settings_pylint():
            ''' '''
            settings.beginGroup("dialog_toolsconfig_pylint")
            
            for message_type in self.pylint_features:
                for nb in self.pylint_features[message_type]:
                    cb = getattr(self.ui, "PYLINT_%s_%s" % (message_type, nb))
                    settings.setValue("PYLINT_%s_%s" % (message_type, nb), cb.checkState())

            # MASTER TAB
            settings.setValue("PYLINT_MASTER_RCFILE", self.ui.PYLINT_MASTER_RCFILE.text())
            settings.setValue("PYLINT_MASTER_INITHOOK", self.ui.PYLINT_MASTER_INITHOOK.text())
            settings.setValue("PYLINT_MASTER_ERRORS_ONLY", self.ui.PYLINT_MASTER_ERRORS_ONLY.checkState())
            settings.setValue("PYLINT_MASTER_PROFILE", self.ui.PYLINT_MASTER_PROFILE.checkState())
            settings.setValue("PYLINT_MASTER_IGNORE", self.ui.PYLINT_MASTER_IGNORE.text())
            settings.setValue("PYLINT_MASTER_PERSISTENT", self.ui.PYLINT_MASTER_PERSISTENT.checkState())
            settings.setValue("PYLINT_MASTER_LOAD_PLUGINS", self.ui.PYLINT_MASTER_LOAD_PLUGINS.text())
            settings.setValue("PYLINT_MASTER_UNSAFE_LOAD_ANY_EXTENSION", self.ui.PYLINT_MASTER_UNSAFE_LOAD_ANY_EXTENSION.checkState())
            settings.setValue("PYLINT_MASTER_EXTENSION_PKG_WHITELIST", self.ui.PYLINT_MASTER_EXTENSION_PKG_WHITELIST.text())
            
            # MESSAGE CONTROL TAB
            btngroup_name = "PYLINT_MSGCONTROL_ENABLECHECKERS_SELECTIONTYPE_BTNGROUP"
            btngroup = getattr(self.ui, btngroup_name)
            for btn in btngroup.buttons():
                if btn.isChecked():
                    settings.setValue(btngroup_name, btn.text())
                    
            btngroup_name = "PYLINT_MSGCONTROL_ENABLEMSGCATEGORIES_SELECTIONTYPE_BTNGROUP"
            btngroup = getattr(self.ui, btngroup_name)
            for btn in btngroup.buttons():
                if btn.isChecked():
                    settings.setValue(btngroup_name, btn.text())
                    
            settings.setValue("PYLINT_MESSAGES_SETUP__ENABLE_MSGCATEGORIES_IDS", self.ui.PYLINT_MESSAGES_SETUP__ENABLE_MSGCATEGORIES_IDS.text())
            settings.setValue("PYLINT_MESSAGES_SETUP__DISABLE_MSGCATEGORIES_IDS", self.ui.PYLINT_MESSAGES_SETUP__DISABLE_MSGCATEGORIES_IDS.text())
                    
            btngroup_name = "PYLINT_MSGCONTROL_ENABLEMSGS_SELECTIONTYPE_BTNGROUP"
            btngroup = getattr(self.ui, btngroup_name)
            for btn in btngroup.buttons():
                if btn.isChecked():
                    settings.setValue(btngroup_name, btn.text())
          
            # REPORT TAB
            settings.setValue("PYLINT_REPORT_FORMAT", self.ui.PYLINT_REPORT_FORMAT.currentText())
            settings.setValue("PYLINT_REPORT_MSG_TEMPLATE", self.ui.PYLINT_REPORT_MSG_TEMPLATE.text())
            settings.setValue("PYLINT_REPORT_FILES_OUTPUT", self.ui.PYLINT_REPORT_FILES_OUTPUT.checkState())
            settings.setValue("PYLINT_REPORT_REPORTS", self.ui.PYLINT_REPORT_REPORTS.checkState())
            settings.setValue("PYLINT_REPORT_EVALUATION", self.ui.PYLINT_REPORT_EVALUATION.text())
            settings.setValue("PYLINT_REPORT_COMMENT", self.ui.PYLINT_REPORT_COMMENT.checkState())
            
            btngroup_name = "PYLINT_REPORTS_SELECTIONTYPE_BTNGROUP"
            btngroup = getattr(self.ui, btngroup_name)
            for btn in btngroup.buttons():
                if btn.isChecked():
                    settings.setValue(btngroup_name, btn.text())

            # BASIC TAB
            settings.setValue("PYLINT_BASIC_REQUIRED_ATTRIBUTES", self.ui.PYLINT_BASIC_REQUIRED_ATTRIBUTES.text())
            settings.setValue("PYLINT_BASIC_NO_DOCSTRING_RGX", self.ui.PYLINT_BASIC_NO_DOCSTRING_RGX.text())
            settings.setValue("PYLINT_BASIC_MODULE_RGX", self.ui.PYLINT_BASIC_MODULE_RGX.text())
            settings.setValue("PYLINT_BASIC_CONST_RGX", self.ui.PYLINT_BASIC_CONST_RGX.text())
            settings.setValue("PYLINT_BASIC_CLASS_RGX", self.ui.PYLINT_BASIC_CLASS_RGX.text())
            settings.setValue("PYLINT_BASIC_FUNCTION_RGX", self.ui.PYLINT_BASIC_FUNCTION_RGX.text())
            settings.setValue("PYLINT_BASIC_METHOD_RGX", self.ui.PYLINT_BASIC_METHOD_RGX.text())
            settings.setValue("PYLINT_BASIC_ATTRIBUTE_RGX", self.ui.PYLINT_BASIC_ATTRIBUTE_RGX.text())
            settings.setValue("PYLINT_BASIC_ARGUMENT_RGX", self.ui.PYLINT_BASIC_ARGUMENT_RGX.text())
            settings.setValue("PYLINT_BASIC_VARIABLE_RGX", self.ui.PYLINT_BASIC_VARIABLE_RGX.text())
            settings.setValue("PYLINT_BASIC_INLINEVAR_RGX", self.ui.PYLINT_BASIC_INLINEVAR_RGX.text())
            settings.setValue("PYLINT_BASIC_GOOD_NAMES", self.ui.PYLINT_BASIC_GOOD_NAMES.text())
            settings.setValue("PYLINT_BASIC_BAD_NAMES", self.ui.PYLINT_BASIC_BAD_NAMES.text())
            settings.setValue("PYLINT_BASIC_BAD_FUNCTIONS", self.ui.PYLINT_BASIC_BAD_FUNCTIONS.text())
            
            # CLASSES
            settings.setValue("PYLINT_CLASSES_IGNORE_IFACE_METHODS", self.ui.PYLINT_CLASSES_IGNORE_IFACE_METHODS.text())
            settings.setValue("PYLINT_CLASSES_DEFINING_ATTR_METHODS", self.ui.PYLINT_CLASSES_DEFINING_ATTR_METHODS.text())
            settings.setValue("PYLINT_CLASSES_VALID_CLASSMETHODS_FIRST_ARG", self.ui.PYLINT_CLASSES_VALID_CLASSMETHODS_FIRST_ARG.text())
            settings.setValue("PYLINT_CLASSES_VALID_METACLASS_CLASSMETHOD_FIRST_ARG", self.ui.PYLINT_CLASSES_VALID_METACLASS_CLASSMETHOD_FIRST_ARG.text())
            settings.setValue("PYLINT_CLASSES_EXCLUDE_PROTECTED", self.ui.PYLINT_CLASSES_EXCLUDE_PROTECTED.text())         

            # DESIGN TAB
            settings.setValue("PYLINT_DESIGN_MAX_ARGS", self.ui.PYLINT_DESIGN_MAX_ARGS.value())
            settings.setValue("PYLINT_DESIGN_MAX_LOCALS", self.ui.PYLINT_DESIGN_MAX_LOCALS.value())
            settings.setValue("PYLINT_DESIGN_MAX_RETURNS", self.ui.PYLINT_DESIGN_MAX_RETURNS.value())
            settings.setValue("PYLINT_DESIGN_MAX_BRANCHS", self.ui.PYLINT_DESIGN_MAX_BRANCHS.value())
            settings.setValue("PYLINT_DESIGN_MAX_STATEMENTS", self.ui.PYLINT_DESIGN_MAX_STATEMENTS.value())
            settings.setValue("PYLINT_DESIGN_MAX_PARENTS", self.ui.PYLINT_DESIGN_MAX_PARENTS.value())
            settings.setValue("PYLINT_DESIGN_MAX_ATTRIBUTES", self.ui.PYLINT_DESIGN_MAX_ATTRIBUTES.value())
            settings.setValue("PYLINT_DESIGN_MIN_PUBLIC_METHODS", self.ui.PYLINT_DESIGN_MIN_PUBLIC_METHODS.value())
            settings.setValue("PYLINT_DESIGN_MAX_PUBLIC_METHODS", self.ui.PYLINT_DESIGN_MAX_PUBLIC_METHODS.value())
            settings.setValue("PYLINT_DESIGN_IGNORE_ARGUMENTS_NAMES", self.ui.PYLINT_DESIGN_IGNORE_ARGUMENTS_NAMES.text())
            
            # FORMAT TAB
            settings.setValue("PYLINT_FORMAT_MAX_LINES_LENGTH", self.ui.PYLINT_FORMAT_MAX_LINES_LENGTH.value())
            settings.setValue("PYLINT_FORMAT_MAX_MODULE_LINES", self.ui.PYLINT_FORMAT_MAX_MODULE_LINES.value())
            settings.setValue("PYLINT_FORMAT_IGNORE_LONG_LINES", self.ui.PYLINT_FORMAT_IGNORE_LONG_LINES.text())
            settings.setValue("PYLINT_FORMAT_SINGLE_LINE_IF_STMT", self.ui.PYLINT_FORMAT_SINGLE_LINE_IF_STMT.checkState())
            settings.setValue("PYLINT_FORMAT_NO_SPACE_CHECK", self.ui.PYLINT_FORMAT_NO_SPACE_CHECK.text())
            settings.setValue("PYLINT_FORMAT_INDENT_STRING", self.ui.PYLINT_FORMAT_INDENT_STRING.currentText())
            settings.setValue("PYLINT_FORMAT_INDENT_AFTER_PAREN", self.ui.PYLINT_FORMAT_INDENT_AFTER_PAREN.value())
            settings.setValue("PYLINT_FORMAT_EXPECTED_LINE_ENDING_FORMAT", self.ui.PYLINT_FORMAT_EXPECTED_LINE_ENDING_FORMAT.currentText())

            # IMPORT TAB
            settings.setValue("PYLINT_IMPORTS_DEPRECATED_MODULES", self.ui.PYLINT_IMPORTS_DEPRECATED_MODULES.text())
            settings.setValue("PYLINT_IMPORTS_IMPORT_GRAPH", self.ui.PYLINT_IMPORTS_IMPORT_GRAPH.text())
            settings.setValue("PYLINT_IMPORTS_EXT_IMPORT_GRAPH", self.ui.PYLINT_IMPORTS_EXT_IMPORT_GRAPH.text())
            settings.setValue("PYLINT_IMPORTS_INT_IMPORT_GRAPH", self.ui.PYLINT_IMPORTS_INT_IMPORT_GRAPH.text())

            # LOGGING TAB
            settings.setValue("PYLINT_LOGGING_LOGGING_MODULES", self.ui.PYLINT_LOGGING_LOGGING_MODULES.text())
            
            # MISCELLANEOUS TAB
            settings.setValue("PYLINT_MISCELLANEOUS_NOTES", self.ui.PYLINT_MISCELLANEOUS_NOTES.text())
            
            # SIMILARITIES TAB
            settings.setValue("PYLINT_SIMILARITIES_MIN_SIMILARITY_LINES", self.ui.PYLINT_SIMILARITIES_MIN_SIMILARITY_LINES.value())
            settings.setValue("PYLINT_SIMILARITIES_IGNORE_COMMENTS", self.ui.PYLINT_SIMILARITIES_IGNORE_COMMENTS.checkState())
            settings.setValue("PYLINT_SIMILARITIES_IGNORE_DOCSTRINGS", self.ui.PYLINT_SIMILARITIES_IGNORE_DOCSTRINGS.checkState())
            settings.setValue("PYLINT_SIMILARITIES_IGNORE_IMPORTS", self.ui.PYLINT_SIMILARITIES_IGNORE_IMPORTS.checkState())
    
            # TYPECHECK TAB
            settings.setValue("PYLINT_TYPECHECK_IGNORE_MIXIN_MEMBERS", self.ui.PYLINT_TYPECHECK_IGNORE_MIXIN_MEMBERS.text())
            settings.setValue("PYLINT_TYPECHECK_IGNORED_MODULES", self.ui.PYLINT_TYPECHECK_IGNORED_MODULES.text())
            settings.setValue("PYLINT_TYPECHECK_IGNORED_CLASSES", self.ui.PYLINT_TYPECHECK_IGNORED_CLASSES.text())
            settings.setValue("PYLINT_TYPECHECK_ZOPE", self.ui.PYLINT_TYPECHECK_ZOPE.checkState())
            settings.setValue("PYLINT_TYPECHECK_GENERATED_MEMBERS", self.ui.PYLINT_TYPECHECK_GENERATED_MEMBERS.text())
    
            # VARIABLE TAB
            settings.setValue("PYLINT_VARIABLES_INIT_IMPORT", self.ui.PYLINT_VARIABLES_INIT_IMPORT.checkState())
            settings.setValue("PYLINT_VARIABLES_DUMMY_VARIABLES_RGX", self.ui.PYLINT_VARIABLES_DUMMY_VARIABLES_RGX.text())
            settings.setValue("PYLINT_VARIABLES_ADDITIONAL_BUILTINS", self.ui.PYLINT_VARIABLES_ADDITIONAL_BUILTINS.text())
            settings.setValue("PYLINT_VARIABLES_CALLBACKS", self.ui.PYLINT_VARIABLES_CALLBACKS.text())
            
            settings.endGroup()
            
            return
         
        settings.beginGroup("dialog_toolsconfig")
        settings.setValue("geometry", self.saveGeometry())
        settings.endGroup()
        
        settings_pylint()
        settings_pyflakes()
        settings_pymetrics()
            
    def set_setting(self, settings):
        '''
        '''
        def xSetCheckState(ctrl, check_val):
            ctrl.setCheckState({2:QtCore.Qt.Checked, 1:QtCore.Qt.Checked, 0:QtCore.Qt.Unchecked}[int(check_val)])
            
        def xSetValue(ctrl, spin_val):
            ctrl.setValue(int(spin_val))

        def xSetCurrentText(ctrl, combobox_val):
            items = []
            for i in range(ctrl.count()):
                items.append(ctrl.itemText(i))
            idx = items.index(combobox_val)
            ctrl.setCurrentIndex(idx)

        def settings_pyflakes():
            ''' '''
            settings.beginGroup("dialog_toolsconfig_pyflakes")
            for pyflakes_feature in self.pyflakes_features:
                btngroup_name = "PYFLAKES_%s_BTNGROUP" % pyflakes_feature
                btngroup = getattr(self.ui, btngroup_name)
                value = settings.value(btngroup_name, "Error")
                # last check
                if value not in ["Error", "Warning", "Info", "Debug"]:
                    value = "Error"
                btns = [ btn for btn in btngroup.buttons() if btn.text() == value ]
                if btns:
                    btns[0].setChecked(1)
                else:
                    pass
            settings.endGroup()
        
        def settings_pymetrics():
            ''' '''
            settings.beginGroup("dialog_toolsconfig_pymetrics")
            self.ui.PYMETRICS_BASIC.setCheckState({2:QtCore.Qt.Checked, 0:QtCore.Qt.Unchecked}[int(settings.value("PYMETRICS_BASIC", 2))])
            self.ui.PYMETRICS_SIMPLE.setCheckState({2:QtCore.Qt.Checked, 0:QtCore.Qt.Unchecked}[int(settings.value("PYMETRICS_SIMPLE", 2))])
            self.ui.PYMETRICS_MCCABE.setCheckState({2:QtCore.Qt.Checked, 0:QtCore.Qt.Unchecked}[int(settings.value("PYMETRICS_MCCABE", 2))])
            self.ui.PYMETRICS_SLOC.setCheckState({2:QtCore.Qt.Checked, 0:QtCore.Qt.Unchecked}[int(settings.value("PYMETRICS_SLOC", 2))])
            
            self.ui.PYMETRICS_OUTPUT_NOCSV.setCheckState({2:QtCore.Qt.Checked, 0:QtCore.Qt.Unchecked}[int(settings.value("PYMETRICS_OUTPUT_NOCSV", 2))])
            self.ui.PYMETRICS_OUTPUT_NOSQL.setCheckState({2:QtCore.Qt.Checked, 0:QtCore.Qt.Unchecked}[int(settings.value("PYMETRICS_OUTPUT_NOSQL", 2))])
            self.ui.PYMETRICS_OUTPUT_ZERO.setCheckState({2:QtCore.Qt.Checked, 0:QtCore.Qt.Unchecked}[int(settings.value("PYMETRICS_OUTPUT_ZERO", 0))])
            self.ui.PYMETRICS_OUTPUT_QUIET.setCheckState({2:QtCore.Qt.Checked, 0:QtCore.Qt.Unchecked}[int(settings.value("PYMETRICS_OUTPUT_QUIET", 0))])
            self.ui.PYMETRICS_OUTPUT_QUIETMODULEDOCSTRING.setCheckState({2:QtCore.Qt.Checked, 0:QtCore.Qt.Unchecked}[int(settings.value("PYMETRICS_OUTPUT_QUIETMODULEDOCSTRING", 0))])
            self.ui.PYMETRICS_OUTPUT_VERBOSE.setCheckState({2:QtCore.Qt.Checked, 0:QtCore.Qt.Unchecked}[int(settings.value("PYMETRICS_OUTPUT_VERBOSE", 0))])
            self.ui.PYMETRICS_OUTPUT_NOKWCNT.setCheckState({2:QtCore.Qt.Checked, 0:QtCore.Qt.Unchecked}[int(settings.value("PYMETRICS_OUTPUT_NOKWCNT", 0))])
            
            self.ui.PYMETRICS_OUTPUT_CSV_FILENAME.setText(settings.value("PYMETRICS_OUTPUT_CSV_FILENAME", ""))
            self.ui.PYMETRICS_OUTPUT_CSV_NOHEADINGS.setCheckState({2:QtCore.Qt.Checked, 0:QtCore.Qt.Unchecked}[int(settings.value("PYMETRICS_OUTPUT_CSV_NOHEADINGS", 2))])
            self.ui.PYMETRICS_OUTPUT_SQL_FILENAME.setText(settings.value("PYMETRICS_OUTPUT_SQL_FILENAME", ""))
            self.ui.PYMETRICS_OUTPUT_SQL_TOKENTABLE.setText(settings.value("PYMETRICS_OUTPUT_SQL_TOKENTABLE", "")) 
            self.ui.PYMETRICS_OUTPUT_SQL_METRICSTABLE.setText(settings.value("PYMETRICS_OUTPUT_SQL_METRICSTABLE", ""))
            self.ui.PYMETRICS_OUTPUT_SQL_EXISTS.setCheckState({2:QtCore.Qt.Checked, 0:QtCore.Qt.Unchecked}[int(settings.value("PYMETRICS_OUTPUT_SQL_EXISTS", 2))]) 
            self.ui.PYMETRICS_OUTPUT_SQL_NOOLD.setCheckState({2:QtCore.Qt.Checked, 0:QtCore.Qt.Unchecked}[int(settings.value("PYMETRICS_OUTPUT_SQL_NOOLD", 2))])
            
            
            self.ui.PYMETRICS_CUSTOM_EXTRAMODULES_TEXT.setText(settings.value("PYMETRICS_CUSTOM_EXTRAMODULES_TEXT", ""))
            self.ui.PYMETRICS_CUSTOM_EXTRAMETRICS_TEXT.setText(settings.value("PYMETRICS_CUSTOM_EXTRAMETRICS_TEXT", ""))
            self.ui.PYMETRICS_CUSTOM_USERDEFINEDLIBNAME_TEXT.setText(settings.value("PYMETRICS_CUSTOM_USERDEFINEDLIBNAME_TEXT", ""))
            
            self.ui.PYMETRICS_CUSTOM_EXTRAMODULES.setCheckState({2:QtCore.Qt.Checked, 0:QtCore.Qt.Unchecked}[int(settings.value("PYMETRICS_CUSTOM_EXTRAMODULES", 0))])
            self.ui.PYMETRICS_CUSTOM_EXTRAMETRICS.setCheckState({2:QtCore.Qt.Checked, 0:QtCore.Qt.Unchecked}[int(settings.value("PYMETRICS_CUSTOM_EXTRAMETRICS", 0))])
            self.ui.PYMETRICS_CUSTOM_USERDEFINEDLIBNAME.setCheckState({2:QtCore.Qt.Checked, 0:QtCore.Qt.Unchecked}[int(settings.value("PYMETRICS_CUSTOM_USERDEFINEDLIBNAME", 0))])
                
            settings.endGroup()
        
        def settings_pylint():
            ''' '''
            settings.beginGroup("dialog_toolsconfig_pylint")
            
            for message_type in self.pylint_features:
                for nb in self.pylint_features[message_type]:
                    cb = getattr(self.ui, "PYLINT_%s_%s" % (message_type, nb))
                    try:
                        xSetCheckState(cb, settings.value("PYLINT_%s_%s" % (message_type, nb)))
                    except Exception as _:
                        xSetCheckState(cb, 1)

            # MASTER TAB
            self.ui.PYLINT_MASTER_RCFILE.setText(settings.value("PYLINT_MASTER_RCFILE"))
            self.ui.PYLINT_MASTER_INITHOOK.setText(settings.value("PYLINT_MASTER_INITHOOK"))
            xSetCheckState(self.ui.PYLINT_MASTER_ERRORS_ONLY, settings.value("PYLINT_MASTER_ERRORS_ONLY"))
            xSetCheckState(self.ui.PYLINT_MASTER_PROFILE, settings.value("PYLINT_MASTER_PROFILE"))
            self.ui.PYLINT_MASTER_IGNORE.setText(settings.value("PYLINT_MASTER_IGNORE", "CVS"))
            xSetCheckState(self.ui.PYLINT_MASTER_PERSISTENT, settings.value("PYLINT_MASTER_PERSISTENT"))
            self.ui.PYLINT_MASTER_LOAD_PLUGINS.setText(settings.value("PYLINT_MASTER_LOAD_PLUGINS"))
            xSetCheckState(self.ui.PYLINT_MASTER_UNSAFE_LOAD_ANY_EXTENSION, settings.value("PYLINT_MASTER_UNSAFE_LOAD_ANY_EXTENSION"))
            self.ui.PYLINT_MASTER_EXTENSION_PKG_WHITELIST.setText(settings.value("PYLINT_MASTER_EXTENSION_PKG_WHITELIST"))
            
            # MESSAGE CONTROL TAB
            btngroup_name = "PYLINT_MSGCONTROL_ENABLECHECKERS_SELECTIONTYPE_BTNGROUP"
            btngroup = getattr(self.ui, btngroup_name)    
            value = settings.value(btngroup_name)
            btns = [ btn for btn in btngroup.buttons() if btn.text() == value ]
            if btns:
                btns[0].setChecked(1)
                    
            btngroup_name = "PYLINT_MSGCONTROL_ENABLEMSGCATEGORIES_SELECTIONTYPE_BTNGROUP"
            btngroup = getattr(self.ui, btngroup_name)
            value = settings.value(btngroup_name)
            btns = [ btn for btn in btngroup.buttons() if btn.text() == value ]
            if btns:
                btns[0].setChecked(1)
                
            self.ui.PYLINT_MESSAGES_SETUP__ENABLE_MSGCATEGORIES_IDS.setText(settings.value("PYLINT_MESSAGES_SETUP__ENABLE_MSGCATEGORIES_IDS","R,C,W,E,F"))
            self.ui.PYLINT_MESSAGES_SETUP__DISABLE_MSGCATEGORIES_IDS.setText(settings.value("PYLINT_MESSAGES_SETUP__DISABLE_MSGCATEGORIES_IDS","I"))
                    
            btngroup_name = "PYLINT_MSGCONTROL_ENABLEMSGS_SELECTIONTYPE_BTNGROUP"
            btngroup = getattr(self.ui, btngroup_name)
            value = settings.value(btngroup_name)
            btns = [ btn for btn in btngroup.buttons() if btn.text() == value ]
            if btns:
                btns[0].setChecked(1)
          
            # REPORT TAB
            xSetCurrentText(self.ui.PYLINT_REPORT_FORMAT ,settings.value("PYLINT_REPORT_FORMAT"))
            self.ui.PYLINT_REPORT_MSG_TEMPLATE.setText(settings.value("PYLINT_REPORT_MSG_TEMPLATE", "{msg_id}: {line},{column}: {msg}"))
            xSetCheckState(self.ui.PYLINT_REPORT_FILES_OUTPUT, settings.value("PYLINT_REPORT_FILES_OUTPUT"))
            xSetCheckState(self.ui.PYLINT_REPORT_REPORTS, settings.value("PYLINT_REPORT_REPORTS"))
            self.ui.PYLINT_REPORT_EVALUATION.setText(settings.value("PYLINT_REPORT_EVALUATION", "10.0 - ((float(5 * error + warning + refactor + convention) / statement) * 10)"))
            xSetCheckState(self.ui.PYLINT_REPORT_COMMENT, settings.value("PYLINT_REPORT_COMMENT"))
            
            btngroup_name = "PYLINT_REPORTS_SELECTIONTYPE_BTNGROUP"
            btngroup = getattr(self.ui, btngroup_name)
            value = settings.value(btngroup_name)
            btns = [ btn for btn in btngroup.buttons() if btn.text() == value ]
            if btns:
                btns[0].setChecked(1)

            # BASIC TAB
            self.ui.PYLINT_BASIC_REQUIRED_ATTRIBUTES.setText(settings.value("PYLINT_BASIC_REQUIRED_ATTRIBUTES", ""))
            self.ui.PYLINT_BASIC_NO_DOCSTRING_RGX.setText(settings.value("PYLINT_BASIC_NO_DOCSTRING_RGX", "__.*__"))
            self.ui.PYLINT_BASIC_MODULE_RGX.setText(settings.value("PYLINT_BASIC_MODULE_RGX", "(([a-z_][a-z0-9_]*)|([A-Z][a-zA-Z0-9]+))$"))
            self.ui.PYLINT_BASIC_CONST_RGX.setText(settings.value("PYLINT_BASIC_CONST_RGX", "(([A-Z_][A-Z0-9_]*)|(__.*__))$"))
            self.ui.PYLINT_BASIC_CLASS_RGX.setText(settings.value("PYLINT_BASIC_CLASS_RGX", "[A-Z_][a-zA-Z0-9]+$"))
            self.ui.PYLINT_BASIC_FUNCTION_RGX.setText(settings.value("PYLINT_BASIC_FUNCTION_RGX", "[a-z_][a-z0-9_]{2,30}$"))
            self.ui.PYLINT_BASIC_METHOD_RGX.setText(settings.value("PYLINT_BASIC_METHOD_RGX", "[a-z_][a-z0-9_]{2,30}$"))
            self.ui.PYLINT_BASIC_ATTRIBUTE_RGX.setText(settings.value("PYLINT_BASIC_ATTRIBUTE_RGX", "[a-z_][a-z0-9_]{2,30}$"))
            self.ui.PYLINT_BASIC_ARGUMENT_RGX.setText(settings.value("PYLINT_BASIC_ARGUMENT_RGX", "[a-z_][a-z0-9_]{2,30}$"))
            self.ui.PYLINT_BASIC_VARIABLE_RGX.setText(settings.value("PYLINT_BASIC_VARIABLE_RGX", "[a-z_][a-z0-9_]{2,30}$"))
            self.ui.PYLINT_BASIC_INLINEVAR_RGX.setText(settings.value("PYLINT_BASIC_INLINEVAR_RGX", "[A-Za-z_][A-Za-z0-9_]*$"))
            self.ui.PYLINT_BASIC_GOOD_NAMES.setText(settings.value("PYLINT_BASIC_GOOD_NAMES", "i,j,k,ex,Run,_"))
            self.ui.PYLINT_BASIC_BAD_NAMES.setText(settings.value("PYLINT_BASIC_BAD_NAMES", "foo,bar,baz,toto,tutu,tata"))
            self.ui.PYLINT_BASIC_BAD_FUNCTIONS.setText(settings.value("PYLINT_BASIC_BAD_FUNCTIONS", "map,filter,apply,input"))
            
            # CLASSES
            self.ui.PYLINT_CLASSES_IGNORE_IFACE_METHODS.setText(settings.value("PYLINT_CLASSES_IGNORE_IFACE_METHODS", ""))
            self.ui.PYLINT_CLASSES_DEFINING_ATTR_METHODS.setText(settings.value("PYLINT_CLASSES_DEFINING_ATTR_METHODS", "__init__,__new__"))
            self.ui.PYLINT_CLASSES_VALID_CLASSMETHODS_FIRST_ARG.setText(settings.value("PYLINT_CLASSES_VALID_CLASSMETHODS_FIRST_ARG", "cls"))
            self.ui.PYLINT_CLASSES_VALID_METACLASS_CLASSMETHOD_FIRST_ARG.setText(settings.value("PYLINT_CLASSES_VALID_METACLASS_CLASSMETHOD_FIRST_ARG", "mcs"))
            self.ui.PYLINT_CLASSES_EXCLUDE_PROTECTED.setText(settings.value("PYLINT_CLASSES_EXCLUDE_PROTECTED", "_asdict,_fields,_replace,_source,_make"))         

            # DESIGN TAB
            xSetValue(self.ui.PYLINT_DESIGN_MAX_ARGS, settings.value("PYLINT_DESIGN_MAX_ARGS", 5))
            xSetValue(self.ui.PYLINT_DESIGN_MAX_LOCALS, settings.value("PYLINT_DESIGN_MAX_LOCALS", 15))
            xSetValue(self.ui.PYLINT_DESIGN_MAX_RETURNS, settings.value("PYLINT_DESIGN_MAX_RETURNS", 6))
            xSetValue(self.ui.PYLINT_DESIGN_MAX_BRANCHS, settings.value("PYLINT_DESIGN_MAX_BRANCHS", 12))
            xSetValue(self.ui.PYLINT_DESIGN_MAX_STATEMENTS, settings.value("PYLINT_DESIGN_MAX_STATEMENTS", 50))
            xSetValue(self.ui.PYLINT_DESIGN_MAX_PARENTS, settings.value("PYLINT_DESIGN_MAX_PARENTS", 7))
            xSetValue(self.ui.PYLINT_DESIGN_MAX_ATTRIBUTES, settings.value("PYLINT_DESIGN_MAX_ATTRIBUTES", 10))
            xSetValue(self.ui.PYLINT_DESIGN_MIN_PUBLIC_METHODS, settings.value("PYLINT_DESIGN_MIN_PUBLIC_METHODS", 2))
            xSetValue(self.ui.PYLINT_DESIGN_MAX_PUBLIC_METHODS, settings.value("PYLINT_DESIGN_MAX_PUBLIC_METHODS", 20))
            self.ui.PYLINT_DESIGN_IGNORE_ARGUMENTS_NAMES.setText(settings.value("PYLINT_DESIGN_IGNORE_ARGUMENTS_NAMES", ""))
            
            # FORMAT TAB
            xSetValue(self.ui.PYLINT_FORMAT_MAX_LINES_LENGTH, settings.value("PYLINT_FORMAT_MAX_LINES_LENGTH", 80))
            xSetValue(self.ui.PYLINT_FORMAT_MAX_MODULE_LINES, settings.value("PYLINT_FORMAT_MAX_MODULE_LINES", 1000))
            self.ui.PYLINT_FORMAT_IGNORE_LONG_LINES.setText(settings.value("PYLINT_FORMAT_IGNORE_LONG_LINES", "^\\s*(# )?<?https?://\\S+>?$"))
            xSetCheckState(self.ui.PYLINT_FORMAT_SINGLE_LINE_IF_STMT, settings.value("PYLINT_FORMAT_SINGLE_LINE_IF_STMT", 0))
            self.ui.PYLINT_FORMAT_NO_SPACE_CHECK.setText(settings.value("PYLINT_FORMAT_NO_SPACE_CHECK", "trailing-comma,dict-separator"))
            xSetCurrentText(self.ui.PYLINT_FORMAT_INDENT_STRING, settings.value("PYLINT_FORMAT_INDENT_STRING", "4-SPACES"))
            xSetValue(self.ui.PYLINT_FORMAT_INDENT_AFTER_PAREN, settings.value("PYLINT_FORMAT_INDENT_AFTER_PAREN", 4))
            xSetCurrentText(self.ui.PYLINT_FORMAT_EXPECTED_LINE_ENDING_FORMAT, settings.value("PYLINT_FORMAT_EXPECTED_LINE_ENDING_FORMAT", "empty"))

            # IMPORT TAB
            self.ui.PYLINT_IMPORTS_IMPORT_GRAPH.setText(settings.value("PYLINT_IMPORTS_IMPORT_GRAPH", ""))
            self.ui.PYLINT_IMPORTS_EXT_IMPORT_GRAPH.setText(settings.value("PYLINT_IMPORTS_EXT_IMPORT_GRAPH", ""))
            self.ui.PYLINT_IMPORTS_INT_IMPORT_GRAPH.setText(settings.value("PYLINT_IMPORTS_INT_IMPORT_GRAPH", ""))
            self.ui.PYLINT_IMPORTS_DEPRECATED_MODULES.setText(settings.value("PYLINT_IMPORTS_DEPRECATED_MODULES", "regsub,string,TERMIOS,Bastion,rexec"))

            # LOGGING TAB
            self.ui.PYLINT_LOGGING_LOGGING_MODULES.setText(settings.value("PYLINT_LOGGING_LOGGING_MODULES", "logging"))
            
            # MISCELLANEOUS TAB
            self.ui.PYLINT_MISCELLANEOUS_NOTES.setText(settings.value("PYLINT_MISCELLANEOUS_NOTES", "FIXME,XXX,TODO"))
            
            # SIMILARITIES TAB
            xSetValue(self.ui.PYLINT_SIMILARITIES_MIN_SIMILARITY_LINES, settings.value("PYLINT_SIMILARITIES_MIN_SIMILARITY_LINES", 4))
            xSetCheckState(self.ui.PYLINT_SIMILARITIES_IGNORE_COMMENTS, settings.value("PYLINT_SIMILARITIES_IGNORE_COMMENTS", 0))
            xSetCheckState(self.ui.PYLINT_SIMILARITIES_IGNORE_DOCSTRINGS, settings.value("PYLINT_SIMILARITIES_IGNORE_DOCSTRINGS", 0))
            xSetCheckState(self.ui.PYLINT_SIMILARITIES_IGNORE_IMPORTS, settings.value("PYLINT_SIMILARITIES_IGNORE_IMPORTS", 0))
    
            # TYPECHECK TAB
            self.ui.PYLINT_TYPECHECK_IGNORE_MIXIN_MEMBERS.setText(settings.value("PYLINT_TYPECHECK_IGNORE_MIXIN_MEMBERS", ""))
            self.ui.PYLINT_TYPECHECK_IGNORED_MODULES.setText(settings.value("PYLINT_TYPECHECK_IGNORED_MODULES", ""))
            self.ui.PYLINT_TYPECHECK_IGNORED_CLASSES.setText(settings.value("PYLINT_TYPECHECK_IGNORED_CLASSES", "SQLObject"))
            xSetCheckState(self.ui.PYLINT_TYPECHECK_ZOPE, settings.value("PYLINT_TYPECHECK_ZOPE", 0))
            self.ui.PYLINT_TYPECHECK_GENERATED_MEMBERS.setText(settings.value("PYLINT_TYPECHECK_GENERATED_MEMBERS", "REQUEST,acl_users,aq_parent"))
    
            # VARIABLE TAB
            xSetCheckState(self.ui.PYLINT_VARIABLES_INIT_IMPORT, settings.value("PYLINT_VARIABLES_INIT_IMPORT", 0))
            self.ui.PYLINT_VARIABLES_DUMMY_VARIABLES_RGX.setText(settings.value("PYLINT_VARIABLES_DUMMY_VARIABLES_RGX", "_|dummy"))
            self.ui.PYLINT_VARIABLES_ADDITIONAL_BUILTINS.setText(settings.value("PYLINT_VARIABLES_ADDITIONAL_BUILTINS", ""))
            self.ui.PYLINT_VARIABLES_CALLBACKS.setText(settings.value("PYLINT_VARIABLES_CALLBACKS", "cb_,_cb"))

            settings.endGroup()
        
        
        settings.beginGroup("dialog_toolsconfig")
        self.restoreGeometry(settings.value("geometry"))
        settings.endGroup()
        
        settings_pylint()
        settings_pyflakes()
        settings_pymetrics()
            
    def set_callbacks(self):
        '''
        '''
        def pymetrics_callbacks():
            self.ui.PYMETRICS_OUTPUT_NOCSV.stateChanged.connect(self.cb_pymetrics_checkbox)
            self.ui.PYMETRICS_OUTPUT_NOSQL.stateChanged.connect(self.cb_pymetrics_checkbox)

            self.ui.PYMETRICS_CUSTOM_EXTRAMODULES.stateChanged.connect(self.cb_pymetrics_checkbox)
            self.ui.PYMETRICS_CUSTOM_EXTRAMETRICS.stateChanged.connect(self.cb_pymetrics_checkbox)
            self.ui.PYMETRICS_CUSTOM_USERDEFINEDLIBNAME.stateChanged.connect(self.cb_pymetrics_checkbox)
        
            # call them
            self.ui.PYMETRICS_OUTPUT_NOCSV.click()
            self.ui.PYMETRICS_OUTPUT_NOSQL.click()

            self.ui.PYMETRICS_CUSTOM_EXTRAMODULES.click()
            self.ui.PYMETRICS_CUSTOM_EXTRAMETRICS.click()
            self.ui.PYMETRICS_CUSTOM_USERDEFINEDLIBNAME.click()
            
        def pyflakes_callbacks():
            for pyflakes_feature in self.pyflakes_features:
            
                btn = "PYFLAKES_%s_RESETTODEFAULT" % pyflakes_feature
            
                ctrl = getattr(self.ui, btn)
                ctrl.clicked.connect(self.cb_pyflakes_buttons)
            
        def pylint_callbacks():
            self.ui.PYLINT_MESSAGES_SETUP__ENABLE_CHECKERS_IDS_RADIOBTN.clicked.connect(self.cb_pylint_radiobuttons)
            self.ui.PYLINT_MESSAGES_SETUP__DISABLE_CHECKERS_IDS_RADIOBTN.clicked.connect(self.cb_pylint_radiobuttons)
        
            self.ui.PYLINT_MESSAGES_SETUP__ENABLE_MSGCATEGORIES_IDS_RADIOBTN.clicked.connect(self.cb_pylint_radiobuttons)
            self.ui.PYLINT_MESSAGES_SETUP__DISABLE_MSGCATEGORIES_IDS_RADIOBTN.clicked.connect(self.cb_pylint_radiobuttons)
        
            self.ui.PYLINT_MESSAGES_SETUP__ENABLE_MSG_IDS_RADIOBTN.clicked.connect(self.cb_pylint_radiobuttons)
            self.ui.PYLINT_MESSAGES_SETUP__DISABLE_MSG_IDS_RADIOBTN.clicked.connect(self.cb_pylint_radiobuttons)
        
            self.ui.PYLINT_REPORTS_ENABLE_RB.clicked.connect(self.cb_pylint_radiobuttons)
            self.ui.PYLINT_REPORTS_DISABLE_RB.clicked.connect(self.cb_pylint_radiobuttons)
        
        
        pylint_callbacks()
        pyflakes_callbacks()
        pymetrics_callbacks()

    def cb_pylint_radiobuttons(self):
        ''' to finish ...
        '''
        def toggle_feature(feature):
            if feature == 'REPORT':
                for nb in self.pylint_features[feature]:
                    cb = getattr(self.ui, "PYLINT_%s_%s" % (feature, nb))
                    if cb.isChecked():
                        cb.setCheckState(QtCore.Qt.Unchecked)
                    else:
                        cb.setCheckState(QtCore.Qt.Checked)
            if feature == "MSGS":
                for f in ("FATAL", "ERROR" , "WARNING", "CONVENTION", "INFORMATION", "REFACTOR"):
                    for nb in self.pylint_features[f]:
                        cb = getattr(self.ui, "PYLINT_%s_%s" % (f, nb))
                        if cb.isChecked():
                            cb.setCheckState(QtCore.Qt.Unchecked)
                        else:
                            cb.setCheckState(QtCore.Qt.Checked)
        # -----------------------------------------------------------------------
        # -----------------------------------------------------------------------
        
        sender = self.sender()
        sender_name = sender.objectName()
        
        if sender_name in ("PYLINT_REPORTS_ENABLE_RB" , "PYLINT_REPORTS_DISABLE_RB"): 
            if self.ui.PYLINT_REPORTS_ENABLE_RB.isChecked():
                toggle_feature("REPORT")
            else:
                toggle_feature("REPORT")
            
        if sender_name in ("PYLINT_MESSAGES_SETUP__ENABLE_MSG_IDS_RADIOBTN" , "PYLINT_MESSAGES_SETUP__DISABLE_MSG_IDS_RADIOBTN"): 
            if self.ui.PYLINT_MESSAGES_SETUP__ENABLE_MSG_IDS_RADIOBTN.isChecked():
                toggle_feature("MSGS")
            else:
                toggle_feature("MSGS")
            
        self.update_ui("PyLint")
    
    def cb_pymetrics_checkbox(self):
        ''' '''
        sender = self.sender()
        sender_name = sender.objectName()
        
        self.update_ui("PyMetrics")  

    def cb_pyflakes_buttons(self):
        '''
        '''
        btn = self.sender()
        
        btnname = btn.objectName()
        
        pyflakes_feature = btnname.split("_")[1]
        default          = self.pyflakes_features[pyflakes_feature]["default"]

        radiobtn_name = "PYFLAKES_%s_RB_%s" % (pyflakes_feature, default) 
        
        ctrl = getattr(self.ui, radiobtn_name)
        ctrl.setChecked(1)
        
    def loadUi(self, uifile): 
        '''
        '''   
        class UiLoader(QUiLoader):
            """
            """
            def __init__(self, baseinstance):
                """
                """
                QUiLoader.__init__(self, baseinstance)
                self.baseinstance = baseinstance
        
            def createWidget(self, className, parent=None, name=""):
                import QColorButton
                
                widget = None
        
                # mayby QtUiTools.QUiLoader.availableWidgets(self) does not return your controls
                # ... should they have a "plugin" orsomethiong like that ? ...
                
                if className in QtUiTools.QUiLoader.availableWidgets(self):
                    widget = QtUiTools.QUiLoader.createWidget(self, className, parent, name)
                else:
                    classes = {
                       'QColorButton' : QColorButton.QColorButton,
                    }
                    widget_class = classes.get(className, None)
        
                    if widget_class:
                        widget = widget_class(parent)
                    else:
                        pass
                        # raise KeyError("Unknown widget '%s'" % className)
                    # else:
                    #    raise AttributeError("Trying to load custom widget '%s', but base instance '%s' does not specify custom widgets." % (className, repr(self.baseinstance)))
        
        
                if widget and self.baseinstance is not None:
                    setattr(self.baseinstance, name, widget)
        
                return widget


        loader = UiLoader(None)
    
        return loader.load(uifile)

    def closeEvent(self, event):
        '''
        '''
        self.hide()


    def get_command_options(self, tool):
        '''
        '''
        def pylint_command():
            analyserOpt = " "
        
            # ----------------- MASTER OPTIONS --------------------------------------------

            if self.ui.PYLINT_MASTER_RCFILE.text():
                analyserOpt = "--rcfile=%s " % self.ui.PYLINT_MASTER_RCFILE.text()
                return analyserOpt
        
            #if self.ui.PYLINT_MASTER_INITHOOK.text()                : analyserOpt += "--init-hook=%s " % self.ui.PYLINT_MASTER_INITHOOK.text()  # WHAT'S THIS ?
            if self.ui.PYLINT_MASTER_ERRORS_ONLY.isChecked()         : analyserOpt += "--errors-only "
            if self.ui.PYLINT_MASTER_PROFILE.isChecked()             : analyserOpt += "--profile=y "
            if self.ui.PYLINT_MASTER_IGNORE.text() != "CVS"          : analyserOpt += "--ignore=%s " % self.ui.PYLINT_MASTER_IGNORE.text()
            if not self.ui.PYLINT_MASTER_PERSISTENT.isChecked()      : analyserOpt += "--persistent=n "
            if self.ui.PYLINT_MASTER_LOAD_PLUGINS.text()             : analyserOpt += "--load-plugins=%s " % self.ui.PYLINT_MASTER_LOAD_PLUGINS.text()
            if self.ui.PYLINT_MASTER_UNSAFE_LOAD_ANY_EXTENSION.isChecked()  : analyserOpt += "--unsafe-load-any-extension=y "
            if self.ui.PYLINT_MASTER_EXTENSION_PKG_WHITELIST.text()  : analyserOpt += "--extension-pkg-whitelist=%s " % self.ui.PYLINT_MASTER_EXTENSION_PKG_WHITELIST.text()
        
            # ----------------- MESSAGES CTRL OPTIONS --------------------------------------------
        
            #btngroup = getattr(self.ui, "PYLINT_MSGCONTROL_ENABLECHECKERS_SELECTIONTYPE_BTNGROUP")
            #for btn in btngroup.buttons():
            #    if btn.isChecked():
            #        if btn.text().startswith("--enable"):
            #            analyserOpt = "--enable-checkers=%s" % ",".join(PYLINT_MESSAGES_SETUP__ENABLE_CHECKERS_IDS.text())
            #        else:
            #            analyserOpt = "--disable-checkers=%s" % ",".join(PYLINT_MESSAGES_SETUP__DISABLE_CHECKERS_IDS.text())
        
            btngroup = getattr(self.ui, "PYLINT_MSGCONTROL_ENABLEMSGCATEGORIES_SELECTIONTYPE_BTNGROUP")
            for btn in btngroup.buttons():
                if btn.isChecked():
                    if btn.text().startswith("--enable"):
                        analyserOpt += "--enable=%s " % ",".join(self.ui.PYLINT_MESSAGES_SETUP__ENABLE_MSGCATEGORIES_IDS.text())
                    else:
                        analyserOpt += "--disable=%s " % ",".join(self.ui.PYLINT_MESSAGES_SETUP__DISABLE_MSGCATEGORIES_IDS.text())
        
            all_msgs = []
            
            for message_type in self.pylint_features:
                if message_type == "REPORT":
                    continue  # done later
                if message_type[:1] in self.ui.PYLINT_MESSAGES_SETUP__DISABLE_MSGCATEGORIES_IDS.text().split(","):
                    continue  # filtered
                
                for nb in self.pylint_features[message_type]:
                    cb = getattr(self.ui, "PYLINT_%s_%s" % (message_type, nb))
                    if cb.isChecked():
                        
                        all_msgs.append("%s%s" % ( message_type[:1], nb))
                                    
            
            btngroup = getattr(self.ui, "PYLINT_MSGCONTROL_ENABLEMSGS_SELECTIONTYPE_BTNGROUP")
            for btn in btngroup.buttons():
                if btn.isChecked():
                    if btn.text().startswith("--enable"):
                        analyserOpt += "--enable=%s " % ",".join(all_msgs)
                    else:
                        analyserOpt += "--disable=%s " % ",".join(all_msgs)
        
            # ----------------- REPORT OPTIONS --------------------------------------------
            x = self.ui.PYLINT_REPORT_MSG_TEMPLATE.text()
            analyserOpt += "--msg-template=\"%s\" " % self.ui.PYLINT_REPORT_MSG_TEMPLATE.text()
        
            if self.ui.PYLINT_REPORT_FORMAT.currentText() != "text":      analyserOpt += "--output-format=%s " % self.ui.PYLINT_REPORT_FORMAT.currentText() 
            if self.ui.PYLINT_REPORT_FILES_OUTPUT.isChecked():            analyserOpt += "--files-output=y "
            if not self.ui.PYLINT_REPORT_REPORTS.isChecked():             analyserOpt += "--reports=n "
            if self.ui.PYLINT_REPORT_EVALUATION.text() != "10.0 - ((float(5 * error + warning + refactor + convention) / statement) * 10)":
                                                                          analyserOpt += "--evaluation=%s " % self.ui.PYLINT_REPORT_EVALUATION.text()  # HUMM...
            if self.ui.PYLINT_REPORT_COMMENT.isChecked():                 analyserOpt += "--comment=y "
        
            all_reports = []
        
            if self.ui.PYLINT_REPORT_0001.isChecked(): all_reports.append("RP0001")
            if self.ui.PYLINT_REPORT_0002.isChecked(): all_reports.append("RP0002")
            if self.ui.PYLINT_REPORT_0003.isChecked(): all_reports.append("RP0003")
            if self.ui.PYLINT_REPORT_0004.isChecked(): all_reports.append("RP0004")
            if self.ui.PYLINT_REPORT_0101.isChecked(): all_reports.append("RP0101")
            if self.ui.PYLINT_REPORT_0401.isChecked(): all_reports.append("RP0401")
            if self.ui.PYLINT_REPORT_0402.isChecked(): all_reports.append("RP0402")
            if self.ui.PYLINT_REPORT_0701.isChecked(): all_reports.append("RP0701")
            if self.ui.PYLINT_REPORT_0801.isChecked(): all_reports.append("RP0801")

            btngroup = getattr(self.ui, "PYLINT_REPORTS_SELECTIONTYPE_BTNGROUP")
            for btn in btngroup.buttons():
                if btn.isChecked():
                    if btn.text().startswith("--enable"):
                        analyserOpt += "--enable=%s " % ",".join(all_reports)
                    else:
                        analyserOpt += "--disable=%s " % ",".join(all_reports)
        
            # ---------------- BASIC OPTIONS --------------------------------------------
        
            if self.ui.PYLINT_BASIC_REQUIRED_ATTRIBUTES.text() != ""                                 : analyserOpt += "--required-attributes=%s " % self.ui.PYLINT_BASIC_REQUIRED_ATTRIBUTES.text()
            if self.ui.PYLINT_BASIC_NO_DOCSTRING_RGX.text() != "__.*__"                              : analyserOpt += "--no-docstrings-rgx=%s " % self.ui.PYLINT_BASIC_NO_DOCSTRING_RGX.text()
            if self.ui.PYLINT_BASIC_MODULE_RGX.text() != "(([a-z_][a-z0-9_]*)|([A-Z][a-zA-Z0-9]+))$" : analyserOpt += "--module-rgx=%s " % self.ui.PYLINT_BASIC_MODULE_RGX.text()
            if self.ui.PYLINT_BASIC_CONST_RGX.text() != "(([A-Z_][A-Z0-9_]*)|(__.*__))$"             : analyserOpt += "--const-rgx=%s " % self.ui.PYLINT_BASIC_CONST_RGX.text()
            if self.ui.PYLINT_BASIC_CLASS_RGX.text() != "[A-Z_][a-zA-Z0-9]+$"                        : analyserOpt += "--class-rgx=%s " % self.ui.PYLINT_BASIC_CLASS_RGX.text()
            if self.ui.PYLINT_BASIC_FUNCTION_RGX.text() != "[a-z_][a-z0-9_]{2,30}$"                  : analyserOpt += "--function-rgx=%s " % self.ui.PYLINT_BASIC_FUNCTION_RGX.text()
            if self.ui.PYLINT_BASIC_METHOD_RGX.text() != "[a-z_][a-z0-9_]{2,30}$"                    : analyserOpt += "--method-rgx=%s " % self.ui.PYLINT_BASIC_METHOD_RGX.text()
            if self.ui.PYLINT_BASIC_ATTRIBUTE_RGX.text() != "[a-z_][a-z0-9_]{2,30}$"                 : analyserOpt += "--attr-rgx=%s " % self.ui.PYLINT_BASIC_ATTRIBUTE_RGX.text()
            if self.ui.PYLINT_BASIC_ARGUMENT_RGX.text() != "[a-z_][a-z0-9_]{2,30}$"                  : analyserOpt += "--argument-rgx=%s " % self.ui.PYLINT_BASIC_ARGUMENT_RGX.text()
            if self.ui.PYLINT_BASIC_VARIABLE_RGX.text() != "[a-z_][a-z0-9_]{2,30}$"                  : analyserOpt += "--variable-rgx=%s " % self.ui.PYLINT_BASIC_VARIABLE_RGX.text()
            if self.ui.PYLINT_BASIC_INLINEVAR_RGX.text() != "[A-Za-z_][A-Za-z0-9_]*$"                : analyserOpt += "--inlinevar-rgx=%s " % self.ui.PYLINT_BASIC_INLINEVAR_RGX.text()
            if self.ui.PYLINT_BASIC_GOOD_NAMES.text() != "i,j,k,ex,Run,_"                            : analyserOpt += "--good-names=%s " % self.ui.PYLINT_BASIC_GOOD_NAMES.text()
            if self.ui.PYLINT_BASIC_BAD_NAMES.text() != "foo,bar,baz,toto,tutu,tata"                 : analyserOpt += "--bad-names=%s " % self.ui.PYLINT_BASIC_BAD_NAMES.text()
            if self.ui.PYLINT_BASIC_BAD_FUNCTIONS.text() != "map,filter,apply,input"                 : analyserOpt += "--bad-functions=%s " % self.ui.PYLINT_BASIC_BAD_FUNCTIONS.text()
        
            # ---------------- CLASSES OPTIONS --------------------------------------------
        
            if self.ui.PYLINT_CLASSES_IGNORE_IFACE_METHODS.text()                           : analyserOpt += "--ignore-iface-methods=%s " % self.ui.PYLINT_CLASSES_IGNORE_IFACE_METHODS.text()
            if self.ui.PYLINT_CLASSES_DEFINING_ATTR_METHODS.text() != "__init__,__new__"    : analyserOpt += "--defining-attr-methods=%s " % self.ui.PYLINT_CLASSES_DEFINING_ATTR_METHODS.text()
            if self.ui.PYLINT_CLASSES_VALID_CLASSMETHODS_FIRST_ARG.text() != "cls"          : analyserOpt += "--valid-classmethod-first-arg=%s " % self.ui.PYLINT_CLASSES_VALID_CLASSMETHODS_FIRST_ARG.text()
            if self.ui.PYLINT_CLASSES_VALID_METACLASS_CLASSMETHOD_FIRST_ARG.text() != "mcs" : analyserOpt += "--valid-metaclass-classmethod-first-arg=%s " % self.ui.PYLINT_CLASSES_VALID_METACLASS_CLASSMETHOD_FIRST_ARG.text()
            if self.ui.PYLINT_CLASSES_EXCLUDE_PROTECTED.text() != "_asdict,_fields,_replace,_source,_make" : analyserOpt += "--exclude-protected=%s " % self.ui.PYLINT_CLASSES_EXCLUDE_PROTECTED.text()
        
            # ---------------- DESIGN OPTIONS --------------------------------------------
        
            if self.ui.PYLINT_DESIGN_MAX_ARGS.value() != 5            : analyserOpt += "--max-args=%d " % self.ui.PYLINT_DESIGN_MAX_ARGS.value()
            if self.ui.PYLINT_DESIGN_MAX_LOCALS.value() != 15         : analyserOpt += "--max-locals=%d " % self.ui.PYLINT_DESIGN_MAX_LOCALS.value()
            if self.ui.PYLINT_DESIGN_MAX_RETURNS.value() != 6         : analyserOpt += "--max-returns=%d " % self.ui.PYLINT_DESIGN_MAX_RETURNS.value()
            if self.ui.PYLINT_DESIGN_MAX_BRANCHS.value() != 12        : analyserOpt += "--max-branchs=%d " % self.ui.PYLINT_DESIGN_MAX_BRANCHS.value()
            if self.ui.PYLINT_DESIGN_MAX_STATEMENTS.value() != 50     : analyserOpt += "--max-statements=%d " % self.ui.PYLINT_DESIGN_MAX_STATEMENTS.value()
            if self.ui.PYLINT_DESIGN_MAX_PARENTS.value() != 7         : analyserOpt += "--max-parents=%d " % self.ui.PYLINT_DESIGN_MAX_PARENTS.value()
            if self.ui.PYLINT_DESIGN_MAX_ATTRIBUTES.value() != 10     : analyserOpt += "--max-attributes=%d " % self.ui.PYLINT_DESIGN_MAX_ATTRIBUTES.value()
            if self.ui.PYLINT_DESIGN_MIN_PUBLIC_METHODS.value() != 2  : analyserOpt += "--min-public-methods=%d " % self.ui.PYLINT_DESIGN_MIN_PUBLIC_METHODS.value()
            if self.ui.PYLINT_DESIGN_MAX_PUBLIC_METHODS.value() != 20 : analyserOpt += "--max-public-methods=%d " % self.ui.PYLINT_DESIGN_MAX_PUBLIC_METHODS.value()
        
            if self.ui.PYLINT_DESIGN_IGNORE_ARGUMENTS_NAMES.text() != "" : analyserOpt += "--ignored-argument-names=%s " % self.ui.PYLINT_DESIGN_IGNORE_ARGUMENTS_NAMES.text()
        
            # ---------------- FORMAT OPTIONS --------------------------------------------
        
            if self.ui.PYLINT_FORMAT_MAX_LINES_LENGTH.value() != 80       : analyserOpt += "--max-line-length=%d " % self.ui.PYLINT_FORMAT_MAX_LINES_LENGTH.value()
            if self.ui.PYLINT_FORMAT_MAX_MODULE_LINES.value() != 1000     : analyserOpt += "--max-module-lines=%d " % self.ui.PYLINT_FORMAT_MAX_MODULE_LINES.value()
            if self.ui.PYLINT_FORMAT_IGNORE_LONG_LINES.text() != "^\s*(# )?<?https?://\S+>?$"       : analyserOpt += "--ignore-long-lines=%s " % self.ui.PYLINT_FORMAT_IGNORE_LONG_LINES.text()
            if self.ui.PYLINT_FORMAT_SINGLE_LINE_IF_STMT.isChecked() == True : analyserOpt += "--single-line-if-stmt=y "
            if self.ui.PYLINT_FORMAT_NO_SPACE_CHECK.text() != "trailing-comma,dict-separator"       : analyserOpt += "--no-space-check=%s " % self.ui.PYLINT_FORMAT_NO_SPACE_CHECK.text()
            
        
            if self.ui.PYLINT_FORMAT_INDENT_STRING.currentText() == "4-SPACES" : pass
            if self.ui.PYLINT_FORMAT_INDENT_STRING.currentText() == "TAB"      : analyserOpt += "--indent-string='\\t' "
        
            if self.ui.PYLINT_FORMAT_INDENT_AFTER_PAREN.value() != 4     : analyserOpt += "--indent-after-paren=%d " % self.ui.PYLINT_FORMAT_INDENT_AFTER_PAREN.value()
            if self.ui.PYLINT_FORMAT_EXPECTED_LINE_ENDING_FORMAT.currentText() != "empty"      : analyserOpt += "--expected-line-ending-format=%s " % self.ui.PYLINT_FORMAT_EXPECTED_LINE_ENDING_FORMAT.currentText()
        
            # ---------------- IMPORTS OPTIONS --------------------------------------------
        
            if self.ui.PYLINT_IMPORTS_IMPORT_GRAPH.text():                                                 analyserOpt += "--import-graph=%s " % self.ui.PYLINT_IMPORTS_IMPORT_GRAPH.text()
            if self.ui.PYLINT_IMPORTS_EXT_IMPORT_GRAPH.text():                                             analyserOpt += "--ext-import-graph=%s " % self.ui.PYLINT_IMPORTS_EXT_IMPORT_GRAPH.text()
            if self.ui.PYLINT_IMPORTS_INT_IMPORT_GRAPH.text():                                             analyserOpt += "--int_import_graph=%s " % self.ui.PYLINT_IMPORTS_INT_IMPORT_GRAPH.text()
            if self.ui.PYLINT_IMPORTS_DEPRECATED_MODULES.text() != "regsub,string,TERMIOS,Bastion,rexec" : analyserOpt += "--deprecated-modules=%s " % self.ui.PYLINT_IMPORTS_DEPRECATED_MODULES.text()
        
            # ---------------- LOGGING OPTIONS --------------------------------------------
        
            if self.ui.PYLINT_LOGGING_LOGGING_MODULES.text() != "logging":               analyserOpt += "--logging-modules=%s " % self.ui.PYLINT_LOGGING_LOGGING_MODULES.text()
        
            # ---------------- MISC OPTIONS --------------------------------------------
        
            if self.ui.PYLINT_MISCELLANEOUS_NOTES.text() != "FIXME,XXX,TODO":            analyserOpt += "--notes=%s " % self.ui.PYLINT_MISCELLANEOUS_NOTES.text()
        
            # ---------------- SIMILARITIES OPTIONS --------------------------------------------
        
            if self.ui.PYLINT_SIMILARITIES_MIN_SIMILARITY_LINES.value() != 4 : analyserOpt += "--min-similarity-lines=%d " % self.ui.PYLINT_SIMILARITIES_MIN_SIMILARITY_LINES.value()
            if not self.ui.PYLINT_SIMILARITIES_IGNORE_COMMENTS.isChecked():        analyserOpt += "--ignore-comments=n "
            if not self.ui.PYLINT_SIMILARITIES_IGNORE_DOCSTRINGS.isChecked():      analyserOpt += "--ignore-docstrings=n "
            if not self.ui.PYLINT_SIMILARITIES_IGNORE_IMPORTS.isChecked():         analyserOpt += "--ignore-imports=n "
        
            # ---------------- TYPECHECK OPTIONS --------------------------------------------
        
            if not self.ui.PYLINT_TYPECHECK_IGNORE_MIXIN_MEMBERS.isChecked():                      analyserOpt += "--ignore-mixin-members=n "
            if self.ui.PYLINT_TYPECHECK_IGNORED_MODULES.text() != "":                              analyserOpt += "--ignored-modules=%s " % self.ui.PYLINT_TYPECHECK_IGNORED_MODULES.text()
            if self.ui.PYLINT_TYPECHECK_IGNORED_CLASSES.text() != "SQLObject":                     analyserOpt += "--ignored-classes=%s " % self.ui.PYLINT_TYPECHECK_IGNORED_CLASSES.text()
            if self.ui.PYLINT_TYPECHECK_ZOPE.isChecked():                                          analyserOpt += "--zope=y "
            if self.ui.PYLINT_TYPECHECK_GENERATED_MEMBERS.text() != "REQUEST,acl_users,aq_parent": analyserOpt += "--generated-members=%s " % self.ui.PYLINT_TYPECHECK_GENERATED_MEMBERS.text()
        
            # ---------------- VARIABLES OPTIONS --------------------------------------------
        
            if self.ui.PYLINT_VARIABLES_INIT_IMPORT.isChecked():                 analyserOpt += "--init-import=y "
            if self.ui.PYLINT_VARIABLES_DUMMY_VARIABLES_RGX.text() != "_|dummy": analyserOpt += "--dummy-variables-rgx=%s " % self.ui.PYLINT_VARIABLES_DUMMY_VARIABLES_RGX.text()
            if self.ui.PYLINT_VARIABLES_ADDITIONAL_BUILTINS.text() != "":        analyserOpt += "--additional-builtins=%s " % self.ui.PYLINT_VARIABLES_ADDITIONAL_BUILTINS.text()
            if self.ui.PYLINT_VARIABLES_CALLBACKS.text() != "cb_,_cb":           analyserOpt += "--callbacks=%s " % self.ui.PYLINT_VARIABLES_CALLBACKS.text()
        
            # finally...
            return analyserOpt

        def pyflakes_command():
            return ""  # empty!

        def pymetrics_command():
            analyserOpt = " "

            # the METRICS
            if not self.ui.PYMETRICS_BASIC.isChecked():
                analyserOpt = analyserOpt + "--nobasic "
        
            metrics = []
        
            if self.ui.PYMETRICS_SIMPLE.isChecked():
                metrics.append("simple:SimpleMetric")
            if self.ui.PYMETRICS_MCCABE.isChecked():
                metrics.append("mccabe:McCabeMetric")
            if self.ui.PYMETRICS_SLOC.isChecked():
                metrics.append("sloc:SLOCMetric")
            #if self.ui.PYMETRICS_HALSTEAD:
            #    metrics.append("halstead:HalsteadMetric")
        
            analyserOpt = analyserOpt + "-i %s " % ",".join(metrics)
        
            # the OUTPUT
            if self.ui.PYMETRICS_OUTPUT_QUIETMODULEDOCSTRING.isChecked():
                analyserOpt = analyserOpt + "--quietmoduledocstring "
        
            if self.ui.PYMETRICS_OUTPUT_NOCSV.isChecked():
                analyserOpt = analyserOpt + "--nocsv "
            else:
                if self.ui.PYMETRICS_OUTPUT_CSV_FILENAME:
                    analyserOpt = analyserOpt + "-c %s " % self.ui.PYMETRICS_OUTPUT_CSV_FILENAME.text()
                if self.ui.PYMETRICS.OUTPUT_CSV_NOHEADINGS.isChecked():
                    analyserOpt = analyserOpt + "--noheadings "
        
            if self.ui.PYMETRICS_OUTPUT_NOSQL.isChecked():
                analyserOpt = analyserOpt + "--nosql "
            else:
                if self.ui.PYMETRICS_OUTPUT_SQL_FILENAME.text():
                    analyserOpt = analyserOpt + "-s %s " % self.ui.PYMETRICS_OUTPUT_SQL_FILENAME.text()
                if self.ui.PYMETRICS_OUTPUT_SQL_TOKENTABLE.text():
                    analyserOpt = analyserOpt + "-t %s " % self.ui.PYMETRICS_OUTPUT_SQL_TOKENTABLE.text()
                if self.ui.PYMETRICS_OUTPUT_SQL_METRICSTABLE.text():
                    analyserOpt = analyserOpt + "-m %s " % self.ui.PYMETRICS_OUTPUT_SQL_METRICSTABLE.text()
                #if self.ui.PYMETRICS.OUTPUT.sqltableexists:
                #    analyserOpt = analyserOpt + "--exists "
                #    analyserOpt = analyserOpt + "--noold "
                else:
                    if self.ui.PYMETRICS_OUTPUT_SQL_NOOLD.isChecked():
                        analyserOpt = analyserOpt + "--noold "
            
            if self.ui.PYMETRICS_OUTPUT_ZERO.checkState()   : analyserOpt = analyserOpt + "--zero "
            if self.ui.PYMETRICS_OUTPUT_QUIET.checkState()  : analyserOpt = analyserOpt + "--quiet "
            if self.ui.PYMETRICS_OUTPUT_VERBOSE.checkState(): analyserOpt = analyserOpt + "--verbose "
            if self.ui.PYMETRICS_OUTPUT_NOKWCNT.checkState(): analyserOpt = analyserOpt + "--nokwcnt "
            
            if self.ui.PYMETRICS_CUSTOM_EXTRAMODULES.isChecked():
                analyserOpt = analyserOpt + "--files=%s " % self.ui.PYMETRICS_CUSTOM_EXTRAMODULES_TEXT.text()
            if self.ui.PYMETRICS_CUSTOM_EXTRAMETRICS.isChecked():
                analyserOpt = analyserOpt + "--include=%s " % self.ui.PYMETRICS_CUSTOM_EXTRAMETRICS_TEXT.text()
            if self.ui.PYMETRICS_CUSTOM_USERDEFINEDLIBNAME.isChecked():
                analyserOpt = analyserOpt + "--library=%s " % self.ui.PYMETRICS_CUSTOM_USERDEFINEDLIBNAME_TEXT.text()
        
            return analyserOpt
        
        commands = {
            "pylint"    : pylint_command,
            "pyflakes"  : pyflakes_command,
            "pymetrics" : pymetrics_command,
        }
        
        return commands[tool]()
    

       
