import wx
import wx.lib.newevent
import threading
import time
import os
import subprocess
import sys
import numpy as np
from wx.lib.newevent import NewEvent

# Custom event for progress updates
UpdateProgressEvent, EVT_UPDATE_PROGRESS = NewEvent()

class VatPhotoCompilerWorker(threading.Thread):
    def __init__(self, parent, root, voxel_size, printer_volume, low_material, high_material, output_directory, file_prefix):
        super().__init__()
        self.parent = parent
        self.root = root
        self.voxel_size = voxel_size
        self.printer_volume = printer_volume
        self.low_material = low_material
        self.high_material = high_material
        self.output_directory = output_directory
        self.file_prefix = file_prefix
        self._running = True

    def run(self):
        try:
            # This is where you would call the actual compiler
            # For now, we simulate the progress
            for i in range(101):
                if not self._running:
                    break
                time.sleep(0.05)
                evt = UpdateProgressEvent(progress=i, error=None, finished=(i == 100))
                wx.PostEvent(self.parent, evt)
        except Exception as e:
            evt = UpdateProgressEvent(error=str(e), finished=True)
            wx.PostEvent(self.parent, evt)

    def stop(self):
        self._running = False

class VatPhotoProgressPanel(wx.Panel):
    def __init__(self, parent, export_options):
        super().__init__(parent)
        self.export_options = export_options
        self.worker = None
        self.start_time = None

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.StaticText(self, label="Exporting Vat Photo Stack..."), 0, wx.ALL, 5)

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

        self.worker = VatPhotoCompilerWorker(
            self,
            self.export_options['root'],
            self.export_options['voxel_size'],
            self.export_options['printer_volume'],
            self.export_options['low_material'],
            self.export_options['high_material'],
            self.export_options['output_directory'],
            self.export_options['file_prefix']
        )
        self.worker.start()

    def on_update_progress(self, event):
        if event.error:
            self.update_timer.Stop()
            wx.MessageBox(f"An error occurred during export: {event.error}", "Error", wx.OK | wx.ICON_ERROR)
            self.GetParent().GetParent().FindWindowByLabel("Back").Enable(True)
        elif event.finished:
            self.update_timer.Stop()
            self.progress_bar.SetValue(100)
            elapsed_seconds = time.time() - self.start_time
            elapsed_time_str = time.strftime('%H:%M:%S', time.gmtime(elapsed_seconds))
            self.elapsed_time_label.SetLabel(f"Elapsed time: {elapsed_time_str}")

            main_frame = self.GetTopLevelParent()
            main_frame.on_export_complete(self.export_options['output_directory'], elapsed_time_str)
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

