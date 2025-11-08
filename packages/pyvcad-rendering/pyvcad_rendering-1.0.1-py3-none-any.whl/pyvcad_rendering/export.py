import wx

from .export_frame import ExportFrame

def export(vcad_object, materials):
    app = wx.App(False)
    app.frame = ExportFrame(vcad_object, materials)
    app.MainLoop()

def Export(vcad_object, materials):
    export(vcad_object, materials)

__all__ = ["export", "Export"]

