import wx
import numpy as np

class FiniteElementMeshPanel(wx.Panel):
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

        # Element Type
        element_type_label = wx.StaticText(self, label="Element Type:")
        sizer.Add(element_type_label, 0, wx.ALL, 5)
        self.element_type_combo = wx.ComboBox(self, choices=["Tetrahedron (C3D4)", "Brick (C3D8)"], style=wx.CB_READONLY)
        self.element_type_combo.SetSelection(0)
        self.element_type_combo.Bind(wx.EVT_COMBOBOX, self.on_element_type_change)
        sizer.Add(self.element_type_combo, 0, wx.ALL | wx.EXPAND, 5)

        # Brick Options
        self.brick_group_box = wx.StaticBox(self, label="Brick Element (C3D8) Options")
        self.brick_group_box.Hide()
        brick_sizer = wx.StaticBoxSizer(self.brick_group_box, wx.VERTICAL)

        brick_grid = wx.GridSizer(2, 3, 5, 5)
        brick_grid.Add(wx.StaticText(self.brick_group_box, label="X Cells:"), 0, wx.ALIGN_CENTER_VERTICAL)
        brick_grid.Add(wx.StaticText(self.brick_group_box, label="Y Cells:"), 0, wx.ALIGN_CENTER_VERTICAL)
        brick_grid.Add(wx.StaticText(self.brick_group_box, label="Z Cells:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.x_dim_ctrl = wx.TextCtrl(self.brick_group_box)
        self.y_dim_ctrl = wx.TextCtrl(self.brick_group_box)
        self.z_dim_ctrl = wx.TextCtrl(self.brick_group_box)
        brick_grid.Add(self.x_dim_ctrl, 1, wx.EXPAND)
        brick_grid.Add(self.y_dim_ctrl, 1, wx.EXPAND)
        brick_grid.Add(self.z_dim_ctrl, 1, wx.EXPAND)
        brick_sizer.Add(brick_grid, 0, wx.EXPAND | wx.ALL, 5)

        self.num_elements_label = wx.StaticText(self.brick_group_box, label="Number of Elements: 0")
        brick_sizer.Add(self.num_elements_label, 0, wx.ALL, 5)

        self.use_volumetric_dither_check = wx.CheckBox(self.brick_group_box, label="Use Volumetric Dither")
        brick_sizer.Add(self.use_volumetric_dither_check, 0, wx.ALL, 5)

        for ctrl in [self.x_dim_ctrl, self.y_dim_ctrl, self.z_dim_ctrl]:
            ctrl.Bind(wx.EVT_TEXT, self.on_brick_dim_change)

        sizer.Add(brick_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # Tetrahedral Options
        self.tetra_group_box = wx.StaticBox(self, label="Tetrahedron Element (C3D4) Options")
        tetra_sizer = wx.StaticBoxSizer(self.tetra_group_box, wx.VERTICAL)

        # Voxel Size
        voxel_size_sizer = wx.BoxSizer(wx.HORIZONTAL)
        voxel_size_sizer.Add(wx.StaticText(self.tetra_group_box, label="Sample Size (mm):"), 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        self.voxel_size_ctrl = wx.SpinCtrlDouble(self.tetra_group_box, min=0.000001, max=100.0, initial=0.1, inc=0.000001)
        self.voxel_size_ctrl.SetDigits(6)
        voxel_size_sizer.Add(self.voxel_size_ctrl, 1, wx.EXPAND | wx.ALL, 5)
        auto_compute_btn = wx.Button(self.tetra_group_box, label="Auto-compute")
        auto_compute_btn.Bind(wx.EVT_BUTTON, self.on_auto_compute)
        voxel_size_sizer.Add(auto_compute_btn, 0, wx.ALL, 5)
        tetra_sizer.Add(voxel_size_sizer, 0, wx.EXPAND)

        # Variable Mesh Size
        self.use_variable_mesh_check = wx.CheckBox(self.tetra_group_box, label="Use Gradient-based Variable Mesh Size")
        self.use_variable_mesh_check.Bind(wx.EVT_CHECKBOX, self.on_toggle_variable_mesh)
        tetra_sizer.Add(self.use_variable_mesh_check, 0, wx.ALL, 5)

        # Cell Size (non-variable)
        self.cell_size_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.cell_size_sizer.Add(wx.StaticText(self.tetra_group_box, label="Cell Size:"), 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        self.cell_size_ctrl = wx.SpinCtrlDouble(self.tetra_group_box, min=0.000001, max=100.0, initial=0.1, inc=0.000001)
        self.cell_size_ctrl.SetDigits(6)
        self.cell_size_sizer.Add(self.cell_size_ctrl, 1, wx.EXPAND | wx.ALL, 5)
        tetra_sizer.Add(self.cell_size_sizer, 0, wx.EXPAND)

        # Variable Mesh Options
        self.variable_mesh_group = wx.StaticBox(self.tetra_group_box, label="Variable Mesh Size Options")
        self.variable_mesh_group.Hide()
        variable_mesh_sizer = wx.StaticBoxSizer(self.variable_mesh_group, wx.VERTICAL)

        min_cell_sizer = wx.BoxSizer(wx.HORIZONTAL)
        min_cell_sizer.Add(wx.StaticText(self.variable_mesh_group, label="Minimum Cell Size:"), 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        self.min_cell_size_ctrl = wx.SpinCtrlDouble(self.variable_mesh_group, min=0.000001, max=100.0, inc=0.000001)
        self.min_cell_size_ctrl.SetDigits(6)
        min_cell_sizer.Add(self.min_cell_size_ctrl, 1, wx.EXPAND | wx.ALL, 5)
        variable_mesh_sizer.Add(min_cell_sizer, 0, wx.EXPAND)

        max_cell_sizer = wx.BoxSizer(wx.HORIZONTAL)
        max_cell_sizer.Add(wx.StaticText(self.variable_mesh_group, label="Maximum Cell Size:"), 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        self.max_cell_size_ctrl = wx.SpinCtrlDouble(self.variable_mesh_group, min=0.000001, max=100.0, inc=0.000001)
        self.max_cell_size_ctrl.SetDigits(6)
        max_cell_sizer.Add(self.max_cell_size_ctrl, 1, wx.EXPAND | wx.ALL, 5)
        variable_mesh_sizer.Add(max_cell_sizer, 0, wx.EXPAND)

        variable_mesh_sizer.Add(wx.StaticText(self.variable_mesh_group, label="Cell Size Mapping Expression:"), 0, wx.ALL, 5)
        self.variable_cell_size_expr_ctrl = wx.TextCtrl(self.variable_mesh_group, style=wx.TE_MULTILINE)
        self.variable_cell_size_expr_ctrl.SetValue("min_cell + h * (max_cell - min_cell)")
        variable_mesh_sizer.Add(self.variable_cell_size_expr_ctrl, 1, wx.EXPAND | wx.ALL, 5)
        tetra_sizer.Add(variable_mesh_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # Facet Angle
        facet_angle_sizer = wx.BoxSizer(wx.HORIZONTAL)
        facet_angle_sizer.Add(wx.StaticText(self.tetra_group_box, label="Facet Angle (deg):"), 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        self.facet_angle_slider = wx.Slider(self.tetra_group_box, value=30, minValue=0, maxValue=90)
        self.facet_angle_label = wx.StaticText(self.tetra_group_box, label="30")
        self.facet_angle_slider.Bind(wx.EVT_SLIDER, lambda evt: self.facet_angle_label.SetLabel(str(self.facet_angle_slider.GetValue())))
        facet_angle_sizer.Add(self.facet_angle_slider, 1, wx.EXPAND | wx.ALL, 5)
        facet_angle_sizer.Add(self.facet_angle_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        tetra_sizer.Add(facet_angle_sizer, 0, wx.EXPAND)

        # Facet Size
        facet_size_sizer = wx.BoxSizer(wx.HORIZONTAL)
        facet_size_sizer.Add(wx.StaticText(self.tetra_group_box, label="Facet Size (mm):"), 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        self.facet_size_ctrl = wx.SpinCtrlDouble(self.tetra_group_box, min=0.000001, max=100.0, inc=0.000001)
        self.facet_size_ctrl.SetDigits(6)
        facet_size_sizer.Add(self.facet_size_ctrl, 1, wx.EXPAND | wx.ALL, 5)
        tetra_sizer.Add(facet_size_sizer, 0, wx.EXPAND)

        # Facet Distance
        facet_dist_sizer = wx.BoxSizer(wx.HORIZONTAL)
        facet_dist_sizer.Add(wx.StaticText(self.tetra_group_box, label="Facet Distance (mm):"), 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        self.facet_dist_ctrl = wx.SpinCtrlDouble(self.tetra_group_box, min=0.000001, max=100.0, inc=0.000001)
        self.facet_dist_ctrl.SetDigits(6)
        facet_dist_sizer.Add(self.facet_dist_ctrl, 1, wx.EXPAND | wx.ALL, 5)
        tetra_sizer.Add(facet_dist_sizer, 0, wx.EXPAND)

        # Cell Radius/Edge Ratio
        cell_ratio_sizer = wx.BoxSizer(wx.HORIZONTAL)
        cell_ratio_sizer.Add(wx.StaticText(self.tetra_group_box, label="Cell Radius/Edge Ratio:"), 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        self.cell_ratio_ctrl = wx.SpinCtrl(self.tetra_group_box, min=1, max=10, initial=2)
        cell_ratio_sizer.Add(self.cell_ratio_ctrl, 1, wx.EXPAND | wx.ALL, 5)
        tetra_sizer.Add(cell_ratio_sizer, 0, wx.EXPAND)

        sizer.Add(tetra_sizer, 0, wx.EXPAND | wx.ALL, 5)

        self.on_auto_compute(None)
        self.SetSizerAndFit(sizer)

    def on_browse(self, event):
        with wx.FileDialog(self, "Save INP File", wildcard="INP files (*.inp)|*.inp",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            pathname = fileDialog.GetPath()
            if not pathname.lower().endswith(".inp"):
                pathname += ".inp"
            self.path_ctrl.SetValue(pathname)

    def on_element_type_change(self, event):
        is_tetra = self.element_type_combo.GetSelection() == 0
        self.tetra_group_box.Show(is_tetra)
        self.brick_group_box.Show(not is_tetra)
        self.GetParent().Layout()

    def on_brick_dim_change(self, event):
        try:
            x = int(self.x_dim_ctrl.GetValue())
            y = int(self.y_dim_ctrl.GetValue())
            z = int(self.z_dim_ctrl.GetValue())
            self.num_elements_label.SetLabel(f"Number of Elements: {x*y*z:,.0f}")
        except ValueError:
            self.num_elements_label.SetLabel("Number of Elements: Invalid Input")

    def on_toggle_variable_mesh(self, event):
        use_variable = self.use_variable_mesh_check.IsChecked()
        self.variable_mesh_group.Show(use_variable)
        self.cell_size_sizer.Show(not use_variable)
        self.GetParent().Layout()

    def on_auto_compute(self, event):
        if event: # Only show message box on button click
            reply = wx.MessageBox("This will overwrite the current values. Are you sure you want to continue?", "Overwrite Values?", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
            if reply == wx.NO:
                return

        voxel_size = self.voxel_size_ctrl.GetValue()
        self.voxel_size_ctrl.SetIncrement(voxel_size / 10.0)

        self.facet_size_ctrl.SetValue(voxel_size)
        self.facet_size_ctrl.SetIncrement(voxel_size / 10.0)

        self.facet_dist_ctrl.SetValue(voxel_size / 10.0)
        self.facet_dist_ctrl.SetIncrement(voxel_size / 100.0)

        self.cell_size_ctrl.SetValue(voxel_size)
        self.cell_size_ctrl.SetIncrement(voxel_size / 10.0)

        self.min_cell_size_ctrl.SetValue(voxel_size)
        self.min_cell_size_ctrl.SetIncrement(voxel_size / 20.0)

        self.max_cell_size_ctrl.SetValue(voxel_size * 10)
        self.max_cell_size_ctrl.SetIncrement(voxel_size / 20.0)

    def get_export_options(self):
        options = {"file_path": self.path_ctrl.GetValue()}
        if self.element_type_combo.GetSelection() == 0: # Tetra
            options.update({
                "element_type": "tetra",
                "voxel_size": self.voxel_size_ctrl.GetValue(),
                "facet_angle": self.facet_angle_slider.GetValue(),
                "facet_size": self.facet_size_ctrl.GetValue(),
                "facet_distance": self.facet_dist_ctrl.GetValue(),
                "cell_radius_edge_ratio": self.cell_ratio_ctrl.GetValue(),
                "use_variable_mesh_size": self.use_variable_mesh_check.IsChecked(),
                "cell_size": self.cell_size_ctrl.GetValue(),
                "min_cell_size": self.min_cell_size_ctrl.GetValue(),
                "max_cell_size": self.max_cell_size_ctrl.GetValue(),
                "variable_cell_size_expression": self.variable_cell_size_expr_ctrl.GetValue(),
            })
        else: # Brick
            options.update({
                "element_type": "brick",
                "x_dim": int(self.x_dim_ctrl.GetValue()),
                "y_dim": int(self.y_dim_ctrl.GetValue()),
                "z_dim": int(self.z_dim_ctrl.GetValue()),
                "use_volumetric_dither": self.use_volumetric_dither_check.IsChecked(),
            })
        return options
