import os
import sys
import subprocess
import shutil
import json

from pathlib import Path

import pcbnew
import wx

from .version import __version__
from .standards_dialog import StandardsDialog
from .part_dialog import PartDialog

class UGRDialog(wx.Dialog):
    # Program settings (populated on startup)
    settings_fs_unc_path = ""
    settings_folders = {}

    # Project Settings (populated on startup)
    project_name = ""
    submission_path = ""

    def __init__(self: "UGRDialog", parent: wx.Frame) -> None:
        super().__init__(parent, -1, "UGRacing Plugin Dialog")

        information_section = self.get_information_section()
        button_section = self.get_button_section()

        buttons = self.CreateButtonSizer(wx.OK)

        header = wx.BoxSizer(wx.HORIZONTAL)
        header.Add(information_section, 3, wx.ALL, 5)
        header.Add(button_section, 2, wx.ALL, 5)

        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(header, 0, wx.EXPAND | wx.ALL, 5)
        box.Add(buttons, 0, wx.EXPAND | wx.ALL, 5)

        self.SetSizerAndFit(box)

        with open(os.path.join(os.path.dirname(__file__), "settings.json")) as f:
            d = json.load(f)
            print(d)

            self.settings_fs_unc_path = d["Fileshare_UNC_Path"]
            self.settings_folders = d["Folders"]



    def get_information_section(self) -> wx.BoxSizer:
        source_dir = os.path.dirname(__file__)
        icon_file_name = os.path.join(source_dir, "icon_full.png")
        icon = wx.Image(icon_file_name, wx.BITMAP_TYPE_ANY)
        icon_bitmap = wx.Bitmap(icon)
        static_icon_bitmap = wx.StaticBitmap(self, wx.ID_ANY, icon_bitmap)

        font = wx.Font(
            12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD
        )

        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(static_icon_bitmap, 0, wx.ALL, 5)
        text = wx.StaticText(self, -1, f"UGR plugin version: {__version__}",)
        box.Add(text, 0, wx.ALL, 5)

        return box

    def get_button_section(self) -> wx.BoxSizer:
        box = wx.BoxSizer(wx.VERTICAL)

        init_folder = wx.Button(self, -1, label="Initialise Folder")
        init_folder.Bind(wx.EVT_BUTTON, self.on_init_folder)

        set_defaults = wx.Button(self, -1, label="Set Defaults")
        set_defaults.Bind(wx.EVT_BUTTON, self.on_set_defaults)

        standards = wx.Button(self, -1, label="Standards Check")
        standards.Bind(wx.EVT_BUTTON, self.on_standards_click)

        box.Add(init_folder, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        box.Add(set_defaults, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        box.Add(standards, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        return box

    def on_standards_click(self, event: wx.CommandEvent) -> None:
        try:
            standardsdialog = StandardsDialog(self)
        except Exception as e:
            ebox = wx.MessageBox(f"Dialog creation failed: {e}")
            ebox.Show()

        if standardsdialog.ShowModal() == wx.ID_OK:
            standardsdialog.checkStandards()

    def on_set_defaults(self, event: wx.CommandEvent) -> None:
        try:
            board = pcbnew.GetBoard()
            ds = board.GetDesignSettings()

            # Tracks / vias
            ds.SetTrackWidth(int(0.2 * 1e6))    # 0.2 mm
            ds.SetClearance(int(0.2 * 1e6))      # 0.2 mm
            ds.SetViaSize(int(0.4 * 1e6))        # 0.4 mm
            ds.SetViaDrill(int(0.25 * 1e6))       # 0.25 mm 
        except Exception as e:
            ebox = wx.MessageBox(f"Failed to set defaults: {e}")
            ebox.Show()

    def confirm_fileshare(self):
        vpn_box = wx.MessageDialog(self, "Fileshare connection required\n\nThe following action requires connection to the fileshare. If you aren't connected to Eduroam, or on a university/GUES computer, please connect the VPN now.\n\nPress continue to proceed.", "Fileshare required!",style=wx.YES_NO)
        vpn_box.SetYesNoLabels("Continue", "Cancel")
        res = vpn_box.ShowModal()

        if res == wx.ID_YES:
            res = os.path.exists(r'\\lumiere.eng-ad.gla.ac.uk\groups\UGR')

            if not res:
                wx.MessageBox("Error: Failed to connect to fileshare. Please check your internet/VPN connection and try again.")

        else:
            res = False

        return res
    
    def get_next_id(self, folder):
        subfolders = [ f.path for f in os.scandir(folder) if f.is_dir() ]

        folder_name = os.path.basename(folder)
        folder_id = folder_name[0:folder_name.index(" ")]
        id_base = folder_id + "."
        largest_id = 0

        for f in subfolders:
            name = os.path.basename(f)
            id = name[0:name.index(" ")]
            id_end = id[id.rfind(".")+1:]

            if int(id_end) > largest_id: 
                largest_id = int(id_end)

        next_id = id_base + str(largest_id+1)
        return next_id
    
    def compress_and_upload(self, zipname):
        board = pcbnew.GetBoard()
        folder = os.getcwd()

        shutil.make_archive(zipname, 'zip', folder)


    def on_init_folder(self, event: wx.CommandEvent) -> None:
        try:
            board = pcbnew.GetBoard()
            if (self.confirm_fileshare()):
                dlg = PartDialog(None, self.settings_folders)

                if dlg.ShowModal() == wx.ID_OK:
                    car, subteam, subteam_path, part = dlg.get_values()
                    print(f"Car: {car}, Subteam: {subteam}, Part: {part}")

                dlg.Destroy()

                subteam_path = os.path.join(self.settings_fs_unc_path, subteam_path)

                next_id = self.get_next_id(subteam_path)

                folder_name = f"{next_id} - {part}"
                folder_path = f"{subteam_path}\{folder_name}"

                dest = wx.MessageBox(f"Your project will be uploaded to the following folder:\n{folder_path}")

                os.makedirs(folder_path)
                self.compress_and_upload(f"{folder_path}\\{car}_{part}")

                # TODO: VERSIONING

                

        except Exception as e:
            ebox = wx.MessageBox(f"Error occurred: {e}")
            ebox.Show()
