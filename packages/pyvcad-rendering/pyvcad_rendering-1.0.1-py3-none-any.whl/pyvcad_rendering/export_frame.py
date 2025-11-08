import wx
import os
import sys
import subprocess

import pyvcad_rendering.compiler_input_ui as compiler_ui



class CompilerSelectionPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.compilers = [
            "GCVF Inkjet (.gcvf)",
            "Direct Material Inkjet (PNG Stack)",
            # "Color Inkjet (PNG Stack)",
            "Myerson Inkjet (Bitmap Stack)",
            "Meshes (.STL)",
            "Finite Element Mesh (.INP)",
            "Vat Photo (Bitmap Stack)"
        ]
        self.compiler_map = {
            "GCVF Inkjet (.gcvf)": (compiler_ui.GCVFInkjetPanel, compiler_ui.GCVFInkjetProgressPanel),
            "Direct Material Inkjet (PNG Stack)": (compiler_ui.DirectMaterialInkjetPanel, compiler_ui.DirectMaterialInkjetProgressPanel),
            # "Color Inkjet (PNG Stack)": (compiler_ui.ColorInkjetPanel, None),
            "Myerson Inkjet (Bitmap Stack)": (compiler_ui.MyersonInkjetPanel, compiler_ui.MyersonInkjetProgressPanel),
            "Meshes (.STL)": (compiler_ui.MeshesPanel, compiler_ui.MeshesProgressPanel),
            "Finite Element Mesh (.INP)": (compiler_ui.FiniteElementMeshPanel, compiler_ui.FiniteElementMeshProgressPanel),
            "Vat Photo (Bitmap Stack)": (compiler_ui.VatPhotoPanel, compiler_ui.VatPhotoProgressPanel)
        }
        self.compiler_descriptions = {
            "GCVF Inkjet (.gcvf)": "Description for GCVF Inkjet (.gcvf)",
            "Direct Material Inkjet (PNG Stack)": "Description for Direct Material Inkjet (PNG Stack)",
            "Color Inkjet (PNG Stack)": "Description for Color Inkjet (PNG Stack)",
            "Myerson Inkjet (Bitmap Stack)": "Description for Myerson Inkjet (Bitmap Stack)",
            "Meshes (.STL)": "Description for Meshes (.STL)",
            "Finite Element Mesh (.INP)": "Description for Finite Element Mesh (.INP)",
            "Vat Photo (Bitmap Stack)": "Description for Vat Photo (Bitmap Stack)"
        }

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.StaticText(self, label="Select a compiler:"), 0, wx.ALL, 5)
        self.compiler_choice = wx.Choice(self, choices=self.compilers)
        sizer.Add(self.compiler_choice, 0, wx.ALL | wx.EXPAND, 5)

        self.description_text = wx.StaticText(self, label="")
        sizer.Add(self.description_text, 1, wx.ALL | wx.EXPAND, 5)

        self.SetSizer(sizer)

        self.compiler_choice.Bind(wx.EVT_CHOICE, self.on_compiler_select)
        self.compiler_choice.SetSelection(0)
        self.on_compiler_select(None)

    def on_compiler_select(self, event):
        selection = self.compiler_choice.GetStringSelection()
        description = self.compiler_descriptions.get(selection, "")
        self.description_text.SetLabel(description)
        self.GetParent().Layout()

    def get_selected_compiler_panel(self, parent, root, materials):
        selection = self.compiler_choice.GetStringSelection()
        panel_classes = self.compiler_map.get(selection)
        if panel_classes and panel_classes[0]:
            return panel_classes[0](parent, root, materials)
        return None

    def get_selected_progress_panel(self, parent, export_options):
        selection = self.compiler_choice.GetStringSelection()
        panel_classes = self.compiler_map.get(selection)
        if panel_classes and panel_classes[1]:
            return panel_classes[1](parent, export_options)
        return None

class ExportFrame(wx.Frame):
    def __init__(self, root, materials, *args, **kwargs):
        super().__init__(None, title="Export OpenVCAD Design", size=(800, 600), *args, **kwargs)
        self.root = root
        self.materials = materials

        self.panel = wx.Panel(self)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.panel.SetSizer(self.sizer)

        self.book = wx.Simplebook(self.panel)

        # Step 1: Compiler Selection
        self.compiler_selection_panel = CompilerSelectionPanel(self.book)
        self.book.AddPage(self.compiler_selection_panel, "Select Compiler")

        # Step 2: Compiler Inputs (placeholder)
        self.compiler_input_panel = wx.Panel(self.book)
        self.book.AddPage(self.compiler_input_panel, "Compiler Inputs")

        # Step 3: Progress
        self.progress_panel = wx.Panel(self.book)
        self.book.AddPage(self.progress_panel, "Progress")

        # Step 4: Confirmation
        confirmation_panel = wx.Panel(self.book)
        confirmation_sizer = wx.BoxSizer(wx.VERTICAL)
        self.confirmation_text = wx.StaticText(confirmation_panel, label="")
        confirmation_sizer.Add(self.confirmation_text, 0, wx.ALL, 5)
        self.open_folder_button = wx.Button(confirmation_panel, label="Open Output Folder")
        self.open_folder_button.Bind(wx.EVT_BUTTON, self.on_open_folder)
        self.open_folder_button.Hide()
        confirmation_sizer.Add(self.open_folder_button, 0, wx.ALL, 5)
        confirmation_panel.SetSizer(confirmation_sizer)
        self.book.AddPage(confirmation_panel, "Confirmation")

        self.sizer.Add(self.book, 1, wx.EXPAND | wx.ALL, 25)

        self.btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.back_btn = wx.Button(self.panel, label="Back")
        self.next_btn = wx.Button(self.panel, label="Next")
        self.back_btn.Bind(wx.EVT_BUTTON, self.on_back)
        self.next_btn.Bind(wx.EVT_BUTTON, self.on_next)
        self.btn_sizer.Add(self.back_btn, 0, wx.ALL, 5)
        self.btn_sizer.Add(self.next_btn, 0, wx.ALL, 5)
        self.sizer.Add(self.btn_sizer, 0, wx.ALIGN_RIGHT | wx.RIGHT | wx.BOTTOM, 10)

        self.update_buttons()
        self.Centre()
        self.Show()
        self.export_file_path = None

    def on_back(self, event):
        current_page = self.book.GetSelection()
        if current_page > 0:
            if current_page == 1: # From inputs to compiler selection
                self.open_folder_button.Hide()
            self.book.SetSelection(current_page - 1)
        self.update_buttons()

    def on_next(self, event):
        current_page = self.book.GetSelection()
        if current_page < self.book.GetPageCount() - 1:
            if current_page == 0: # From compiler selection to inputs
                self.update_compiler_input_panel()
                self.book.SetSelection(current_page + 1)
            elif current_page == 1: # From inputs to progress
                if self.start_export():
                    self.book.SetSelection(current_page + 1)
            else:
                self.book.SetSelection(current_page + 1)
        elif current_page == self.book.GetPageCount() - 1:
            # On the final confirmation page, close the app
            self.Close()
        self.update_buttons()

    def update_compiler_input_panel(self):
        # Remove old panel
        self.book.RemovePage(1)

        # Add new panel
        new_panel = self.compiler_selection_panel.get_selected_compiler_panel(self.book, self.root, self.materials)
        if new_panel:
            self.compiler_input_panel = new_panel
        else:
            # Fallback to an empty panel
            self.compiler_input_panel = wx.Panel(self.book)
        self.book.InsertPage(1, self.compiler_input_panel, "Compiler Inputs")

    def start_export(self):
        export_options = self.compiler_input_panel.get_export_options()

        # Check for file_path or output_directory
        if not export_options.get("file_path") and not export_options.get("output_directory"):
            wx.MessageBox("File path or output directory cannot be empty.", "Error", wx.OK | wx.ICON_ERROR)
            return False

        self.book.RemovePage(2) # Remove old progress panel

        new_progress_panel = self.compiler_selection_panel.get_selected_progress_panel(self.book, export_options)

        if new_progress_panel:
            self.progress_panel = new_progress_panel
            self.book.InsertPage(2, self.progress_panel, "Progress")
            self.progress_panel.start_export()
            return True
        else:
            # Fallback for compilers without a progress panel
            self.book.InsertPage(2, wx.Panel(self.book), "Progress")
            wx.MessageBox("This compiler does not have a progress panel implemented yet.", "Info", wx.OK | wx.ICON_INFORMATION)
            return False

    def on_export_complete(self, file_path, elapsed_time):
        self.export_file_path = file_path
        self.confirmation_text.SetLabel(f"Export completed in {elapsed_time}.")
        self.open_folder_button.Show()
        self.book.SetSelection(3) # Go to confirmation page
        self.update_buttons()

    def on_open_folder(self, event):
        if self.export_file_path:
            dir_path = os.path.dirname(self.export_file_path)
            # Open the directory in the system's file explorer
            if sys.platform == "win32":
                os.startfile(dir_path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", dir_path])
            else:
                subprocess.Popen(["xdg-open", dir_path])

    def update_buttons(self):
        current_page = self.book.GetSelection()
        # Disable back on progress page (2) and confirmation page (3)
        self.back_btn.Enable(current_page > 0 and current_page != 2 and current_page != 3)
        self.next_btn.SetLabel("Next")
        if current_page == self.book.GetPageCount() - 2: # Progress page
            self.next_btn.Enable(False)
        elif current_page == self.book.GetPageCount() - 1: # Confirmation page
            self.next_btn.SetLabel("Finish")
            self.next_btn.Enable(True)
        else:
            self.next_btn.Enable(True)

