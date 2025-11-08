import wx
import numpy as np

class MeshesPanel(wx.Panel):
    def __init__(self, parent, root, materials):
        super().__init__(parent)
        self.root = root
        self.materials = materials

        sizer = wx.BoxSizer(wx.VERTICAL)

        # Path
        path_label = wx.StaticText(self, label="Path:")
        sizer.Add(path_label, 0, wx.ALL, 5)

        path_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.path_ctrl = wx.TextCtrl(self)
        path_sizer.Add(self.path_ctrl, 1, wx.EXPAND | wx.ALL, 5)
        browse_btn = wx.Button(self, label="Browse")
        browse_btn.Bind(wx.EVT_BUTTON, self.on_browse)
        path_sizer.Add(browse_btn, 0, wx.ALL, 5)
        sizer.Add(path_sizer, 0, wx.EXPAND)

        # Sample Resolution
        sample_resolution_label = wx.StaticText(self, label="Sample Resolution (Min Feature Size) in mm:")
        sizer.Add(sample_resolution_label, 0, wx.ALL, 5)
        self.sample_resolution_ctrl = wx.SpinCtrlDouble(self, min=0.01, max=100.0, initial=1.0, inc=0.01)
        self.sample_resolution_ctrl.SetDigits(2)
        sizer.Add(self.sample_resolution_ctrl, 0, wx.ALL | wx.EXPAND, 5)

        # Geometry Only
        self.geometry_only_check = wx.CheckBox(self, label="Export Geometry Only")
        self.geometry_only_check.Bind(wx.EVT_CHECKBOX, self.on_toggle_geometry_only)
        sizer.Add(self.geometry_only_check, 0, wx.ALL, 5)

        # Filename
        filename_label = wx.StaticText(self, label="Filename:")
        sizer.Add(filename_label, 0, wx.ALL, 5)

        filename_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.filename_ctrl = wx.TextCtrl(self)
        filename_sizer.Add(self.filename_ctrl, 1, wx.EXPAND | wx.ALL, 5)
        extension_label = wx.StaticText(self, label="_XX.stl")
        filename_sizer.Add(extension_label, 0, wx.ALL, 5)
        sizer.Add(filename_sizer, 0, wx.EXPAND)

        # Number of Slices
        self.number_of_slices_label = wx.StaticText(self, label="Number of Material Iso Slices:")
        sizer.Add(self.number_of_slices_label, 0, wx.ALL, 5)
        self.number_of_slices_ctrl = wx.TextCtrl(self)
        sizer.Add(self.number_of_slices_ctrl, 0, wx.ALL | wx.EXPAND, 5)

        self.SetSizer(sizer)

    def on_browse(self, event):
        with wx.DirDialog(self, "Choose a directory:",
                           style=wx.DD_DEFAULT_STYLE) as dirDialog:
            if dirDialog.ShowModal() == wx.ID_CANCEL:
                return
            self.path_ctrl.SetValue(dirDialog.GetPath())

    def on_toggle_geometry_only(self, event):
        is_geometry_only = event.IsChecked()
        self.number_of_slices_label.Enable(not is_geometry_only)
        self.number_of_slices_ctrl.Enable(not is_geometry_only)

    def get_export_options(self):
        num_slices = 1
        if not self.geometry_only_check.IsChecked():
            try:
                num_slices = int(self.number_of_slices_ctrl.GetValue())
            except ValueError:
                wx.MessageBox("Number of slices must be an integer.", "Error", wx.OK | wx.ICON_ERROR)
                return None

        return {
            "output_directory": self.path_ctrl.GetValue(),
            "file_prefix": self.filename_ctrl.GetValue(),
            "sample_resolution": self.sample_resolution_ctrl.GetValue(),
            "num_slices": num_slices,
            "root": self.root,
            "materials": self.materials
        }
