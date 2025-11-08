import wx
import numpy as np

class VatPhotoPanel(wx.Panel):
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

        # Materials
        materials_label = wx.StaticText(self, label="Select materials:")
        sizer.Add(materials_label, 0, wx.ALL, 5)

        materials_in_design = self.root.material_list()
        material_names = [self.materials.name(m) for m in materials_in_design]

        low_material_label = wx.StaticText(self, label="Low Material:")
        sizer.Add(low_material_label, 0, wx.ALL, 5)
        self.low_material_combo = wx.ComboBox(self, choices=material_names, style=wx.CB_READONLY)
        sizer.Add(self.low_material_combo, 0, wx.ALL | wx.EXPAND, 5)

        high_material_label = wx.StaticText(self, label="High Material:")
        sizer.Add(high_material_label, 0, wx.ALL, 5)
        self.high_material_combo = wx.ComboBox(self, choices=material_names, style=wx.CB_READONLY)
        sizer.Add(self.high_material_combo, 0, wx.ALL | wx.EXPAND, 5)

        if "white" in material_names:
            self.high_material_combo.SetStringSelection("white")
        if "black" in material_names:
            self.low_material_combo.SetStringSelection("black")

        # Printer Build Volume
        printer_volume_label = wx.StaticText(self, label="Printer Build Volume (XYZ) in mm:")
        sizer.Add(printer_volume_label, 0, wx.ALL, 5)

        printer_volume_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.printer_volume_x = wx.SpinCtrlDouble(self, min=1.0, max=1000.0, initial=96.0)
        self.printer_volume_y = wx.SpinCtrlDouble(self, min=1.0, max=1000.0, initial=54.0)
        self.printer_volume_z = wx.SpinCtrlDouble(self, min=1.0, max=1000.0, initial=100.0)
        printer_volume_sizer.Add(self.printer_volume_x, 1, wx.EXPAND | wx.ALL, 5)
        printer_volume_sizer.Add(self.printer_volume_y, 1, wx.EXPAND | wx.ALL, 5)
        printer_volume_sizer.Add(self.printer_volume_z, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(printer_volume_sizer, 0, wx.EXPAND)

        # Voxel Size
        voxel_size_label = wx.StaticText(self, label="Voxel Size (XYZ) in microns:")
        sizer.Add(voxel_size_label, 0, wx.ALL, 5)

        voxel_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.voxel_size_x = wx.SpinCtrlDouble(self, min=1.0, max=100000.0, initial=50.0)
        self.voxel_size_y = wx.SpinCtrlDouble(self, min=1.0, max=100000.0, initial=50.0)
        self.voxel_size_z = wx.SpinCtrlDouble(self, min=1.0, max=100000.0, initial=100.0)
        voxel_sizer.Add(self.voxel_size_x, 1, wx.EXPAND | wx.ALL, 5)
        voxel_sizer.Add(self.voxel_size_y, 1, wx.EXPAND | wx.ALL, 5)
        voxel_sizer.Add(self.voxel_size_z, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(voxel_sizer, 0, wx.EXPAND)

        # Resolution Info
        self.resolution_info_label = wx.StaticText(self, label="")
        sizer.Add(self.resolution_info_label, 0, wx.ALL, 5)

        # Sampling Info
        self.sampling_info_label = wx.StaticText(self, label="")
        sizer.Add(self.sampling_info_label, 0, wx.ALL, 5)

        for ctrl in [self.printer_volume_x, self.printer_volume_y, self.voxel_size_x, self.voxel_size_y, self.voxel_size_z]:
            ctrl.Bind(wx.EVT_SPINCTRLDOUBLE, self.on_update_info)

        self.update_info()
        self.SetSizer(sizer)

    def on_browse(self, event):
        with wx.DirDialog(self, "Choose a directory:", style=wx.DD_DEFAULT_STYLE) as dirDialog:
            if dirDialog.ShowModal() == wx.ID_CANCEL:
                return
            self.path_ctrl.SetValue(dirDialog.GetPath())

    def on_update_info(self, event):
        self.update_info()

    def update_info(self):
        # Update resolution info
        x_res = int(np.ceil(self.printer_volume_x.GetValue() / (self.voxel_size_x.GetValue() / 1000.0)))
        y_res = int(np.ceil(self.printer_volume_y.GetValue() / (self.voxel_size_y.GetValue() / 1000.0)))
        self.resolution_info_label.SetLabel(f"Printer Resolution: {x_res} x {y_res} pixels")

        # Update sampling info
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
        self.Layout()

    def get_export_options(self):
        low_material_name = self.low_material_combo.GetValue()
        high_material_name = self.high_material_combo.GetValue()

        if low_material_name == high_material_name:
            wx.MessageBox("Low and High materials must be different.", "Invalid Selection", wx.OK | wx.ICON_WARNING)
            return None

        return {
            "output_directory": self.path_ctrl.GetValue(),
            "file_prefix": self.filename_ctrl.GetValue(),
            "low_material": self.materials.id(low_material_name),
            "high_material": self.materials.id(high_material_name),
            "printer_volume": np.array([
                self.printer_volume_x.GetValue(),
                self.printer_volume_y.GetValue(),
                self.printer_volume_z.GetValue()
            ]),
            "voxel_size": np.array([
                self.voxel_size_x.GetValue() / 1000.0,
                self.voxel_size_y.GetValue() / 1000.0,
                self.voxel_size_z.GetValue() / 1000.0
            ]),
            "root": self.root,
            "materials": self.materials
        }
