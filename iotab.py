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
import wx.lib.buttons as buts
import fitz

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class IOTab(scrolled.ScrolledPanel):
    def __init__(self,parent,main_gui):
        super(IOTab, self).__init__(parent)
        
        vert_sizer = wx.BoxSizer(wx.VERTICAL)

        # add the various parameter inputs
        # Display the selected PDF
        newline = wx.BoxSizer(wx.HORIZONTAL)
        in_doc_btn = buts.GenBitmapTextButton(self, -1, bitmap=wx.Bitmap(resource_path("openXS.ico")), label= "Select input SVG with layers")
        in_doc_btn.Bind(wx.EVT_BUTTON,main_gui.on_open)
        newline.Add(in_doc_btn, flag=wx.ALIGN_CENTRE_VERTICAL)
        self.input_fname_display = wx.StaticText(self, label=_('None'))
        newline.Add(self.input_fname_display, flag=wx.ALIGN_CENTRE_VERTICAL|wx.LEFT, border=5)
        vert_sizer.Add(newline,flag=wx.TOP|wx.LEFT|wx.RIGHT,border=10)

        newline = wx.BoxSizer(wx.HORIZONTAL)
        self.out_doc_btn = buts.GenBitmapTextButton(self, -1, bitmap=wx.Bitmap(resource_path("savepdfXS.ico")), label= "Save output as PDF")
        self.out_doc_btn.Bind(wx.EVT_BUTTON,main_gui.on_output)
        newline.Add(self.out_doc_btn, flag=wx.ALIGN_CENTRE_VERTICAL)
        self.output_fname_display = wx.StaticText(self, label=_('None'))
        newline.Add(self.output_fname_display, flag=wx.ALIGN_CENTRE_VERTICAL|wx.LEFT, border=5)
        vert_sizer.Add(newline,flag=wx.TOP|wx.LEFT|wx.RIGHT,border=10)

        newline = wx.BoxSizer(wx.HORIZONTAL)
        self.generate_hidden_layers = wx.CheckBox(self,label=_('Generate hidden layers'))
        self.generate_hidden_layers.SetValue(0)
        self.generate_hidden_layers.Bind(wx.EVT_CHECKBOX,self.on_generate_hidden_layers_checked)
        newline.Add(self.generate_hidden_layers, flag=wx.ALL, border=10)
        vert_sizer.Add(newline,flag=wx.TOP|wx.LEFT|wx.RIGHT,border=10)

        self.boxA0 = wx.StaticBox(self,label='Full size PDF generation')
        boxA0sizer = wx.StaticBoxSizer(self.boxA0, wx.VERTICAL)
        self.generate_a0 = wx.CheckBox(self,label=_('Generate full size PDF'))
        self.generate_a0.SetValue(1)
        self.generate_a0.Bind(wx.EVT_CHECKBOX,self.on_generate_a0a4_checked)
        boxA0sizer.Add(self.generate_a0, flag=wx.ALL, border=10)
        vert_sizer.Add(boxA0sizer, flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT, border=10)

        self.boxA4 = wx.StaticBox(self,label='A4 PDF generation')
        boxA4sizer = wx.StaticBoxSizer(self.boxA4, wx.VERTICAL)
        self.generate_a4 = wx.CheckBox(self,label=_('Generate A4'))
        self.generate_a4.SetValue(1)
        self.generate_a4.Bind(wx.EVT_CHECKBOX,self.on_generate_a0a4_checked)
        boxA4sizer.Add(self.generate_a4, flag=wx.ALL, border=10)
        
        """newline = wx.BoxSizer(wx.HORIZONTAL)
        newline.Add(wx.StaticText(self, label='    '))
        self.in_canvas_doc_btn = wx.Button(self, label=_('Select input A4 SVG canvas'))
        self.in_canvas_doc_btn.Bind(wx.EVT_BUTTON,main_gui.on_open_canvas)
        newline.Add(self.in_canvas_doc_btn, flag=wx.ALIGN_CENTRE_VERTICAL)
        self.input_canevas_fname_display = wx.StaticText(self, label=_('None'))
        newline.Add(self.input_canevas_fname_display, flag=wx.ALIGN_CENTRE_VERTICAL|wx.LEFT, border=5)
        boxA4sizer.Add(newline, flag=wx.ALL, border=10)"""

        newline = wx.BoxSizer(wx.HORIZONTAL)
        newline.Add(wx.StaticText(self, label='    '))
        boxorientation = wx.StaticBox(self,label='Canvas', size=(200,200))
        boxorientationsizer = wx.StaticBoxSizer(boxorientation, wx.VERTICAL)
        self.generate_A4_landscape_or_portrait_toggle = wx.ToggleButton(self)
        self.generate_A4_landscape_or_portrait_toggle.Bind(wx.EVT_TOGGLEBUTTON,self.on_generate_A4_landscape_or_portrait_toggle) 
        self.generate_A4_landscape_or_portrait_toggle.SetValue(True)
        boxorientationsizer.Add(self.generate_A4_landscape_or_portrait_toggle, flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, border=10)
        self.generate_A4_percent_slider = wx.Slider(self, value = 80, minValue = 70, maxValue = 100, size=(180,20), style = wx.SL_HORIZONTAL|wx.SL_LABELS|wx.SL_TICKS|wx.SL_TOP)
        self.generate_A4_percent_slider.SetTickFreq(5)
        self.generate_A4_percent_slider.Bind(wx.EVT_SLIDER, self.on_generate_A4_percent_scroll)
        #self.generate_A4_percent_slider.Bind(wx.EVT_SCROLL, self.on_generate_A4_percent_scroll)
        self.generate_A4_percent_slider.SetValue(80)
        boxorientationsizer.Add(self.generate_A4_percent_slider, flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, border=10)
        newline.Add(boxorientationsizer, flag=wx.ALIGN_CENTRE_VERTICAL)

        newline.Add(wx.StaticText(self, label='    '))
        self.assembly_page_mode = ['4 sides (center)', '2 sides (top-left)']     
        self.generate_assembly_page = wx.RadioBox(self, label = 'Assembly page', choices = self.assembly_page_mode, majorDimension = 3, style = wx.RA_SPECIFY_ROWS)
        self.generate_assembly_page.Bind(wx.EVT_RADIOBOX,self.on_generate_assembly_page_checked) 
        newline.Add(self.generate_assembly_page, flag=wx.ALIGN_TOP)
        
        newline.Add(wx.StaticText(self, label='    '))
        self.assembly_mark_mode = ['No', 'LxCy', 'A-A']     
        self.generate_assembly_mark = wx.RadioBox(self, label = 'Assembly mark', choices = self.assembly_mark_mode, majorDimension = 3, style = wx.RA_SPECIFY_ROWS)
        self.generate_assembly_mark.Bind(wx.EVT_RADIOBOX,self.on_generate_assembly_mark_checked) 
        newline.Add(self.generate_assembly_mark, flag=wx.ALIGN_TOP)
        
        newline.Add(wx.StaticText(self, label='    '))
        boxorder = wx.StaticBox(self,label='Generation order')
        boxordersizer = wx.StaticBoxSizer(boxorder, wx.VERTICAL)
        self.generate_order_leftright_or_topdown_toggle = wx.ToggleButton(self)
        self.generate_order_leftright_or_topdown_toggle.Bind(wx.EVT_TOGGLEBUTTON,self.on_generate_order_leftright_or_topdown_toggle) 
        self.generate_order_leftright_or_topdown_toggle.SetValue(True)
        boxordersizer.Add(self.generate_order_leftright_or_topdown_toggle, flag=wx.ALL, border=10)
        newline.Add(boxordersizer, flag=wx.ALIGN_TOP)
        
        boxA4sizer.Add(newline, flag=wx.ALL, border=10)

        vert_sizer.Add(boxA4sizer, flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT, border=10)
       
        self.on_generate_a0a4_checked(event=None)
        self.on_generate_assembly_mark_checked(event=None)
        self.on_generate_assembly_page_checked(event=None)
        self.on_generate_order_leftright_or_topdown_toggle(event=None)  
        self.on_generate_A4_landscape_or_portrait_toggle(event=None)

        self.SetSizer(vert_sizer)
        self.SetupScrolling()
        self.SetBackgroundColour(parent.GetBackgroundColour())
        
    def load_new(self,filenames):
        self.input_fname_display.SetLabel(' '.join(filenames))
        if len(filenames) == 1:
            self.output_fname_display.SetLabel(label=_('Select the output PDF filename'))
            self.out_doc_btn.Enable(True)
        else:
            self.output_fname_display.SetLabel(label=_('PDF filename automatically build (see AutoGenPDF directory)'))
            self.out_doc_btn.Enable(False)

    def load_new_canvas(self,filename):
        self.input_canevas_fname_display.SetLabel(filename)
        
    def on_generate_hidden_layers_checked(self,event):
        self.generate_hidden_layers_checked = bool(self.generate_hidden_layers.GetValue())
        
    def on_generate_a0a4_checked(self,event):
        self.generate_a0_checked = bool(self.generate_a0.GetValue())
        self.generate_a4_checked = bool(self.generate_a4.GetValue())
        self.generate_order_leftright_or_topdown_toggle.Enable(self.generate_a4_checked)
        self.generate_assembly_mark.Enable(self.generate_a4_checked)
        self.generate_assembly_page.Enable(self.generate_a4_checked)
        if self.generate_a0_checked and self.output_fname_display.Label != 'None':
            self.boxA0.SetLabel("Full size PDF generation : %s"%self.output_fname_display.Label.replace('.pdf', '.A0.pdf'))
        else:
            self.boxA0.SetLabel("Full size PDF generation")
        if self.generate_a4_checked and self.output_fname_display.Label != 'None':
            self.boxA4.SetLabel("Full size PDF generation : %s"%self.output_fname_display.Label.replace('.pdf', '.A4.pdf'))
        else:
            self.boxA4.SetLabel("Full size PDF generation")
            
    def on_generate_assembly_mark_checked(self,event):
        self.generate_assembly_mark_choice = self.assembly_mark_mode.index(self.generate_assembly_mark.GetStringSelection())
        
    def on_generate_assembly_page_checked(self,event):
        self.generate_assembly_page_choice = self.assembly_page_mode.index(self.generate_assembly_page.GetStringSelection())

    def on_generate_order_leftright_or_topdown_toggle(self,event):
        self.generate_order_leftright_or_topdown = "leftright" if self.generate_order_leftright_or_topdown_toggle.GetValue() else "topdown"
        if self.generate_order_leftright_or_topdown == "leftright":
            self.generate_order_leftright_or_topdown_toggle.SetBitmap(wx.Bitmap(resource_path("leftright.png")))
        else:
            self.generate_order_leftright_or_topdown_toggle.SetBitmap(wx.Bitmap(resource_path("topdown.png")))
        
    def on_generate_A4_landscape_or_portrait_toggle(self,event):
        self.generate_A4_landscape_or_portrait = "Portrait" if self.generate_A4_landscape_or_portrait_toggle.GetValue() else "Landscape"
        if self.generate_A4_landscape_or_portrait == "Portrait":
            self.generate_A4_landscape_or_portrait_toggle.SetBitmap(wx.Bitmap(resource_path("portrait.png")))
        else:
            self.generate_A4_landscape_or_portrait_toggle.SetBitmap(wx.Bitmap(resource_path("landscape.png")))
        self.canvas_construction()

    def on_generate_A4_percent_scroll(self,event):
        print(_('scroll %s')%self.generate_A4_percent_slider.GetValue())
        self.canvas_construction()

    def canvas_construction(self):
        doc = fitz.open()  
        page = doc.new_page()
        sliderpercent = self.generate_A4_percent_slider.GetValue() / 100.0
        if self.generate_A4_landscape_or_portrait == "Landscape":
            percentH = page.rect.width * sliderpercent
            percentW = page.rect.height * sliderpercent
        else:
            percentW = page.rect.width * sliderpercent
            percentH = page.rect.height * sliderpercent
        doc.delete_page(0)
        page = doc.new_page(width = percentW, height = percentH)
        shape = page.new_shape()
        shape.draw_rect(fitz.Rect(0,0,20,20))       
        shape.draw_rect(fitz.Rect(percentW-20,0,percentW,20))
        shape.draw_rect(fitz.Rect(0,percentH-20,20,percentH))
        shape.draw_rect(fitz.Rect(percentW-20,percentH-20,percentW,percentH))
        shape.finish(width=1, color=(0,0,0), fill=(0.9,0.9,0.9))
        shape.draw_rect(fitz.Rect(0,0,percentW,percentH))
        shape.finish(width=2, color=(0,0,0))
        shape.commit()
        doc = doc.convert_to_pdf()
        doc = fitz.open("pdf", doc)
        doc.save("canvasAuto.pdf")
        doc.close()

