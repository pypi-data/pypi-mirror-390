import wx
import numpy as np

class MyersonInkjetPanel(wx.Panel):
    def __init__(self, parent, root, materials):
        super().__init__(parent)
        self.root = root
        self.materials = materials

        min_bounds, max_bounds = self.root.bounding_box()
        self.min_bounds = np.array([min_bounds.x, min_bounds.y, min_bounds.z])
        self.max_bounds = np.array([max_bounds.x, max_bounds.y, max_bounds.z])

        sizer = wx.BoxSizer(wx.VERTICAL)

        # Project Folder
        path_label = wx.StaticText(self, label="Project Folder:")
        sizer.Add(path_label, 0, wx.ALL, 5)

        path_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.path_ctrl = wx.TextCtrl(self)
        path_sizer.Add(self.path_ctrl, 1, wx.EXPAND | wx.ALL, 5)
        browse_btn = wx.Button(self, label="Browse")
        browse_btn.Bind(wx.EVT_BUTTON, self.on_browse)
        path_sizer.Add(browse_btn, 0, wx.ALL, 5)
        sizer.Add(path_sizer, 0, wx.EXPAND)

        # Layer Height
        layer_label = wx.StaticText(self, label="Layer Height:")
        sizer.Add(layer_label, 0, wx.ALL, 5)
        self.layer_height_ctrl = wx.SpinCtrlDouble(self, min=0.0001, max=10.0, initial=0.046, inc=0.0001)
        self.layer_height_ctrl.SetDigits(4)
        sizer.Add(self.layer_height_ctrl, 0, wx.ALL | wx.EXPAND, 5)

        # DPI
        dpi_label = wx.StaticText(self, label="Printer Resolution (DPI):")
        sizer.Add(dpi_label, 0, wx.ALL, 5)
        dpi_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.x_dpi_ctrl = wx.SpinCtrl(self, min=1, max=600, initial=300)
        self.y_dpi_ctrl = wx.SpinCtrl(self, min=1, max=600, initial=300)
        dpi_sizer.Add(self.x_dpi_ctrl, 1, wx.EXPAND | wx.ALL, 5)
        dpi_sizer.Add(self.y_dpi_ctrl, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(dpi_sizer, 0, wx.EXPAND)

        # Taper Angle
        taper_label = wx.StaticText(self, label="Taper Angle:")
        sizer.Add(taper_label, 0, wx.ALL, 5)
        self.taper_angle_ctrl = wx.SpinCtrlDouble(self, min=0.0, max=45.0, initial=5.0, inc=0.1)
        sizer.Add(self.taper_angle_ctrl, 0, wx.ALL | wx.EXPAND, 5)

        # Extra Width
        extra_width_label = wx.StaticText(self, label="Extra Width:")
        sizer.Add(extra_width_label, 0, wx.ALL, 5)
        self.extra_width_ctrl = wx.SpinCtrlDouble(self, min=0.0, max=10.0, initial=1.0, inc=0.01)
        sizer.Add(self.extra_width_ctrl, 0, wx.ALL | wx.EXPAND, 5)

        # Sampling Info
        self.sampling_info_label = wx.StaticText(self, label="")
        sizer.Add(self.sampling_info_label, 0, wx.ALL, 5)

        for ctrl in [self.layer_height_ctrl, self.x_dpi_ctrl, self.y_dpi_ctrl]:
            ctrl.Bind(wx.EVT_SPINCTRL, self.on_update_sampling)
            ctrl.Bind(wx.EVT_SPINCTRLDOUBLE, self.on_update_sampling)

        self.update_sampling_info()
        self.SetSizer(sizer)

    def on_browse(self, event):
        with wx.DirDialog(self, "Choose a directory:", style=wx.DD_DEFAULT_STYLE) as dirDialog:
            if dirDialog.ShowModal() == wx.ID_CANCEL:
                return
            self.path_ctrl.SetValue(dirDialog.GetPath())

    def on_update_sampling(self, event):
        self.update_sampling_info()

    def update_sampling_info(self):
        vx = 25.4 / self.x_dpi_ctrl.GetValue()
        vy = 25.4 / self.y_dpi_ctrl.GetValue()
        vz = self.layer_height_ctrl.GetValue()

        size = self.max_bounds - self.min_bounds
        x_dim = int(np.ceil(size[0] / vx))
        y_dim = int(np.ceil(size[1] / vy))
        z_dim = int(np.ceil(size[2] / vz))

        sampling_info = (
            f"Sample Space Size: {size[0]:.3f} x {size[1]:.3f} x {size[2]:.3f} mm\n"
            f"Voxel Size: {vx:.3f} x {vy:.3f} x {vz:.3f} mm\n"
            f"Dimensions: {x_dim} x {y_dim} x {z_dim} (voxels)\n"
            f"Pixels per Layer: {x_dim * y_dim:,.0f}\n"
            f"Total Voxels: {x_dim * y_dim * z_dim:,.0f}"
        )
        self.sampling_info_label.SetLabel(sampling_info)

    def get_export_options(self):
        return {
            "output_directory": self.path_ctrl.GetValue(),
            "layer_height": self.layer_height_ctrl.GetValue(),
            "x_dpi": self.x_dpi_ctrl.GetValue(),
            "y_dpi": self.y_dpi_ctrl.GetValue(),
            "taper_angle": self.taper_angle_ctrl.GetValue(),
            "extra_width": self.extra_width_ctrl.GetValue(),
            "root": self.root,
            "materials": self.materials
        }
