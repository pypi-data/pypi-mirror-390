# vtk_pipeline_wx.py
import threading
import numpy as np
import wx
import wx.lib.newevent as ne

import vtkmodules.util.numpy_support as vtk_np
import vtkmodules.vtkInteractionStyle  # Ensure interactor styles are registered

from vtkmodules.vtkCommonCore import (
    VTK_FLOAT,
    VTK_UNSIGNED_CHAR,
    vtkCommand,
    vtkUnsignedCharArray,
)
from vtkmodules.vtkCommonDataModel import vtkImageData, vtkPiecewiseFunction
from vtkmodules.vtkFiltersCore import vtkContourFilter
from vtkmodules.vtkFiltersSources import vtkCubeSource
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkColorTransferFunction,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderer,
    vtkVolume,
    vtkVolumeProperty,
    vtkWindowToImageFilter,
)
from vtkmodules.vtkIOImage import vtkPNGWriter
from vtkmodules.vtkRenderingAnnotation import vtkAxesActor
from vtkmodules.vtkInteractionWidgets import vtkOrientationMarkerWidget
from vtkmodules.vtkRenderingVolumeOpenGL2 import vtkSmartVolumeMapper
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleTrackballCamera

import pyvcad as pv


# --------------------------
# wx Custom Events (binders)
# --------------------------
BuildStartedEvent, EVT_BUILD_STARTED = ne.NewEvent()
BuildFinishedEvent, EVT_BUILD_FINISHED = ne.NewEvent()
BuildFailedEvent, EVT_BUILD_FAILED = ne.NewEvent()

IsoSampleEvent, EVT_ISO_SAMPLE = ne.NewEvent()
IsoContourEvent, EVT_ISO_CONTOUR = ne.NewEvent()
IsoColorEvent, EVT_ISO_COLOR = ne.NewEvent()
VolSampleEvent, EVT_VOL_SAMPLE = ne.NewEvent()


class VTKRenderPipeline:

    def __init__(self, event_target: wx.Window, use_default_interaction=True, render_window=None):
        self.event_target = event_target

        # Rendering resources
        self.renderer = vtkRenderer()
        self.render_window = render_window or vtkRenderWindow()
        self.render_window.AddRenderer(self.renderer)

        # Interactor style (GUI thread only)
        if use_default_interaction:
            interactor = self.render_window.GetInteractor()
            if interactor is not None:
                style = vtkInteractorStyleTrackballCamera()
                interactor.SetInteractorStyle(style)

        self.corner_axis_widget = self._create_corner_axis_widget()

        # Render state
        self.render_mode = "iso_surface"
        self.quality_profile = "low"
        self.use_orthogonal_projection = False
        self.use_volume_shading = False
        self.use_volume_blending = True

        self._show_bounding_box = False
        self.bbox_actor = None
        self._show_origin = False
        self.origin_actor = None

        self.vcad_object = None
        self.materials = None
        self.voxel_size = None

        self.current_volume = None
        self.current_iso_surface = None

        # Async build state
        self._gen = 0
        self._pending_reset_camera = False
        self._worker_thread = None
        self._worker_lock = threading.Lock()

        # Default progress callbacks -> post wx events
        self.iso_surface_sample_progress_callback = lambda p: self._post(IsoSampleEvent, progress=float(p))
        self.iso_surface_contouring_progress_callback = lambda p: self._post(IsoContourEvent, progress=float(p))
        self.iso_surface_coloring_progress_callback = lambda p: self._post(IsoColorEvent, progress=float(p))
        self.volume_sample_progress_callback = lambda p: self._post(VolSampleEvent, progress=float(p))

    def update_vcad_object(self, vcad_object, materials, reset_camera=True):
        # Clear current view props immediately (GUI thread)
        self.renderer.RemoveAllViewProps()
        self.bbox_actor = None
        self.current_iso_surface = None
        self.current_volume = None

        self.vcad_object = vcad_object
        self.materials = materials
        self._pending_reset_camera = bool(reset_camera)

        if self.vcad_object is None or self.materials is None:
            self.render_window.Render()
            return

        # Bump generation to invalidate prior builds
        with self._worker_lock:
            self._gen += 1
            gen = self._gen

        # Snapshot config for the worker
        cfg = dict(
            render_mode=self.render_mode,
            quality_profile=self.quality_profile,
            use_volume_shading=self.use_volume_shading,
            show_bbox=self._show_bounding_box,
            show_origin=self._show_origin,
        )

        # Start worker thread
        self._start_worker(gen, self.vcad_object, self.materials, cfg)
        self._post(BuildStartedEvent, generation=gen)

    def set_progress_callbacks(
        self,
        iso_surface_sample=None,
        iso_surface_contouring=None,
        iso_surface_coloring=None,
        volume_sample=None,
    ):
        if iso_surface_sample is not None:
            self.iso_surface_sample_progress_callback = iso_surface_sample
        if iso_surface_contouring is not None:
            self.iso_surface_contouring_progress_callback = iso_surface_contouring
        if iso_surface_coloring is not None:
            self.iso_surface_coloring_progress_callback = iso_surface_coloring
        if volume_sample is not None:
            self.volume_sample_progress_callback = volume_sample

    def get_render_mode(self):
        return self.render_mode

    def show_bounding_box(self, show):
        show = bool(show)
        if show:
            self.bbox_actor = self._create_bbox_actor(self.vcad_object)
            self.renderer.AddActor(self.bbox_actor)
        else:
            self.renderer.RemoveActor(self.bbox_actor)
            self.bbox_actor = None
        self._show_bounding_box = show
        self.render_window.Render()

    def show_origin(self, show):
        show = bool(show)
        if show:
            self.origin_actor = self._create_origin_actor()
            self.renderer.AddActor(self.origin_actor)
        else:
            self.renderer.RemoveActor(self.origin_actor)
            self.origin_actor = None
        self._show_origin = show
        self.render_window.Render()

    def enable_orthogonal_projection(self, enable):
        self.renderer.GetActiveCamera().SetParallelProjection(enable)
        self.render_window.Render()

    def enable_volume_shading(self, enable):
        if self.render_mode == "volumetric":
            self.use_volume_shading = enable
            if self.current_volume is not None:
                if enable:
                    self.current_volume.GetProperty().ShadeOn()
                else:
                    self.current_volume.GetProperty().ShadeOff()
                self.render_window.Render()

    def reset_camera(self):
        min, max = self.vcad_object.bounding_box()
        center = pv.Vec3(
            (min.x + max.x) / 2, (min.y + max.y) / 2, (min.z + max.z) / 2
        )
        size = pv.Vec3(max.x - min.x, max.y - min.y, max.z - min.z)
        distance = ((size.x**2) + (size.y**2) + (size.z**2)) ** 0.5 * 1.5
        offset = distance / 3**0.5

        cam = self.renderer.GetActiveCamera()
        cam.SetPosition(center.x + offset, center.y + offset, center.z + offset)
        cam.SetFocalPoint(center.x, center.y, center.z)
        cam.SetViewUp(0, 0, 1)
        self.renderer.ResetCamera()
        self.renderer.ResetCameraClippingRange()
        self.render_window.Render()

    def set_top_view(self):
        cam = self.renderer.GetActiveCamera()
        cam.SetPosition(0, 0, 1)
        cam.SetViewUp(0, -1, 0)
        cam.SetFocalPoint(0, 0, 0)
        self.renderer.ResetCamera()
        self.render_window.Render()

    def set_side_view(self):
        cam = self.renderer.GetActiveCamera()
        cam.SetPosition(1, 0, 0)
        cam.SetViewUp(0, 0, 1)
        cam.SetFocalPoint(0, 0, 0)
        self.renderer.ResetCamera()
        self.render_window.Render()

    def set_bottom_view(self):
        cam = self.renderer.GetActiveCamera()
        cam.SetPosition(0, 0, -1)
        cam.SetViewUp(0, -1, 0)
        cam.SetFocalPoint(0, 0, 0)
        self.renderer.ResetCamera()
        self.render_window.Render()

    def set_corner_view(self):
        cam = self.renderer.GetActiveCamera()
        cam.SetPosition(1, 1, 1)
        cam.SetViewUp(0, 0, 1)
        cam.SetFocalPoint(0, 0, 0)
        self.renderer.ResetCamera()
        self.render_window.Render()

    def set_render_mode(self, mode: str):
        if mode not in ("volumetric", "iso_surface"):
            raise ValueError(f"Invalid render mode: {mode}")
        if mode == self.render_mode:
            return
        self.render_mode = mode
        if self.vcad_object is None or self.materials is None:
            return
        self.update_vcad_object(self.vcad_object, self.materials, reset_camera=False)

    def set_quality_profile(self, profile: str):
        if profile not in ("low", "medium", "high", "ultra"):
            raise ValueError(f"Invalid quality profile: {profile}")
        if profile == self.quality_profile:
            return
        self.quality_profile = profile
        if self.vcad_object is None or self.materials is None:
            return
        self.update_vcad_object(self.vcad_object, self.materials, reset_camera=False)

    def take_screenshot(self, path: str):
        origin_was_visible = self._show_origin
        if origin_was_visible and self.origin_actor:
            self.renderer.RemoveActor(self.origin_actor)
            self.render_window.Render()

        bbox_was_visible = self._show_bounding_box
        if bbox_was_visible and self.bbox_actor:
            self.renderer.RemoveActor(self.bbox_actor)
            self.render_window.Render()

        window_to_image_filter = vtkWindowToImageFilter()
        window_to_image_filter.SetInput(self.render_window)
        window_to_image_filter.SetScale(2)
        window_to_image_filter.SetInputBufferTypeToRGBA()
        window_to_image_filter.ReadFrontBufferOff()
        window_to_image_filter.Update()

        writer = vtkPNGWriter()
        writer.SetFileName(path)
        writer.SetInputConnection(window_to_image_filter.GetOutputPort())
        writer.SetFileDimensionality(2)
        writer.Write()

        if origin_was_visible and self.origin_actor:
            self.renderer.AddActor(self.origin_actor)
            self.render_window.Render()

        if bbox_was_visible and self.bbox_actor:
            self.renderer.AddActor(self.bbox_actor)
            self.render_window.Render()

    def set_background_color(self, r: float, g: float, b: float):
        self.renderer.SetBackground(r, g, b)

    def enable_volume_blending(self, enable: bool):
        self.use_volume_blending = enable
        if self.render_mode == "volumetric":
            self.update_vcad_object(self.vcad_object, self.materials, reset_camera=False) # Full rebuild required

    def _start_worker(self, gen, vcad_object, materials, cfg):
        worker = _BuildWorker(self, gen, vcad_object, materials, cfg)
        t = threading.Thread(target=worker.run, name=f"VTKBuild-{gen}", daemon=True)
        self._worker_thread = t
        t.start()

    def _post(self, EventClass, **kwargs):
        evt = EventClass(**kwargs)
        wx.PostEvent(self.event_target, evt)

    def _apply_payload(self, payload: dict):
        # Reset current props
        self.renderer.RemoveAllViewProps()
        self.current_iso_surface = None
        self.current_volume = None
        self.bbox_actor = None
        self.origin_actor = None

        # Update voxel size
        self.voxel_size = payload.get("voxel_size")

        # Optional items
        if payload.get("bbox") is not None:
            self.bbox_actor = payload["bbox"]
            self.renderer.AddActor(self.bbox_actor)
        if payload.get("origin") is not None:
            self.origin_actor = payload["origin"]
            self.renderer.AddActor(self.origin_actor)

        # Main renderable
        if payload.get("mode") == "vol":
            self.current_volume = payload["volume"]
            if self.current_volume is not None:
                self.renderer.AddVolume(self.current_volume)
        else:
            self.current_iso_surface = payload["actor"]
            if self.current_iso_surface is not None:
                self.renderer.AddActor(self.current_iso_surface)

        # Corner axis widget (needs interactor; GUI thread only)
        self.corner_axis_widget = self._create_corner_axis_widget()

        self.render_window.Render()
        if self._pending_reset_camera:
            self.reset_camera()
            self._pending_reset_camera = False

    def _create_bbox_actor(self, vcad_object):
        min_pt, max_pt = vcad_object.bounding_box()

        cube = vtkCubeSource()
        cube.SetBounds(min_pt.x, max_pt.x, min_pt.y, max_pt.y, min_pt.z, max_pt.z)

        cube_mapper = vtkPolyDataMapper()
        cube_mapper.SetInputConnection(cube.GetOutputPort())

        cube_actor = vtkActor()
        cube_actor.SetMapper(cube_mapper)
        cube_actor.GetProperty().SetOpacity(0.1)

        return cube_actor

    def _create_origin_actor(self):
        axes = vtkAxesActor()
        axes.SetTotalLength(10.0, 10.0, 10.0)
        axes.SetShaftTypeToLine()
        axes.SetNormalizedShaftLength(1.0, 1.0, 1.0)
        axes.SetNormalizedTipLength(0.2, 0.2, 0.2)
        axes.SetPosition(0.0, 0.0, 0.0)
        return axes

    def _create_corner_axis_widget(self):
        axes = vtkAxesActor()
        widget = vtkOrientationMarkerWidget()
        widget.SetOrientationMarker(axes)
        widget.SetInteractor(self.render_window.GetInteractor())
        widget.SetViewport(0.8, 0.8, 1.0, 1.0)
        widget.SetEnabled(1)
        widget.InteractiveOff()
        return widget

    def _create_volume_from_object(self, vcad_object, materials, voxel_size):
        volume_data = self._create_image_data_from_object(vcad_object, voxel_size, materials)

        volume_mapper = vtkSmartVolumeMapper()
        volume_mapper.SetInputData(volume_data)

        color_transfer_function = vtkColorTransferFunction()
        color_transfer_function.AddRGBPoint(0.0, 0.0, 0.0, 0.0)
        color_transfer_function.AddRGBPoint(255.0, 1.0, 1.0, 1.0)

        opacity_transfer_function = vtkPiecewiseFunction()
        opacity_transfer_function.AddPoint(0.0, 0.0)
        opacity_transfer_function.AddPoint(10.0, 0.2)
        opacity_transfer_function.AddPoint(128.0, 0.4)
        opacity_transfer_function.AddPoint(200.0, 0.8)
        opacity_transfer_function.AddPoint(255.0, 1.0)

        volume_property = vtkVolumeProperty()
        volume_property.SetColor(color_transfer_function)
        volume_property.SetScalarOpacity(opacity_transfer_function)
        volume_property.SetInterpolationTypeToLinear()
        volume_property.IndependentComponentsOff()

        volume = vtkVolume()
        volume.SetMapper(volume_mapper)
        volume.SetProperty(volume_property)
        return volume

    def _create_iso_surface_from_object(self, vcad_object, materials, voxel_size, iso_value=0.0):
        sdf_volume_data = self._create_sdf_from_object(vcad_object, voxel_size)

        def contour_progress_callback(caller, event):
            progress = caller.GetProgress()
            # Only update progress every five percent to reduce overhead
            if progress % 0.05 < 0.001:
                if self.iso_surface_contouring_progress_callback:
                    self.iso_surface_contouring_progress_callback(progress * 100.0)

        contour = vtkContourFilter()
        contour.AddObserver(vtkCommand.ProgressEvent, contour_progress_callback)
        contour.SetInputData(sdf_volume_data)
        contour.SetValue(0, iso_value)
        contour.Update()

        mapper = vtkPolyDataMapper()
        mapper.SetInputConnection(contour.GetOutputPort())

        actor = vtkActor()
        actor.SetMapper(mapper)

        points = contour.GetOutput().GetPoints()
        if points:
            colors = self._colors_for_points(vcad_object, materials, points, voxel_size)
            contour.GetOutput().GetPointData().SetScalars(colors)

        return actor

    def _create_image_data_from_object(self, vcad_object, voxel_size, materials):
        nx, ny, nz, data = vcad_object.toRGBAArray(voxel_size, materials, self.use_volume_blending, self.volume_sample_progress_callback)

        volume_data = vtkImageData()
        volume_data.SetDimensions(nx, ny, nz)
        volume_data.SetSpacing(voxel_size.x, voxel_size.y, voxel_size.z)

        width = nx * voxel_size.x
        height = ny * voxel_size.y
        depth = nz * voxel_size.z
        volume_data.SetOrigin(-width / 2, -height / 2, -depth / 2)

        vtk_data_array = vtk_np.numpy_to_vtk(
            num_array=data, deep=True, array_type=VTK_UNSIGNED_CHAR
        )
        vtk_data_array.SetNumberOfComponents(4)
        volume_data.GetPointData().SetScalars(vtk_data_array)

        return volume_data

    def _create_sdf_from_object(self, vcad_object, voxel_size):
        nx, ny, nz, sdf_data = vcad_object.toSignedDistanceArray(
            voxel_size, self.iso_surface_sample_progress_callback
        )

        # Ensure C-contiguous float32 (NO COPY if already correct)
        if not (sdf_data.dtype == np.float32 and sdf_data.flags['C_CONTIGUOUS']):
            sdf_data = np.ascontiguousarray(sdf_data, dtype=np.float32)

        sdf_volume_data = vtkImageData()
        sdf_volume_data.SetDimensions(nx, ny, nz)
        sdf_volume_data.SetSpacing(voxel_size.x, voxel_size.y, voxel_size.z)

        width = nx * voxel_size.x
        height = ny * voxel_size.y
        depth = nz * voxel_size.z
        sdf_volume_data.SetOrigin(-width / 2, -height / 2, -depth / 2)

        vtk_data_array = vtk_np.numpy_to_vtk(num_array=sdf_data, deep=False, array_type=VTK_FLOAT)
        vtk_data_array.SetNumberOfComponents(1)
        sdf_volume_data.GetPointData().SetScalars(vtk_data_array)

        # --- keepalive: prevent GC of the NumPy owner while VTK reads it ---
        # Either attach to the image:
        setattr(sdf_volume_data, "_np_ref", sdf_data)
        # (Or to the data array: setattr(vtk_data_array, "_np_ref", sdf_data))

        return sdf_volume_data

    def _colors_for_points(self, vcad_object, materials, points, voxel_size):
        pv_points = [pv.Vec3(*points.GetPoint(i)) for i in range(points.GetNumberOfPoints())]
        colors_as_rgb = vcad_object.sample_points_color(
            pv_points, materials, voxel_size, self.iso_surface_coloring_progress_callback
        )

        colors = vtkUnsignedCharArray()
        colors.SetNumberOfComponents(4)
        colors.SetName("Colors")

        for color in colors_as_rgb:
            r = int(color.x)
            g = int(color.y)
            b = int(color.z)
            colors.InsertNextTuple4(r, g, b, 255)

        return colors

    @staticmethod
    def _compute_voxel_size_for_quality_profile(vcad_object, profile: str) -> pv.Vec3:
        LOW_TARGET_VOXELS = 128
        MEDIUM_TARGET_VOXELS = 256
        HIGH_TARGET_VOXELS = 512
        ULTRA_TARGET_VOXELS = 1024
        
        min_pt, max_pt = vcad_object.bounding_box()
        max_dimension = max(
            max_pt.x - min_pt.x,
            max_pt.y - min_pt.y,
            max_pt.z - min_pt.z,
        )

        if profile == "low":
            computed_voxel_size = max_dimension / LOW_TARGET_VOXELS
        elif profile == "medium":
            computed_voxel_size = max_dimension / MEDIUM_TARGET_VOXELS
        elif profile == "high":
            computed_voxel_size = max_dimension / HIGH_TARGET_VOXELS
        elif profile == "ultra":
            computed_voxel_size = max_dimension / ULTRA_TARGET_VOXELS
        else:
            raise ValueError(f"Invalid quality profile to auto compute for: {profile}")

        return pv.Vec3(computed_voxel_size, computed_voxel_size, computed_voxel_size)


class _BuildWorker:
    def __init__(self, pipeline: VTKRenderPipeline, gen: int, vcad_object, materials, cfg: dict):
        self.pipeline = pipeline
        self.gen = gen
        self.vcad_object = vcad_object
        self.materials = materials
        self.cfg = cfg

    def run(self):
        p = self.pipeline
        try:
            old_iso_sample = p.iso_surface_sample_progress_callback
            old_iso_contour = p.iso_surface_contouring_progress_callback
            old_iso_color = p.iso_surface_coloring_progress_callback
            old_vol_sample = p.volume_sample_progress_callback
            p.iso_surface_sample_progress_callback = lambda v: p._post(IsoSampleEvent, progress=float(v))
            p.iso_surface_contouring_progress_callback = lambda v: p._post(IsoContourEvent, progress=float(v))
            p.iso_surface_coloring_progress_callback = lambda v: p._post(IsoColorEvent, progress=float(v))
            p.volume_sample_progress_callback = lambda v: p._post(VolSampleEvent, progress=float(v))

            # Compute heavy stuff (off-thread)
            voxel_size = p._compute_voxel_size_for_quality_profile(
                self.vcad_object, self.cfg["quality_profile"]
            )
            bbox_actor = p._create_bbox_actor(self.vcad_object) if self.cfg["show_bbox"] else None
            origin_actor = p._create_origin_actor() if self.cfg["show_origin"] else None

            if self.cfg["render_mode"] == "volumetric":
                volume = p._create_volume_from_object(self.vcad_object, self.materials, voxel_size)
                if self.cfg["use_volume_shading"] and volume is not None:
                    volume.GetProperty().ShadeOn()
                payload = {
                    "mode": "vol",
                    "voxel_size": voxel_size,
                    "volume": volume,
                    "bbox": bbox_actor,
                    "origin": origin_actor,
                }
            else:
                iso_actor = p._create_iso_surface_from_object(
                    self.vcad_object, self.materials, voxel_size, iso_value=0.0
                )
                payload = {
                    "mode": "iso",
                    "voxel_size": voxel_size,
                    "actor": iso_actor,
                    "bbox": bbox_actor,
                    "origin": origin_actor,
                }

            # Only the newest generation should apply
            def finish_on_ui():
                if self.gen != p._gen:
                    return
                p._apply_payload(payload)
                p._post(BuildFinishedEvent, generation=self.gen)

            wx.CallAfter(finish_on_ui)

        finally:
            # Restore original callbacks
            p.iso_surface_sample_progress_callback = old_iso_sample
            p.iso_surface_contouring_progress_callback = old_iso_contour
            p.iso_surface_coloring_progress_callback = old_iso_color
            p.volume_sample_progress_callback = old_vol_sample