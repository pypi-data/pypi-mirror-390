import wx

class ColorInkjetPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.StaticText(self, label="Color Inkjet (PNG Stack)"), 0, wx.ALL, 5)
        self.SetSizer(sizer)

