import wx
import pcbnew
import os

acc_fp_R = ["Resistor_SMD:R_0603_1608Metric_Pad0.98x0.95mm_HandSolder"]
acc_fp_C = ["Capacitor_SMD:C_0603_1608Metric_Pad1.08x0.95mm_HandSolder", "Capacitor_SMD:C_0805_2012Metric_Pad1.18x1.45mm_HandSolder","Capacitor_SMD:C_1210_3225Metric_Pad1.33x2.70mm_HandSolder"]
acc_fp_L = ["Inductor_SMD:L_1210_3225Metric_Pad1.42x2.65mm_HandSolder"]
acc_fp_U = ["Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", "Package_SO:SOIC-10_3.9x4.9mm_P1mm", "Package_SO:SOIC-14_3.9x8.7mm_P1.27mm", "SOIC-16_3.9x9.9mm_P1.27mm"]

class StandardsDialog(wx.Dialog):
    def __init__(self, parent: wx.Frame):
        super().__init__(parent, title="Standards Checker", size=(300,200))

        vbox = wx.BoxSizer(wx.VERTICAL)
        
        exp_label = wx.StaticText(self, label='''Click the button below to compare your PCB to standards set out by the Electrical team.

The program will check the following:
 - Component Footprints
                                  
Click OK to continue with the standards check. Results will be shown when complete.''')
        vbox.Add(exp_label, 0, wx.ALL, 5)

        buttons = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        vbox.Add(buttons, 0, wx.ALIGN_CENTER | wx.ALL, 10)


        self.SetSizerAndFit(vbox)

    
    def checkStandards(self):
        board = pcbnew.GetBoard()
        ns_found = 0
        ns_footprints = "The following non-standard footprints were found:\n"

        for footprint in board.GetFootprints():
            ref = footprint.GetReference()
            fpid = footprint.GetFPIDAsString()

            if (
                (ref[0] == "R" and ref[0:3] != "REF" and not fpid in acc_fp_R) or 
                (ref[0] == "C" and not fpid in acc_fp_C) or 
                (ref[0] == "L" and not fpid in acc_fp_L) or 
                (ref[0] == "U" and not fpid in acc_fp_U)
            ):
                ns_found += 1
                ns_footprints += f"\nFootprint Reference: {ref}\nFootprint ID: {fpid}"


        if ns_found == 0:
            wx.MessageBox(f"Standards Check Complete\n\nNo non-standard footprints found. Your PCB complies with UGR standard components!")
        else:
            wx.MessageBox(f"Standards Check Complete\n\n{ns_footprints}\n\nThis output will be saved to your project folder as StandardsCheck.txt")
            board_filename = board.GetFileName()
            if not board_filename:
                print("Board has no filename - save the project first")
            else:
                # Get the directory path
                project_dir = os.path.dirname(board_filename)
                
                # Create the full file path
                file_path = os.path.join(project_dir, "StandardsCheck.txt")
                
                # Write the content to the file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(ns_footprints)      
