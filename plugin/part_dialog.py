import wx

class PartDialog(wx.Dialog):
    def __init__(self, parent, car_dict):
        super().__init__(parent, title="Select Part", size=(350, 220))

        self.car_dict = car_dict

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Car dropdown
        car_label = wx.StaticText(panel, label="Car:")
        self.car_choice = wx.Choice(panel, choices=list(car_dict.keys()))
        self.car_choice.Bind(wx.EVT_CHOICE, self.on_car_change)
        self.car_choice.SetSelection(0)

        # Subteam dropdown (populated after car is chosen)
        subteam_label = wx.StaticText(panel, label="Subteam:")
        self.subteam_choice = wx.Choice(panel)

        # Populate subteams for the initially selected car
        self.update_subteams(self.car_choice.GetStringSelection())

        # Part name text box
        part_label = wx.StaticText(panel, label="Part name:")
        self.part_text = wx.TextCtrl(panel)

        # Layout
        grid = wx.FlexGridSizer(3, 2, 10, 10)
        grid.AddMany([
            (car_label, 0, wx.ALIGN_CENTER_VERTICAL), (self.car_choice, 1, wx.EXPAND),
            (subteam_label, 0, wx.ALIGN_CENTER_VERTICAL), (self.subteam_choice, 1, wx.EXPAND),
            (part_label, 0, wx.ALIGN_CENTER_VERTICAL), (self.part_text, 1, wx.EXPAND),
        ])
        grid.AddGrowableCol(1, 1)

        vbox.Add(grid, 1, wx.ALL | wx.EXPAND, 15)

        # OK / Cancel buttons
        hbox = wx.StdDialogButtonSizer()
        ok_btn = wx.Button(panel, wx.ID_OK)
        cancel_btn = wx.Button(panel, wx.ID_CANCEL)
        hbox.AddButton(ok_btn)
        hbox.AddButton(cancel_btn)
        hbox.Realize()

        vbox.Add(hbox, 0, wx.ALIGN_CENTER | wx.ALL, 10)

        panel.SetSizer(vbox)

    def update_subteams(self, car):
        """Update subteam dropdown when car changes."""
        self.subteam_choice.Clear()
        subteams = list(self.car_dict[car].keys())
        self.subteam_choice.AppendItems(subteams)
        if subteams:
            self.subteam_choice.SetSelection(0)

    def on_car_change(self, event):
        selected_car = self.car_choice.GetStringSelection()
        self.update_subteams(selected_car)

    def get_values(self):
        car = self.car_choice.GetStringSelection()
        subteam = self.subteam_choice.GetStringSelection()
        part = self.part_text.GetValue()
        subteam_path = self.car_dict[car].get(subteam, "")
        return car, subteam, subteam_path, part