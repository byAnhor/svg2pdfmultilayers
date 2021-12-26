# -*- coding: utf-8 -*-
# svg2pdfmultilayers is a utility to export multilayered SVG to PDF.
# Copyright (C) 2021 Anita Orhand
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import sys
import os
import wx
import wx.lib.scrolledpanel as scrolled
from frozenclass import FrozenClass

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class LayerExtractTab(FrozenClass, scrolled.ScrolledPanel):
    def __init__(self,parent,main_gui):
        super(LayerExtractTab, self).__init__(parent)
        
        self.main_gui = main_gui
        
        globalsizer = wx.FlexGridSizer(1,1,10,10)

        newline = wx.BoxSizer(wx.HORIZONTAL)
        self.layers_hierarchy = wx.CheckListBox(self,name='Layers hierarchy', choices=[])        
        newline.Add(self.layers_hierarchy, flag=wx.ALL, border=10)
        
        globalsizer.Add(newline,flag=wx.TOP|wx.LEFT|wx.RIGHT,border=10)

        self.SetSizer(globalsizer)
        self.SetupScrolling()
        self.SetBackgroundColour(parent.GetBackgroundColour())
                      
        self._freeze()

