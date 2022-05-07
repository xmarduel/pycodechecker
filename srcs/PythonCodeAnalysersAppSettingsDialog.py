
'''
COPYRIGHT (C) XAM GmbH

MODULE DESCRIPTION:
    The Application Configuration Dialog.
'''

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

from PySide2.QtUiTools import QUiLoader

from PySide2.QtCore import QMetaObject

#----------------------------------------------------------------

class ConfigDialog(QtWidgets.QDialog):
    '''
    Description:
    '''
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
        self.loadUi("PythonCodeAnalysersAppSettingsDialogUI.ui")
        
        # delete dummy tabs from the ui
        count = self.NOTEBOOK_INFOSETS.count()
        while count:
            idx  = self.NOTEBOOK_INFOSETS.currentIndex()
        
            page = self.NOTEBOOK_INFOSETS.widget(idx)
            name = self.NOTEBOOK_INFOSETS.tabText(idx)

            self.NOTEBOOK_INFOSETS.removeTab(idx)
            
            count -= 1
            
        # setup the tree FS browser to show only python files 
        tree = self.TREE_FILESYSTEM
        
        rootpath = QtCore.QDir("C:\\")
        
        rootpath_name = rootpath.dirName()
        
        model = QtWidgets.QFileSystemModel()
        model.setFilter(QtCore.QDir.Dirs | QtCore.QDir.Files)
        model.setNameFilters(["*.py"])
        model.setRootPath(rootpath_name)
        tree.setModel(model)
        tree.setRootIndex(model.index(rootpath_name))
        
        tree.hideColumn(1)
        tree.hideColumn(2)
        tree.hideColumn(3)

    def write_settings(self, settings):
        '''
        '''
        settings.beginGroup("dialog_fileinfoset_editor")
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("MAIN_SPLITTER", self.MAIN_SPLITTER.saveState())
        settings.endGroup()
        
        settings.beginGroup("dialog_fileinfoset_editor_data")
        settings.setValue("tools_run_order_file_per_file", self.RB_FILE_PER_FILE.isChecked())
        settings.setValue("tools_run_order_tool_per_tool", self.RB_TOOL_PER_TOOL.isChecked())
        settings.setValue("pylint_run_order", self.TOOL_PYLINT_RUN_ORDER.value())
        settings.setValue("pyflakes_run_order", self.TOOL_PYFLAKES_RUN_ORDER.value())
        settings.setValue("pymetrics_run_order", self.TOOL_PYMETRICS_RUN_ORDER.value())
        settings.endGroup()
        
        settings.beginGroup("dialog_fileinfoset_editor_filesinfosets")
        # write list of all infosets
        all_filesinfosets = self.get_all_filesinfosets()
        settings.beginWriteArray("filesinfoset")
        for k, filesinfoset in enumerate(all_filesinfosets):
            settings.setArrayIndex(k)
            settings.setValue("name", filesinfoset.name)
            settings.beginWriteArray("fileinfo")
            
            nb_items = filesinfoset.rowCount()
            for p in range(nb_items):
                idx = filesinfoset.index(p, 0)
                item_text  = filesinfoset.data(idx, QtCore.Qt.DisplayRole)
                item_state = filesinfoset.data(idx, QtCore.Qt.CheckStateRole)
            
                settings.setArrayIndex(p)
                settings.setValue("path", item_text)
                settings.setValue("activ", item_state)
            settings.endArray()
        settings.endArray()
        settings.endGroup()

    def set_setting(self, settings):
        '''
        '''
        settings.beginGroup("dialog_fileinfoset_editor")
        self.restoreGeometry(settings.value("geometry"))
        self.MAIN_SPLITTER.restoreState(settings.value("MAIN_SPLITTER"))
        settings.endGroup()
        
        settings.beginGroup("dialog_fileinfoset_editor_data")
        if settings.value("tools_run_order_file_per_file") == "true":
            self.RB_FILE_PER_FILE.setChecked(True)
        else:
            self.RB_FILE_PER_FILE.setChecked(False)
        if settings.value("tools_run_order_tool_per_tool") == "true":
            self.RB_TOOL_PER_TOOL.setChecked(True)
        else:
            self.RB_TOOL_PER_TOOL.setChecked(False)
        
        self.TOOL_PYLINT_RUN_ORDER.setValue(int(settings.value("pylint_run_order", 1)))
        self.TOOL_PYFLAKES_RUN_ORDER.setValue(int(settings.value("pyflakes_run_order", 2)))
        self.TOOL_PYMETRICS_RUN_ORDER.setValue(int(settings.value("pymetrics_run_order", 3)))
        settings.endGroup()
        
        settings.beginGroup("dialog_fileinfoset_editor_filesinfosets")

        size = settings.beginReadArray("filesinfoset")
        for i in range(size):
            settings.setArrayIndex(i)
            name = settings.value("name")
            filesinfoset = FilesInfoSet(name)
            nb_infoset = settings.beginReadArray("fileinfo")
            for j in range(nb_infoset):
                settings.setArrayIndex(j)
                filesinfoset.append_fileinfo(settings.value("path"), int(settings.value("activ")))
            settings.endArray()
            self.addpage_filesinfoset(filesinfoset)
        settings.endArray()
        
        # ok, now setup all the tabs of the notebook...
        
    def set_callbacks(self):
        '''
        '''
        self.INFOSET_RENAME.clicked.connect(self.cb_rename_filesinfoset)
        self.INFOSET_NEW.clicked.connect(self.cb_new_filesinfoset)
        self.INFOSET_DELETE.clicked.connect(self.cb_delete_filesinfoset)

        self.INFOSET_SELECT_ALL.clicked.connect(self.cb_selectall_in_filesinfoset)
        self.INFOSET_UNSELECT_ALL.clicked.connect(self.cb_unselectall_in_filesinfoset)
        self.INFOSET_TOGGLE_SELECTIONS.clicked.connect(self.cb_toggleall_in_filesinfoset)
        self.INFOSET_SORT_ITEMS.clicked.connect(self.cb_sortall_in_filesinfoset)
        
        self.INFOSET_REMOVE_UNSELECTED_ITEMS.clicked.connect(self.cb_remove_all_unselected)
         
        self.TREE_FILESYSTEM.dlg = self
        keyPressEater = TreeViewKeyPressEater(self.TREE_FILESYSTEM)
        self.TREE_FILESYSTEM.installEventFilter(keyPressEater)
    
    def cb_remove_all_unselected(self):
        '''
        '''
        filesinfoset = self.get_selected_filesinfoset()
        
        nb_items = filesinfoset.rowCount()
        
        items_to_remove = []

        for p in range(nb_items):
            idx = filesinfoset.index(p, 0)
            
            item_state = filesinfoset.data(idx, QtCore.Qt.CheckStateRole)
            
            if item_state == QtCore.Qt.Unchecked:
                items_to_remove.append(idx.row())

        items_to_remove.reverse()
        
        for row in items_to_remove:
            filesinfoset.removeRow(row)
    
    def cb_add_file_to_filesinfoset(self):
        '''
        '''
        idx = self.TREE_FILESYSTEM.currentIndex()
        
        path = self.TREE_FILESYSTEM.model().filePath(idx)
        
        filesinfoset = self.get_selected_filesinfoset()
        filesinfoset.append_fileinfo(path, True)
        
        return True
    
    def get_selected_filesinfoset(self):
        '''
        '''
        idx = self.NOTEBOOK_INFOSETS.currentIndex()
        
        page = self.NOTEBOOK_INFOSETS.widget(idx)
        
        return page.model()
    
    def get_all_filesinfosets(self):
        '''
        '''
        # from the ui, get the all the notebook pages models
        count = self.NOTEBOOK_INFOSETS.count()
        
        models = []
        
        for i in range(count):
            page = self.NOTEBOOK_INFOSETS.widget(i)
            
            model = page.model()
            models.append(model)
            
        return models
   
    def addpage_filesinfoset(self, model):
        '''
        '''
        # create a new notebook page
        page = QtWidgets.QListView(self.NOTEBOOK_INFOSETS)
        page.setModel(model)
        
        self.NOTEBOOK_INFOSETS.addTab(page, model.name)
        self.NOTEBOOK_INFOSETS.setCurrentWidget(page)

    def cb_new_filesinfoset(self):
        '''
        '''
        text, ok = QtWidgets.QInputDialog.getText(self, "Enter Name for a New FilesInfoSet",
                "FilesInfoSet:", 
                QtWidgets.QLineEdit.Normal,
                QtCore.QDir.home().dirName())
        
        if ok and text != '':
            filesinfoset = FilesInfoSet(text)
            filesinfoset.append_fileinfo("C:\\toto1.py", True)
            filesinfoset.append_fileinfo("C:\\toto2.py", False)
            filesinfoset.append_fileinfo("C:\\toto3.py", True)
            
            self.addpage_filesinfoset(filesinfoset)
            
            # and add an entry in the main window combobox
            self.parent().ui.CHOICE_FILES_DATASET.addItem(filesinfoset.name)

    def cb_delete_filesinfoset(self):
        '''
        '''
        idx  = self.NOTEBOOK_INFOSETS.currentIndex()
        
        page = self.NOTEBOOK_INFOSETS.widget(idx)
        name = self.NOTEBOOK_INFOSETS.tabText(idx)

        ok = QtGui.QMessageBox(None, 'Are you sure you want to delete %s' % name , 'FilesInfoSet Delete')

        if ok:

            self.NOTEBOOK_INFOSETS.removeTab(idx)
            
            # and remove the entry in the main window combobox
            ctrl = self.parent().ui.CHOICE_FILES_DATASET
            text_idx = {}
            for index in range(ctrl.count()):
                text_idx[ctrl.itemText(index)] = index
            ctrl.removeItem(text_idx[name])

    def cb_selectall_in_filesinfoset(self):
        '''
        '''
        filesinfoset = self.get_selected_filesinfoset()
        
        nb_items = filesinfoset.rowCount()
        for p in range(nb_items):
            idx = filesinfoset.index(p, 0)
            filesinfoset.setData(idx, QtCore.Qt.Checked, QtCore.Qt.CheckStateRole)

    def cb_unselectall_in_filesinfoset(self):
        '''
        '''
        filesinfoset = self.get_selected_filesinfoset()
        
        nb_items = filesinfoset.rowCount()
        for p in range(nb_items):
            idx = filesinfoset.index(p, 0)
            filesinfoset.setData(idx, QtCore.Qt.Unchecked, QtCore.Qt.CheckStateRole)

    def cb_toggleall_in_filesinfoset(self):
        '''
        '''
        filesinfoset = self.get_selected_filesinfoset()
        
        nb_items = filesinfoset.rowCount()
        for p in range(nb_items):
            idx = filesinfoset.index(p, 0)
            
            item_state = filesinfoset.data(idx, QtCore.Qt.CheckStateRole)
            
            if item_state == QtCore.Qt.Checked:
                filesinfoset.setData(idx, QtCore.Qt.Unchecked, QtCore.Qt.CheckStateRole)
            else:
                filesinfoset.setData(idx, QtCore.Qt.Checked, QtCore.Qt.CheckStateRole)

    def cb_sortall_in_filesinfoset(self):
        '''
        '''
        filesinfoset = self.get_selected_filesinfoset()

        # TODO

    def cb_rename_filesinfoset(self):
        '''
        '''
        filesinfoset = self.get_selected_filesinfoset()

        old_name = filesinfoset.name
        
        new_name, ok = QtGui.QInputDialog.getText(self, "Enter New Name for FilesInfoSet",
                "FilesInfoSet:", 
                QtGui.QLineEdit.Normal,
                old_name)
        
        if ok and new_name != '':

            filesinfoset.name = new_name

            idx = self.NOTEBOOK_INFOSETS.currentIndex()
            
            self.NOTEBOOK_INFOSETS.setTabText(idx, filesinfoset.name)

            self.parent().update_combobox(old_name, new_name)

    def get_infoset_data(self, name):
        ''' '''
        # from the ui, get the all the notebook pages models
        count = self.NOTEBOOK_INFOSETS.count()
        
        for i in range(count):
            page = self.NOTEBOOK_INFOSETS.widget(i)
            
            if page.model().name == name:
                return page.model()
            
        return None
        
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
                if parent is None and self.baseinstance:
                    # supposed to create the top-level widget, return the base instance
                    # instead
                    return self.baseinstance
                else:
                    # create a new widget for child widgets
                    widget = QUiLoader.createWidget(self, class_name, parent, name)
                    if self.baseinstance:
                        # set an attribute for the new child widget on the base
                        # instance, just like PyQt4.uic.loadUi does.
                        setattr(self.baseinstance, name, widget)
                    return widget
            
        loader = UiLoader(self)
        widget = loader.load(uifile)
        QMetaObject.connectSlotsByName(widget)
        return widget 

    def set_current_infoset(self, name):
        '''
        '''
        count = self.NOTEBOOK_INFOSETS.count()
        
        for i in range(count):
            page = self.NOTEBOOK_INFOSETS.widget(i)
            
            model = page.model()

            if model.name == name:
                self.NOTEBOOK_INFOSETS.setCurrentWidget(page)

# -----------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------

class FilesInfoSet(QtGui.QStandardItemModel):
    '''
    '''
    def __init__(self, name):
        '''
        '''
        super(FilesInfoSet, self).__init__()
        
        self.name = name

    def append_fileinfo(self, name, checked):
        '''
        '''
        item = QtGui.QStandardItem(name)
        item.setCheckable(True)
        
        if checked:
            item.setCheckState(QtCore.Qt.Checked)
        else:
            item.setCheckState(QtCore.Qt.Unchecked)
        
        self.appendRow(item)
        
    def get_selected_paths(self):
        '''
        '''
        selected_paths = []
        
        nb_items = self.rowCount()
        
        for p in range(nb_items):
            idx = self.index(p, 0)
            
            item_state = self.data(idx, QtCore.Qt.CheckStateRole)
            
            if item_state == QtCore.Qt.Checked:
                selected_paths.append(self.data(idx, QtCore.Qt.DisplayRole))
            else:
                pass
            
        return selected_paths

# -----------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------

class TreeViewKeyPressEater(QtCore.QObject):
    '''
    '''
    def eventFilter(self, treeview, event):
        '''
        Args:
            obj: the tree view
            event : qt event
        '''
        if event.type() == QtCore.QEvent.KeyPress:
            
            keyseq = self.getKeySequenceFromKeyEvent(event)
            keyadd = QtGui.QKeySequence(43)
            
            if keyseq == keyadd:
                return treeview.dlg.cb_add_file_to_filesinfoset()
                
            return QtCore.QObject.eventFilter(self, treeview, event)
        else:
            # standard event processing
            return QtCore.QObject.eventFilter(self, treeview, event)

    def getKeySequenceFromKeyEvent(self, event):
        ''' '''
        key = event.key()
        
        if key == QtCore.Qt.Key_unknown:
            #self.logger.log("DEBUG", "Single click : Unknown")
            return
    
        # the user have clicked just and only the special keys Ctrl, Shift, Alt, Meta.
        if(key == QtCore.Qt.Key_Control or
                key == QtCore.Qt.Key_Shift or
                key == QtCore.Qt.Key_Alt or
                key == QtCore.Qt.Key_Meta):
            #self.logger.log("DEBUG", "Single click of special key: Ctrl, Shift, Alt or Meta")
            #self.logger.log("DEBUG", "New KeySequence: %s" % QtGui.QKeySequence(key).toString(QtGui.QKeySequence.NativeText))
            return
    
        # check for a combination of user clicks
        modifiers = event.modifiers()
        #keyText = event.text()
        # if the keyText is empty than it's a special key like F1, F5, ...
        #self.logger.log("DEBUG", "Pressed Key: %s" % keyText)
    
        if modifiers & QtCore.Qt.ShiftModifier:
            key += QtCore.Qt.SHIFT
        if modifiers & QtCore.Qt.ControlModifier:
            key += QtCore.Qt.CTRL
        if modifiers & QtCore.Qt.AltModifier:
            key += QtCore.Qt.ALT
        if modifiers & QtCore.Qt.MetaModifier:
            key += QtCore.Qt.META
    
        return QtGui.QKeySequence(key)

# -----------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------
