import wx
import wx.lib.newevent
import threading
import time
import os
import subprocess
import sys
import pyvcad as pv
import pyvcad_compilers as pvc
from wx.lib.newevent import NewEvent

# Custom event for progress updates
UpdateProgressEvent, EVT_UPDATE_PROGRESS = NewEvent()

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
            voxel_size_vec3 = pv.Vec3(self.voxel_size[0], self.voxel_size[1], self.voxel_size[2])
            compiler = pvc.GCVFExporter(
                root=self.root,
                voxel_size=voxel_size_vec3,
                material_defs=self.material_defs,
                filename=self.file_path,
                liquid_keep_out=self.liquid_keepout,
                liquid_keep_out_distance=self.liquid_keepout_distance
            )

            def progress_callback(phase, progress):
                if not self._running:
                    raise Exception("Export cancelled")

                progress_value = 0
                if phase == 0:
                    progress_value = int(progress * 100.0)
                else:
                    progress_value = 100

                evt = UpdateProgressEvent(progress=progress_value, error=None, finished=False)
                wx.PostEvent(self.parent, evt)

            compiler.setProgressCallback(progress_callback)
            compiler.compile()

            if self._running:
                evt = UpdateProgressEvent(progress=100, error=None, finished=True)
                wx.PostEvent(self.parent, evt)
        except Exception as e:
            if self._running:
                evt = UpdateProgressEvent(error=str(e), finished=True)
                wx.PostEvent(self.parent, evt)

    def stop(self):
        self._running = False

class GCVFInkjetProgressPanel(wx.Panel):
    def __init__(self, parent, export_options):
        super().__init__(parent)
        self.export_options = export_options
        self.worker = None
        self.start_time = None

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.StaticText(self, label="Exporting GCVF..."), 0, wx.ALL, 5)

        self.progress_bar = wx.Gauge(self, range=100, style=wx.GA_HORIZONTAL)
        sizer.Add(self.progress_bar, 0, wx.ALL | wx.EXPAND, 5)

        self.elapsed_time_label = wx.StaticText(self, label="Elapsed time: 00:00:00")
        sizer.Add(self.elapsed_time_label, 0, wx.ALL, 5)

        self.time_estimate_label = wx.StaticText(self, label="Estimated time remaining: N/A")
        sizer.Add(self.time_estimate_label, 0, wx.ALL, 5)

        self.SetSizer(sizer)

        self.Bind(EVT_UPDATE_PROGRESS, self.on_update_progress)
        self.update_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_update_timer, self.update_timer)

    def start_export(self):
        self.start_time = time.time()
        self.update_timer.Start(1000)

        self.worker = GCVFCompilerWorker(
            self,
            self.export_options['root'],
            self.export_options['voxel_size'],
            self.export_options['materials'],
            self.export_options['file_path'],
            self.export_options['liquid_keepout'],
            self.export_options['liquid_keepout_distance']
        )
        self.worker.start()

    def on_update_progress(self, event):
        if event.error:
            self.update_timer.Stop()
            wx.MessageBox(f"An error occurred during export: {event.error}", "Error", wx.OK | wx.ICON_ERROR)
            self.GetParent().GetParent().FindWindowByLabel("Back").Enable(True) # Allow user to go back
        elif event.finished:
            self.update_timer.Stop()
            self.progress_bar.SetValue(100)
            elapsed_seconds = time.time() - self.start_time
            elapsed_time_str = time.strftime('%H:%M:%S', time.gmtime(elapsed_seconds))
            self.elapsed_time_label.SetLabel(f"Elapsed time: {elapsed_time_str}")

            # Notify MainFrame that export is complete
            main_frame = self.GetTopLevelParent()
            main_frame.on_export_complete(self.export_options['file_path'], elapsed_time_str)
        else:
            self.progress_bar.SetValue(event.progress)

    def on_update_timer(self, event):
        elapsed_seconds = time.time() - self.start_time
        self.elapsed_time_label.SetLabel(f"Elapsed time: {time.strftime('%H:%M:%S', time.gmtime(elapsed_seconds))}")

        progress = self.progress_bar.GetValue()
        if progress > 0:
            remaining_seconds = (elapsed_seconds * (100 - progress)) / progress
            self.time_estimate_label.SetLabel(f"Estimated time remaining: {time.strftime('%H:%M:%S', time.gmtime(remaining_seconds))}")

    def __del__(self):
        if self.worker and self.worker.is_alive():
            self.worker.stop()
            self.worker.join()
        self.update_timer.Stop()
