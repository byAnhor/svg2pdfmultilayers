# svg2pdfmultilayers is a utility to export multilayered SVG to PDF.
# Copyright (C) 2021 Anita Orhand
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import wx
import wx.lib.scrolledpanel as scrolled

class IOTab(scrolled.ScrolledPanel):
    def __init__(self,parent,main_gui):
        super(IOTab, self).__init__(parent)
        
        vert_sizer = wx.BoxSizer(wx.VERTICAL)

        # add the various parameter inputs
        # Display the selected PDF
        newline = wx.BoxSizer(wx.HORIZONTAL)
        in_doc_btn = wx.Button(self, label=_('Select input SVG with layers'))
        in_doc_btn.Bind(wx.EVT_BUTTON,main_gui.on_open)
        newline.Add(in_doc_btn, flag=wx.ALIGN_CENTRE_VERTICAL)
        self.input_fname_display = wx.StaticText(self, label=_('None'))
        newline.Add(self.input_fname_display, flag=wx.ALIGN_CENTRE_VERTICAL|wx.LEFT, border=5)
        vert_sizer.Add(newline,flag=wx.TOP|wx.LEFT|wx.RIGHT,border=10)

        newline = wx.BoxSizer(wx.HORIZONTAL)
        out_doc_btn = wx.Button(self, label=_('Save output as'))
        out_doc_btn.Bind(wx.EVT_BUTTON,main_gui.on_output)
        newline.Add(out_doc_btn, flag=wx.ALIGN_CENTRE_VERTICAL)
        self.output_fname_display = wx.StaticText(self, label=_('None'))
        newline.Add(self.output_fname_display, flag=wx.ALIGN_CENTRE_VERTICAL|wx.LEFT, border=5)
        vert_sizer.Add(newline,flag=wx.TOP|wx.LEFT|wx.RIGHT,border=10)

        self.generate_a0 = wx.CheckBox(self,label=_('Generate A0'))
        self.generate_a0.SetValue(1)
        self.generate_a0.Bind(wx.EVT_CHECKBOX,self.on_generate_a0a4_checked)
        vert_sizer.Add(self.generate_a0,flag=wx.TOP|wx.LEFT|wx.RIGHT,border=10)
        
        newline = wx.BoxSizer(wx.HORIZONTAL)
        self.generate_a4 = wx.CheckBox(self,label=_('Generate A4'))
        self.generate_a4.SetValue(1)
        self.generate_a4.Bind(wx.EVT_CHECKBOX,self.on_generate_a0a4_checked)
        newline.Add(self.generate_a4, flag=wx.ALIGN_CENTRE_VERTICAL)
        self.in_canvas_doc_btn = wx.Button(self, label=_('Select input A4 SVG canvas'))
        self.in_canvas_doc_btn.Bind(wx.EVT_BUTTON,main_gui.on_open_canvas)
        newline.Add(self.in_canvas_doc_btn, flag=wx.ALIGN_CENTRE_VERTICAL)
        self.input_canevas_fname_display = wx.StaticText(self, label=_('None'))
        newline.Add(self.input_canevas_fname_display, flag=wx.ALIGN_CENTRE_VERTICAL|wx.LEFT, border=5)
        vert_sizer.Add(newline,flag=wx.TOP|wx.LEFT|wx.RIGHT,border=10)      
        
        self.on_generate_a0a4_checked(event=None)

        self.SetSizer(vert_sizer)
        self.SetupScrolling()
        self.SetBackgroundColour(parent.GetBackgroundColour())
        
    def load_new(self,filename):
        self.input_fname_display.SetLabel(filename)
        self.output_fname_display.SetLabel(label=_('None'))
        
    def load_new_canvas(self,filename):
        self.input_canevas_fname_display.SetLabel(filename)
         
    def on_generate_a0a4_checked(self,event):
        self.generate_a0_checked = bool(self.generate_a0.GetValue())
        self.generate_a4_checked = bool(self.generate_a4.GetValue())
        self.in_canvas_doc_btn.Enable(self.generate_a4_checked)
        
        