import sys
import wx

from .render_frame import RenderFrame
    
def render(vcad_object, materials):
    app = wx.App(False)
    app.frame = RenderFrame(vcad_object, materials)
    app.MainLoop()

def Render(vcad_object, materials):
    render(vcad_object, materials)

__all__ = ["render", "Render"]
