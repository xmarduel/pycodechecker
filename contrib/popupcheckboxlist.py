#----------------------------------------------------------------------
import wx.combo
import string



class CheckListBoxComboPopup(wx.CheckListBox, wx.combo.ComboPopup):
        
    def __init__(self):

        # Also init the ComboPopup base class.
        wx.combo.ComboPopup.__init__(self)

	self.EndCreate()

    def EndCreate(self):    
	self.sep = ''
	# Since we are using multiple inheritance, and don't know yet
        # which window is to be the parent, we'll do 2-phase create of
        # the ListCtrl instead, and call its Create method later in
        # our Create method.  (See Create below.)
        self.PostCreate(wx.PreCheckListBox())

    def AddItem(self, txt):
        self.InsertItems( [txt], 0 )
        self.values = self.GetStrings()

    def OnMotion(self, evt):
	item, flags = self.HitTest(evt.GetPosition())
        evt.Skip()

    def OnLeftDown(self, evt):
        evt.Skip()


    # The following methods are those that are overridable from the
    # ComboPopup base class.  Most of them are not required, but all
    # are shown here for demonstration purposes.


    # This is called immediately after construction finishes.  You can
    # use self.GetCombo if needed to get to the ComboCtrl instance.
    def Init(self):
        pass

    # Create the popup child control.  Return true for success.
    def Create(self, parent):
        wx.CheckListBox.Create(self, parent)
        self.Bind(wx.EVT_MOTION, self.OnMotion)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        #
        self.InsertItems( ["A", "B", "C", "D", "E"], 0 )
        self.values = self.GetStrings()
        #
        return True


    # Return the widget that is to be used for the popup
    def GetControl(self):
        return self

    # Called just prior to displaying the popup, you can use it to
    # 'select' the current item.
    def SetStringValue(self, val):
	combo = self.GetCombo()
        value = map(string.strip, combo.GetValue().split(self.sep))
        if value == ['']: value = []

        # clean
	for i in range(self.GetCount()):
            self.Check(i, False)

        # setup
	for i in value:
            self.Check(self.values.index(i))

        wx.combo.ComboPopup.OnPopup(self)


    # Return a string representation of the current item.
    def GetStringValue(self):
        combo = self.GetCombo()
        value = []
        for i in range(self.GetCount()):
            if self.IsChecked(i):
                value.append(self.values[i])
        #
        strValue = self.sep.join(value)
        if combo.GetValue() != strValue:
            combo.SetValue(strValue)


    # Called immediately after the popup is shown
    def OnPopup(self):
        wx.combo.ComboPopup.OnPopup(self)

    # Called when popup is dismissed
    def OnDismiss(self):
        self.GetStringValue()
        wx.combo.ComboPopup.OnDismiss(self)

    # This is called to custom paint in the combo control itself
    # (ie. not the popup).  Default implementation draws value as
    # string.
    def PaintComboControl(self, dc, rect):
        wx.combo.ComboPopup.PaintComboControl(self, dc, rect)

    # Receives key events from the parent ComboCtrl.  Events not
    # handled should be skipped, as usual.
    def OnComboKeyEvent(self, event):
        wx.combo.ComboPopup.OnComboKeyEvent(self, event)

    # Implement if you need to support special action when user
    # double-clicks on the parent wxComboCtrl.
    def OnComboDoubleClick(self):
        wx.combo.ComboPopup.OnComboDoubleClick(self)

    # Return final size of popup. Called on every popup, just prior to OnPopup.
    # minWidth = preferred minimum width for window
    # prefHeight = preferred height. Only applies if > 0,
    # maxHeight = max height for window, as limited by screen size
    #   and should only be rounded down, if necessary.
    def GetAdjustedSize(self, minWidth, prefHeight, maxHeight):
        return wx.combo.ComboPopup.GetAdjustedSize(self, minWidth, self.GetCount()*16, maxHeight)

    # Return true if you want delay the call to Create until the popup
    # is shown for the first time. It is more efficient, but note that
    # it is often more convenient to have the control created
    # immediately.    
    # Default returns false.
    def LazyCreate(self):
        return wx.combo.ComboPopup.LazyCreate(self)

class XrcCheckListBoxComboPopup(CheckListBoxComboPopup):
    '''
    '''
    def __init__(self):
        '''
        '''
        p = wx.PreComboBox()
        # the Create step is done by XRC.
        self.PostCreate(p)
        self.EndCreate()
        
