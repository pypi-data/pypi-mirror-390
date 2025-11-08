import wx
import wx.html
import datetime
import webbrowser

from .vtk_pipeline_wx import (
    VTKRenderPipeline,
    EVT_BUILD_STARTED, EVT_BUILD_FINISHED, EVT_BUILD_FAILED,
    EVT_ISO_SAMPLE, EVT_ISO_CONTOUR, EVT_ISO_COLOR, EVT_VOL_SAMPLE
)
from vtkmodules.wx import wxVTKRenderWindowInteractor # VTK imports

def _is_dark_colour(col: wx.Colour) -> bool:
    """Fallback luminance check (sRGB) for older wx versions."""
    r, g, b = col.Red(), col.Green(), col.Blue()
    # relative luminance (approx.) -> threshold ~ 0.5
    lum = (0.2126 * (r/255.0)) + (0.7152 * (g/255.0)) + (0.0722 * (b/255.0))
    return lum < 0.5

class RenderFrame(wx.Frame):
    def __init__(self, vcad_object, materials, parent=None, title="OpenVCAD Renderer"):
        super().__init__(parent, title=title, size=(1000, 700))
        self.progress_dialog = None
        self.vcad_object = vcad_object
        self.materials = materials

        # Create a panel in this frame and embed the VTK interactor
        panel = wx.Panel(self)
        panel_sizer = wx.BoxSizer(wx.VERTICAL)
        self.vtk_widget = wxVTKRenderWindowInteractor.wxVTKRenderWindowInteractor(panel, -1)
        panel_sizer.Add(self.vtk_widget, 1, wx.EXPAND)
        panel.SetSizer(panel_sizer)
        panel.Layout()

        # Frame sizer to hold the panel (so VTK fills the window)
        frame_sizer = wx.BoxSizer(wx.VERTICAL)
        frame_sizer.Add(panel, 1, wx.EXPAND)
        self.SetSizer(frame_sizer)
        self.Layout()

        self.vtk_widget.Enable(1)
        
        self.render_pipeline = VTKRenderPipeline(
            event_target=self,
            use_default_interaction=True,
            render_window=self.vtk_widget.GetRenderWindow(),
        )

        self.Bind(EVT_BUILD_STARTED, lambda e: self.on_build_started(e.generation))
        self.Bind(EVT_BUILD_FINISHED, lambda e: self.on_build_finished(e.generation))
        self.Bind(EVT_BUILD_FAILED, lambda e: self.on_build_failed(getattr(e, "message", "Unknown error")))

        self.Bind(EVT_ISO_SAMPLE, lambda e: self.on_iso_sample_progress(int(e.progress)))
        self.Bind(EVT_ISO_CONTOUR, lambda e: self.on_iso_contour_progress(int(e.progress)))
        self.Bind(EVT_ISO_COLOR, lambda e: self.on_iso_color_progress(int(e.progress)))
        self.Bind(EVT_VOL_SAMPLE, lambda e: self.on_vol_sample_progress(int(e.progress)))

        # ----- Menu Bar -----
        menubar = wx.MenuBar()

        # ===== File =====
        file_menu = wx.Menu()
        self.item_screenshot = file_menu.Append(wx.ID_ANY, "Screenshot")
        menubar.Append(file_menu, "&File")

        # ===== View =====
        view_menu = wx.Menu()

        # Quality sub-menu (radio)
        self.quality_menu = wx.Menu()
        self.item_quality_low = self.quality_menu.AppendRadioItem(wx.ID_ANY, "Low")
        self.item_quality_medium = self.quality_menu.AppendRadioItem(wx.ID_ANY, "Medium")
        self.item_quality_high = self.quality_menu.AppendRadioItem(wx.ID_ANY, "High")
        self.item_quality_ultra = self.quality_menu.AppendRadioItem(wx.ID_ANY, "Ultra")
        self.item_quality_low.Check(True)  # default

        view_menu.AppendSubMenu(self.quality_menu, "Quality")
        view_menu.AppendSeparator()

        self.item_show_origin = view_menu.AppendCheckItem(wx.ID_ANY, "Show Origin")
        self.item_ortho_proj = view_menu.AppendCheckItem(wx.ID_ANY, "Orthographic Projection")
        view_menu.AppendSeparator()

        self.item_reset_camera = view_menu.Append(wx.ID_ANY, "Reset Camera")
        view_menu.AppendSeparator()

        self.item_top_view = view_menu.Append(wx.ID_ANY, "Top View")
        self.item_bottom_view = view_menu.Append(wx.ID_ANY, "Bottom View")
        self.item_side_view = view_menu.Append(wx.ID_ANY, "Side View")
        self.item_corner_view = view_menu.Append(wx.ID_ANY, "Corner View")

        menubar.Append(view_menu, "&View")

        # ===== Object =====
        object_menu = wx.Menu()

        # Mode sub-menu (radio)
        self.render_mode_menu = wx.Menu()
        self.item_iso_surface = self.render_mode_menu.AppendRadioItem(wx.ID_ANY, "Iso-surface")
        self.item_volumetric = self.render_mode_menu.AppendRadioItem(wx.ID_ANY, "Volumetric")
        self.item_iso_surface.Check(True)  # default
        object_menu.AppendSubMenu(self.render_mode_menu, "Mode")

        self.item_show_bbox = object_menu.AppendCheckItem(wx.ID_ANY, "Show bounding box")

        # Volumetric Options sub-menu (disabled by default)
        self.volume_menu = wx.Menu()
        self.item_volumetric_blending = self.volume_menu.AppendCheckItem(wx.ID_ANY, "Volumetric Blending")
        self.item_volumetric_shading = self.volume_menu.AppendCheckItem(wx.ID_ANY, "Volumetric Shading")
        self.item_volumetric_blending.Check(True)  # default enabled

        # Keep handle to the submenu item so we can enable/disable
        self.volume_menu_item = object_menu.AppendSubMenu(self.volume_menu, "Volumetric Options")
        self.volume_menu_item.Enable(False)

        menubar.Append(object_menu, "&Object")

        # ===== Help =====
        help_menu = wx.Menu()
        self.item_about = help_menu.Append(wx.ID_ANY, "About")
        help_menu.AppendSeparator()
        self.item_wiki = help_menu.Append(wx.ID_ANY, "Wiki")
        self.item_docs = help_menu.Append(wx.ID_ANY, "Library Documentation")
        self.item_getting_started = help_menu.Append(wx.ID_ANY, "Getting Started")
        help_menu.AppendSeparator()
        self.item_report_bug = help_menu.Append(wx.ID_ANY, "Report a Bug")
        menubar.Append(help_menu, "&Help")

        self.SetMenuBar(menubar)

        # ----- Bind menu events -----
        # File
        self.Bind(wx.EVT_MENU, self.on_screenshot, self.item_screenshot)

        # View
        self.Bind(wx.EVT_MENU, self.on_toggle_show_origin, self.item_show_origin)
        self.Bind(wx.EVT_MENU, self.on_toggle_ortho_projection, self.item_ortho_proj)
        self.Bind(wx.EVT_MENU, self.on_reset_camera, self.item_reset_camera)
        self.Bind(wx.EVT_MENU, self.on_set_top_view, self.item_top_view)
        self.Bind(wx.EVT_MENU, self.on_set_bottom_view, self.item_bottom_view)
        self.Bind(wx.EVT_MENU, self.on_set_side_view, self.item_side_view)
        self.Bind(wx.EVT_MENU, self.on_set_corner_view, self.item_corner_view)

        # Quality radio group → one handler, read which is checked
        self.Bind(wx.EVT_MENU, self._on_quality_any, self.item_quality_low)
        self.Bind(wx.EVT_MENU, self._on_quality_any, self.item_quality_medium)
        self.Bind(wx.EVT_MENU, self._on_quality_any, self.item_quality_high)
        self.Bind(wx.EVT_MENU, self._on_quality_any, self.item_quality_ultra)

        # Object → Mode radios
        self.Bind(wx.EVT_MENU, self._on_mode_any, self.item_iso_surface)
        self.Bind(wx.EVT_MENU, self._on_mode_any, self.item_volumetric)

        # Object toggles
        self.Bind(wx.EVT_MENU, self.on_toggle_show_bbox, self.item_show_bbox)
        self.Bind(wx.EVT_MENU, self.on_toggle_volumetric_blending, self.item_volumetric_blending)
        self.Bind(wx.EVT_MENU, self.on_toggle_volumetric_shading, self.item_volumetric_shading)

        # Help
        self.Bind(wx.EVT_MENU, self.on_about, self.item_about)
        self.Bind(wx.EVT_MENU, self.on_wiki, self.item_wiki)
        self.Bind(wx.EVT_MENU, self.on_docs, self.item_docs)
        self.Bind(wx.EVT_MENU, self.on_getting_started, self.item_getting_started)
        self.Bind(wx.EVT_MENU, self.on_report_bug, self.item_report_bug)

        self.Centre()
        self.Show()

        # Update if the OS theme changes while the app is running
        self.Bind(wx.EVT_SYS_COLOUR_CHANGED, self._on_sys_colour_changed)

        # Initial render
        self.render_pipeline.update_vcad_object(self.vcad_object, self.materials)

        # Apply background based on current system appearance
        self._apply_bg_from_system()


    def on_build_started(self, _=0):
        is_volumetric = self.render_pipeline.get_render_mode() == "volumetric"
        maximum = 100 if is_volumetric else 300
        
        # Max=300 for iso-surface (3 phases), 100 for volumetric (1 phase)
        self.progress_dialog = wx.ProgressDialog(
            "Rendering…",
            "Initializing…",
            maximum=maximum,
            parent=self,
            style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE | wx.PD_CAN_ABORT
        )
        self.progress_dialog.Update(0, "Initializing…")


    def on_build_finished(self, _=0):
        if self.progress_dialog:
            # Update to max value regardless of mode before destroying
            max_val = self.progress_dialog.GetRange()
            self.progress_dialog.Update(max_val, "Done")
            self.progress_dialog.Destroy()
            self.progress_dialog = None


    def on_build_failed(self, msg: str):
        if self.progress_dialog:
            self.progress_dialog.Destroy()
            self.progress_dialog = None
        wx.MessageBox(msg, "Build failed", wx.OK | wx.ICON_WARNING, parent=self)


    def on_iso_sample_progress(self, p: float):
        if self.progress_dialog:
            self.progress_dialog.Update(int(p), "Phase 1/3: Sampling…")


    def on_iso_contour_progress(self, p: float):
        if self.progress_dialog:
            self.progress_dialog.Update(100 + int(p), "Phase 2/3: Contouring…")


    def on_iso_color_progress(self, p: float):
        if self.progress_dialog:
            self.progress_dialog.Update(200 + int(p), "Phase 3/3: Coloring…")


    def on_vol_sample_progress(self, p: float):
        if self.progress_dialog:
            # Volumetric mode is a single phase from 0-100
            self.progress_dialog.Update(int(p), "Volume Sampling…")


    def on_screenshot(self, _evt=None):
        with wx.FileDialog(
            self,
            message="Save Screenshot",
            defaultFile="screenshot.png",
            wildcard="PNG Image (*.png)|*.png",
            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT
        ) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                path = dlg.GetPath()
                self.render_pipeline.take_screenshot(path)


    def on_about(self, _evt=None):
        year = datetime.date.today().year
        try:
            import pyvcad as pv
            vcad_version = pv.version()
        except Exception:
            vcad_version = "unknown"

        dlg = wx.Dialog(self, title="About OpenVCAD Renderer")
        
        # Main sizer for the dialog content
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Title
        title_font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        title_font.SetPointSize(title_font.GetPointSize() + 4)
        title_font.SetWeight(wx.FONTWEIGHT_BOLD)
        title_text = wx.StaticText(dlg, label="OpenVCAD Renderer")
        title_text.SetFont(title_font)
        main_sizer.Add(title_text, 0, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 15)

        # Content sizer
        content_sizer = wx.BoxSizer(wx.VERTICAL)
        content_sizer.Add(wx.StaticText(dlg, label=f"Built by the Matter Assembly Computation Lab"), 0, wx.BOTTOM, 5)
        content_sizer.Add(wx.StaticText(dlg, label=f"Using pyvcad version: {vcad_version}"), 0, wx.BOTTOM, 5)
        content_sizer.Add(wx.StaticText(dlg, label=f"© Charles Wade and Robert MacCurdy {year}"), 0, wx.BOTTOM, 10)
        
        content_sizer.Add(wx.StaticLine(dlg), 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 10)

        # Disclaimer
        disclaimer_font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        disclaimer_font.SetWeight(wx.FONTWEIGHT_BOLD)
        disclaimer_title = wx.StaticText(dlg, label="DISCLAIMER:")
        disclaimer_title.SetFont(disclaimer_font)
        content_sizer.Add(disclaimer_title, 0, wx.BOTTOM, 5)

        disclaimer_body = wx.StaticText(dlg, label=(
            "OpenVCAD Open Source is a research tool and is not permitted for commercial use.\n"
            "For commercial use, please contact Charles Wade at:\n"
            "charles.wade@colorado.edu"
        ))
        content_sizer.Add(disclaimer_body, 0, wx.BOTTOM, 15)

        main_sizer.Add(content_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 20)

        # OK Button
        main_sizer.Add(wx.Button(dlg, wx.ID_OK, "OK"), 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)

        dlg.SetSizerAndFit(main_sizer)
        dlg.CentreOnParent()
        dlg.ShowModal()
        dlg.Destroy()


    def on_wiki(self, _evt=None):
        webbrowser.open("https://github.com/MacCurdyLab/OpenVCAD-Public/wiki")


    def on_docs(self, _evt=None):
        webbrowser.open("https://matterassembly.org/pyvcad")


    def on_getting_started(self, _evt=None):
        webbrowser.open("https://github.com/MacCurdyLab/OpenVCAD-Public/wiki/Getting-Started-with-OpenVCAD")


    def on_report_bug(self, _evt=None):
        webbrowser.open("https://github.com/MacCurdyLab/OpenVCAD-Public/issues/new?template=bug_report.md")


    def on_reset_camera(self, _evt=None):
        self.render_pipeline.reset_camera()


    def on_toggle_ortho_projection(self, _evt=None):
        checked = self.item_ortho_proj.IsChecked()
        self.render_pipeline.enable_orthogonal_projection(checked)


    def _on_quality_any(self, evt):
        quality_map = { # Map checked item -> quality string
            self.item_quality_low.GetId(): "low",
            self.item_quality_medium.GetId(): "medium",
            self.item_quality_high.GetId(): "high",
            self.item_quality_ultra.GetId(): "ultra",
        }
        quality = quality_map.get(evt.GetId(), "low")
        self.on_quality_changed(quality)


    def on_quality_changed(self, quality: str):
        self.render_pipeline.set_quality_profile(quality)


    def on_toggle_show_bbox(self, _evt=None):
        checked = self.item_show_bbox.IsChecked()
        self.render_pipeline.show_bounding_box(checked)


    def on_toggle_show_origin(self, _evt=None):
        checked = self.item_show_origin.IsChecked()
        self.render_pipeline.show_origin(checked)


    def on_set_top_view(self, _evt=None):
       self.render_pipeline.set_top_view()


    def on_set_bottom_view(self, _evt=None):
        self.render_pipeline.set_bottom_view()


    def on_set_side_view(self, _evt=None):
        self.render_pipeline.set_side_view()


    def on_set_corner_view(self, _evt=None):
        self.render_pipeline.set_corner_view()


    def _on_mode_any(self, evt):
        if evt.GetId() == self.item_volumetric.GetId():
            self.on_render_mode_changed("volumetric")
        else:
            self.on_render_mode_changed("iso_surface")


    def on_render_mode_changed(self, mode: str):
        self.render_pipeline.set_render_mode(mode)
        # Enable/disable volumetric submenu like Qt version
        is_vol = (mode == "volumetric")
        self.volume_menu_item.Enable(is_vol)
        if not is_vol:
            # uncheck shading when leaving volumetric
            self.item_volumetric_shading.Check(False)


    def on_toggle_volumetric_blending(self, _evt=None):
        checked = self.item_volumetric_blending.IsChecked()
        self.render_pipeline.enable_volume_blending(checked)


    def on_toggle_volumetric_shading(self, _evt=None):
        checked = self.item_volumetric_shading.IsChecked()
        self.render_pipeline.enable_volume_shading(checked)

    def _apply_bg_from_system(self):
        """Set the VTK background based on system appearance (dark vs light)."""
        try:
            appearance = wx.SystemSettings.GetAppearance()  # wx.SystemAppearance
            is_dark = appearance.IsDark()
        except AttributeError:
            # Fallback for older wx: infer from window color luminance
            win_col = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW)
            is_dark = _is_dark_colour(win_col)

        if is_dark:
            # Same dark gray you used before
            self.render_pipeline.set_background_color(0.177, 0.177, 0.177)
        else:
            self.render_pipeline.set_background_color(1.0, 1.0, 1.0)


    def _on_sys_colour_changed(self, _evt):
        self._apply_bg_from_system()
