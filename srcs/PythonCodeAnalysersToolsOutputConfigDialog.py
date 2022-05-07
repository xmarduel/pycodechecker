
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
    pylint_buttons = {
        "PYLINT_FATAL_COLOR":          "magenta",
        "PYLINT_ERROR_COLOR":          "red",
        "PYLINT_WARNING_COLOR":        "orange",
        "PYLINT_INFORMATION_COLOR":    "green",
        "PYLINT_CONVENTION_COLOR":     "green",
        "PYLINT_REFACTOR_COLOR":       "blue",
    }
    
    pyflakes_buttons = {
        "PYFLAKES_FATAL_COLOR":        "magenta",
        "PYFLAKES_ERROR_COLOR":        "red",
        "PYFLAKES_WARNING_COLOR":      "orange",
        "PYFLAKES_INFORMATION_COLOR":  "green",
    }

    pymetrics_buttons = {
        "PYMETRICS_HEADER_MODULE_NO_DOCSTRING_COLOR":             "red",
        
        "PYMETRICS_HEADER_EXTRAEXITS_SMALLER_LOWERLIMIT_COLOR":   "blue",
        "PYMETRICS_HEADER_EXTRAEXITS_BETWEENLIMITS_COLOR":        "orange",
        "PYMETRICS_HEADER_EXTRAEXITS_BIGGER_UPPERLIMIT_COLOR":    "red",
        
        "PYMETRICS_BASIC_NUMBERS_COLOR":            "blue",
        
        "PYMETRICS_BASIC_DOCSTRINGS_PERCENTAGE_LOWERLIMIT_COLOR":      "red",
        "PYMETRICS_BASIC_DOCSTRINGS_PERCENTAGE_BETWEENLIMITS_COLOR":   "orange",
        "PYMETRICS_BASIC_DOCSTRINGS_PERCENTAGE_UPPERLIMIT_COLOR":      "blue",
       
        "PYMETRICS_BASIC_COMMENTS_PERCENTAGE_LOWERLIMIT_COLOR":        "red",
        "PYMETRICS_BASIC_COMMENTS_PERCENTAGE_BETWEENLIMITS_COLOR":     "orange",
        "PYMETRICS_BASIC_COMMENTS_PERCENTAGE_UPPERLIMIT_COLOR":        "blue",
        
        "PYMETRICS_DOCSTRING_YES_COLOR":           "blue",
        "PYMETRICS_DOCSTRING_NO_COLOR":            "red",
        
        "PYMETRICS_SLOC_LOWERLIMIT_COLOR":         "blue",
        "PYMETRICS_SLOC_BETWEENLIMITS_COLOR":      "orange",
        "PYMETRICS_SLOC_UPPERLIMIT_COLOR":         "red",
    
        "PYMETRICS_MCCABE_LOWERLIMIT_COLOR":       "blue",
        "PYMETRICS_MCCABE_BETWEENLIMITS_COLOR":    "orange",
        "PYMETRICS_MCCABE_UPPERLIMIT_COLOR":       "red",                
    }
    
    pymetrics_sliders = {
        "PYMETRICS_HEADER_EXTRAEXITS_LOWERLIMIT_SLIDER": 10,
        "PYMETRICS_HEADER_EXTRAEXITS_UPPERLIMIT_SLIDER": 20,
 
        "PYMETRICS_BASIC_DOCSTRINGS_LOWERLIMIT_SLIDER": 75,
        "PYMETRICS_BASIC_DOCSTRINGS_UPPERLIMIT_SLIDER": 90,
        
        "PYMETRICS_BASIC_COMMENTS_PERCENTAGE_LOWERLIMIT_SLIDER": 5,
        "PYMETRICS_BASIC_COMMENTS_PERCENTAGE_UPPERLIMIT_SLIDER": 10,
            
        "PYMETRICS_SLOC_LOWERLIMIT_SLIDER": 250,
        "PYMETRICS_SLOC_UPPERLIMIT_SLIDER": 1000,
        
        "PYMETRICS_MCCABE_LOWERLIMIT_SLIDER": 10,
        "PYMETRICS_MCCABE_UPPERLIMIT_SLIDER": 20,
    }
    
    
    def __init__(self, parent):
        '''
        '''
        super(ConfigDialog, self).__init__(parent)

        # dialog content
        self.make_ui()
        # initialize content
        self.set_setting(parent.settings)
        # setup callbacks
        self.set_callbacks()
        
    def make_ui(self):
        '''
        '''
        self.ui = self.loadUi("PythonCodeAnalysersToolsOutputConfigDialogUI.ui")

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(self.ui)
        
        self.setLayout(mainLayout)
        
        # min / max annotation for the sliders ... not supported in pyside ...
        for slider in self.pymetrics_sliders:
            min_annotation_ctrl = getattr(self.ui, slider + "_MINVALUE")
            max_annotation_ctrl = getattr(self.ui, slider + "_MAXVALUE")
            
            ctrl = getattr(self.ui, slider)
            
            minval = ctrl.minimum()
            maxval = ctrl.maximum()
            
            min_annotation_ctrl.setText(str(minval))
            max_annotation_ctrl.setText(str(maxval))
    
    def set_callbacks(self):
        '''
        '''
        for tool in ("pylint", "pyflakes", "pymetrics"):
            for button_name in getattr(self, "%s_buttons" % tool):
                reset_button_name = button_name.replace("COLOR", "RESETCOLOR")
            
                ctrl = getattr(self.ui, reset_button_name)
                ctrl.clicked.connect(self.cb_resetcolor)
        
    def write_settings(self, settings):
        '''
        '''
        def settings_pylint():
            settings.beginGroup("dialog_outputconfig_pylint")
            for button_name in self.pylint_buttons:
                ctrl = getattr(self.ui, button_name)
                settings.setValue(button_name, ctrl.color())
            settings.endGroup()      
        
        def settings_pyflakes():
            settings.beginGroup("dialog_outputconfig_pyflakes")
            for button_name in self.pyflakes_buttons:
                ctrl = getattr(self.ui, button_name)
                settings.setValue(button_name, ctrl.color())
            settings.endGroup()        
        
        def settings_pymetrics():
            settings.beginGroup("dialog_outputconfig_pymetrics")
            for button_name in self.pymetrics_buttons:
                ctrl = getattr(self.ui, button_name)
                settings.setValue(button_name, ctrl.color())
            for slider_name in self.pymetrics_sliders:
                ctrl = getattr(self.ui, slider_name)
                settings.setValue(slider_name, ctrl.value())
            settings.endGroup()
        
        settings.beginGroup("dialog_outputconfig")
        settings.setValue("geometry", self.saveGeometry())
        settings.endGroup()
        
        settings_pylint()
        settings_pyflakes()
        settings_pymetrics()

    def set_setting(self, settings):
        '''
        setup dialog from settings, this is called only once
        '''
        def settings_pylint():
            settings.beginGroup("dialog_outputconfig_pylint")
            for button_name in self.pylint_buttons:
                ctrl = getattr(self.ui, button_name)
                ctrl.setColor(settings.value(button_name))
            settings.endGroup()    
        
        def settings_pyflakes():
            settings.beginGroup("dialog_outputconfig_pyflakes")
            for button_name in self.pyflakes_buttons:
                ctrl = getattr(self.ui, button_name)
                ctrl.setColor(settings.value(button_name))
            settings.endGroup()        
        
        def settings_pymetrics():
            settings.beginGroup("dialog_outputconfig_pymetrics")
            for button_name in self.pymetrics_buttons:
                ctrl = getattr(self.ui, button_name)
                ctrl.setColor(settings.value(button_name))
            for slider_name in self.pymetrics_sliders:
                ctrl = getattr(self.ui, slider_name)
                ctrl.setValue(int(settings.value(slider_name)))
            settings.endGroup()
            
        settings.beginGroup("dialog_outputconfig")
        self.restoreGeometry(settings.value("geometry"))
        settings.endGroup()
        
        settings_pylint()
        settings_pyflakes()
        settings_pymetrics()
    
    def cb_resetcolor(self):
        '''
        '''
        all_buttons = {}
        all_buttons.update(self.pyflakes_buttons)
        all_buttons.update(self.pymetrics_buttons)
        all_buttons.update(self.pylint_buttons) 
        
        try:
            sname = self.sender().objectName()
            
            k = sname.find("RESET") 
            ctrlname = sname[:k] + sname[k+5:]
            ctrl = getattr(self.ui, ctrlname)
            
            ctrl.setColor(all_buttons[ctrlname])
            
        except Exception as msg:
            pass
        
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