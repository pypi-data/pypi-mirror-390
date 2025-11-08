import wx
import wx.lib.newevent
import pyvcad as pv
import pyvcad_compilers as pvc
import threading
import time
import os
import numpy as np
from wx.lib.newevent import NewCommandEvent

# Custom event for progress updates from the worker thread
UpdateProgressEvent, EVT_UPDATE_PROGRESS = NewCommandEvent()

class GCVFCompilerWorker(threading.Thread):
    def __init__(self, parent, root, voxel_size, material_defs, file_path, liquid_keepout, liquid_keepout_distance):
        super().__init__()
        self.parent = parent
        self.root = root
        self.voxel_size = voxel_size
        self.material_defs = material_defs
        self.file_path = file_path
        self.liquid_keepout = liquid_keepout
        self.liquid_keepout_distance = liquid_keepout_distance
        self._running = True

    def run(self):
        try:
            # This is where you would call the actual compiler
            # For now, we simulate the progress
            for i in range(101):
                if not self._running:
                    break
                time.sleep(0.05)
                progress_data = {
                    'phase': 0,
                    'progress': i / 100.0,
                    'error': None,
                    'finished': i == 100
                }
                wx.PostEvent(self.parent, UpdateProgressEvent(**progress_data))
        except Exception as e:
            progress_data = {'error': str(e), 'finished': True}
            wx.PostEvent(self.parent, UpdateProgressEvent(**progress_data))

    def stop(self):
        self._running = False

class GCVFInkjetPanel(wx.Panel):
    def __init__(self, parent, root, materials):
        super().__init__(parent)
        self.root = root
        self.materials = materials

        min_bounds, max_bounds = self.root.bounding_box()
        self.min_bounds = np.array([min_bounds.x, min_bounds.y, min_bounds.z])
        self.max_bounds = np.array([max_bounds.x, max_bounds.y, max_bounds.z])

        sizer = wx.BoxSizer(wx.VERTICAL)

        # File Path
        path_label = wx.StaticText(self, label="File Path:")
        sizer.Add(path_label, 0, wx.ALL, 5)

        path_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.path_ctrl = wx.TextCtrl(self)
        path_sizer.Add(self.path_ctrl, 1, wx.EXPAND | wx.ALL, 5)
        browse_btn = wx.Button(self, label="Browse")
        browse_btn.Bind(wx.EVT_BUTTON, self.on_browse)
        path_sizer.Add(browse_btn, 0, wx.ALL, 5)
        sizer.Add(path_sizer, 0, wx.EXPAND)

        # Liquid Keepout
        self.liquid_keepout_check = wx.CheckBox(self, label="Enable Liquid Keepout")
        self.liquid_keepout_check.Bind(wx.EVT_CHECKBOX, self.on_toggle_keepout)
        sizer.Add(self.liquid_keepout_check, 0, wx.ALL, 5)

        self.keepout_distance_ctrl = wx.SpinCtrlDouble(self, min=0.0, max=100.0, inc=0.1)
        self.keepout_distance_ctrl.SetValue(0.0)
        self.keepout_distance_ctrl.Enable(False)
        sizer.Add(self.keepout_distance_ctrl, 0, wx.ALL | wx.EXPAND, 5)

        # Voxel Size and Sampling Info
        self.voxel_size = np.array([0.0423, 0.0846, 0.027]) # J750 voxel size
        self.sampling_info_label = wx.StaticText(self, label="")
        self.update_sampling_info()
        sizer.Add(self.sampling_info_label, 0, wx.ALL, 5)

        self.SetSizer(sizer)

    def on_browse(self, event):
        with wx.FileDialog(self, "Save GCVF File", wildcard="GCVF files (*.gcvf)|*.gcvf",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            pathname = fileDialog.GetPath()
            if not pathname.lower().endswith(".gcvf"):
                pathname += ".gcvf"
            self.path_ctrl.SetValue(pathname)

    def on_toggle_keepout(self, event):
        self.keepout_distance_ctrl.Enable(event.IsChecked())

    def update_sampling_info(self):
        size = self.max_bounds - self.min_bounds
        total_voxels = (size[0] / self.voxel_size[0]) * (size[1] / self.voxel_size[1]) * (size[2] / self.voxel_size[2])

        sampling_info = (f"Sample Space Size: {size[0]:.2f} x {size[1]:.2f} x {size[2]:.2f} mm\n"
                         f"Total Voxels: {total_voxels:,.0f}")
        self.sampling_info_label.SetLabel(sampling_info)

    def get_export_options(self):
        return {
            "file_path": self.path_ctrl.GetValue(),
            "liquid_keepout": self.liquid_keepout_check.IsChecked(),
            "liquid_keepout_distance": self.keepout_distance_ctrl.GetValue(),
            "voxel_size": self.voxel_size,
            "root": self.root,
            "materials": self.materials
        }
