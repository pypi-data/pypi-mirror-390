import wx
import numpy as np

class DirectMaterialInkjetPanel(wx.Panel):
    def __init__(self, parent, root, materials):
        super().__init__(parent)
        self.root = root
        self.materials = materials

        min_bounds, max_bounds = self.root.bounding_box()
        self.min_bounds = np.array([min_bounds.x, min_bounds.y, min_bounds.z])
        self.max_bounds = np.array([max_bounds.x, max_bounds.y, max_bounds.z])

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

        # Filename
        filename_label = wx.StaticText(self, label="Filename:")
        sizer.Add(filename_label, 0, wx.ALL, 5)

        filename_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.filename_ctrl = wx.TextCtrl(self)
        filename_sizer.Add(self.filename_ctrl, 1, wx.EXPAND | wx.ALL, 5)
        extension_label = wx.StaticText(self, label="XX.png")
        filename_sizer.Add(extension_label, 0, wx.ALL, 5)
        sizer.Add(filename_sizer, 0, wx.EXPAND)

        # Liquid Keepout
        self.liquid_keepout_check = wx.CheckBox(self, label="Enable Liquid Keepout")
        self.liquid_keepout_check.Bind(wx.EVT_CHECKBOX, self.on_toggle_keepout)
        sizer.Add(self.liquid_keepout_check, 0, wx.ALL, 5)

        self.keepout_distance_ctrl = wx.SpinCtrlDouble(self, min=0.0, max=100.0, inc=0.1)
        self.keepout_distance_ctrl.SetValue(0.0)
        self.keepout_distance_ctrl.Enable(False)
        sizer.Add(self.keepout_distance_ctrl, 0, wx.ALL | wx.EXPAND, 5)

        # Voxel Size
        voxel_size_label = wx.StaticText(self, label="Voxel Size (XYZ) in microns:")
        sizer.Add(voxel_size_label, 0, wx.ALL, 5)

        voxel_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.voxel_size_x = wx.SpinCtrlDouble(self, min=1.0, max=100000.0, initial=42.3)
        self.voxel_size_y = wx.SpinCtrlDouble(self, min=1.0, max=100000.0, initial=84.6)
        self.voxel_size_z = wx.SpinCtrlDouble(self, min=1.0, max=100000.0, initial=27.0)
        voxel_sizer.Add(self.voxel_size_x, 1, wx.EXPAND | wx.ALL, 5)
        voxel_sizer.Add(self.voxel_size_y, 1, wx.EXPAND | wx.ALL, 5)
        voxel_sizer.Add(self.voxel_size_z, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(voxel_sizer, 0, wx.EXPAND)

        for ctrl in [self.voxel_size_x, self.voxel_size_y, self.voxel_size_z]:
            ctrl.Bind(wx.EVT_SPINCTRLDOUBLE, self.on_voxel_size_change)

        # Sampling Info
        self.sampling_info_label = wx.StaticText(self, label="")
        self.update_sampling_info()
        sizer.Add(self.sampling_info_label, 0, wx.ALL, 5)

        self.SetSizer(sizer)

    def on_browse(self, event):
        with wx.DirDialog(self, "Choose a directory:",
                           style=wx.DD_DEFAULT_STYLE) as dirDialog:
            if dirDialog.ShowModal() == wx.ID_CANCEL:
                return
            self.path_ctrl.SetValue(dirDialog.GetPath())

    def on_toggle_keepout(self, event):
        self.keepout_distance_ctrl.Enable(event.IsChecked())

    def on_voxel_size_change(self, event):
        self.update_sampling_info()

    def update_sampling_info(self):
        size = self.max_bounds - self.min_bounds
        voxel_size_mm = np.array([
            self.voxel_size_x.GetValue() / 1000.0,
            self.voxel_size_y.GetValue() / 1000.0,
            self.voxel_size_z.GetValue() / 1000.0
        ])

        total_voxels = (size[0] / voxel_size_mm[0]) * (size[1] / voxel_size_mm[1]) * (size[2] / voxel_size_mm[2])

        sampling_info = (f"Sample Space Size: {size[0]:.2f} x {size[1]:.2f} x {size[2]:.2f} mm\n"
                         f"Total Voxels: {total_voxels:,.0f}")
        self.sampling_info_label.SetLabel(sampling_info)

    def get_export_options(self):
        return {
            "output_directory": self.path_ctrl.GetValue(),
            "file_prefix": self.filename_ctrl.GetValue(),
            "liquid_keepout": self.liquid_keepout_check.IsChecked(),
            "liquid_keepout_distance": self.keepout_distance_ctrl.GetValue(),
            "voxel_size": np.array([
                self.voxel_size_x.GetValue(),
                self.voxel_size_y.GetValue(),
                self.voxel_size_z.GetValue()
            ]),
            "root": self.root,
            "materials": self.materials
        }
