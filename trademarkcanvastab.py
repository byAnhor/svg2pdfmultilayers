# -*- coding: utf-8 -*-
# svg2pdfmultilayers is a utility to export multilayered SVG to PDF.
# Copyright (C) 2021 Anita Orhand
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import sys
import os
import shutil
import wx
import wx.lib.scrolledpanel as scrolled
import wx.lib.buttons as buts
import wx.svg
import fitz
from ressourcespath import resource_path

class TrademarkCanvasTab(scrolled.ScrolledPanel):
    def __init__(self,parent,main_gui):
        super(TrademarkCanvasTab, self).__init__(parent)
        
        self.main_gui = main_gui
        self.preview_image = None
        self.trademark_svg_canvas_filename = None
        self.temp_canvas_svg = self.main_gui.temp_path + '/canvasTRADEMARK.svg'
        self.temp_canvas_pdf = self.main_gui.temp_path + 'canvasTRADEMARK.pdf'

        globalsizer = wx.FlexGridSizer(2,10,10)
        globalsizer.SetSizeHints(self)

        right_sizer = self.construct_right_sizer()
        globalsizer.Add(right_sizer, proportion=0, flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT, border=10)
        left_sizer = self.construct_left_sizer()
        globalsizer.Add(left_sizer, proportion=0, flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT, border=10)

        self.SetSizer(globalsizer)
        self.SetupScrolling()
        self.SetBackgroundColour(parent.GetBackgroundColour())

    def construct_right_sizer(self):
        right_sizer = wx.FlexGridSizer(3,1,10,10)

        self.canvaspreview = wx.StaticBox(self,label='Preview')
        canvaspreviewsizer = wx.StaticBoxSizer(self.canvaspreview, wx.VERTICAL)
        self.preview_image = wx.StaticBitmap(self, size=wx.Size(350,350))
        self.preview_image.Bind(wx.EVT_PAINT, self.on_paint)
        canvaspreviewsizer.Add(self.preview_image, flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, border=10)
        right_sizer.Add(canvaspreviewsizer)

        return right_sizer

    def construct_left_sizer(self):
        left_sizer = wx.FlexGridSizer(5,1,10,10)

        trademarkcanvas = wx.StaticBox(self,label='Trademark canvas', size=(180,100))
        trademarkcanvassizer = wx.StaticBoxSizer(trademarkcanvas, wx.VERTICAL)
        self.select_trademark_canvas_btn = buts.GenBitmapTextButton(self, -1, bitmap=wx.Bitmap(resource_path("openXS.ico")), label= "Select your own SVG canvas")
        self.select_trademark_canvas_btn.Bind(wx.EVT_BUTTON,self.on_select_trademark_canvas)
        trademarkcanvassizer.Add(self.select_trademark_canvas_btn, flag=wx.ALL, border=10)

        left_sizer.Add(trademarkcanvassizer, flag=wx.EXPAND)
        
        return left_sizer
        
    def on_select_trademark_canvas(self,event):
        with wx.FileDialog(self, 'Select input SVG', defaultDir=os.getcwd(),
                           wildcard='SVG files (*.svg)|*.svg',
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL: return
            self.trademark_svg_canvas_filename = fileDialog.GetPath()
            shutil.copyfile(self.trademark_svg_canvas_filename, self.temp_canvas_svg)  
            doc = fitz.open(self.temp_canvas_svg)
            doc = doc.convert_to_pdf()
            doc = fitz.open("pdf", doc)
            doc.save(self.temp_canvas_pdf)

        self.trademark_canvas_construction(event=None)

    def on_paint(self,event):
        dc = wx.PaintDC(self.preview_image)
        ctx = wx.GraphicsContext.Create(dc)
        greycond = not self.preview_image.IsEnabled() or self.trademark_svg_canvas_filename is None
        dc.SetBackground(wx.Brush('grey' if greycond else 'white'))
        dc.Clear()
        svg = wx.svg.SVGimage.CreateFromFile(resource_path("nocanvas.svg") if greycond else self.trademark_svg_canvas_filename)
        dcdim = min(self.preview_image.Size.width, self.preview_image.Size.height)
        imgdim = max(svg.width, svg.height)
        scale = dcdim / imgdim
        width = int(svg.width * scale)
        height = int(svg.height * scale)
        self.preview_image.Size.width = width
        self.preview_image.Size.height = height
        try:
            svg.RenderToGC(ctx, scale, wx.Size(width,height))
        except Exception as e:
            print('Something went wrong in on_paint')
            print('Exception:', e)

    def trademark_canvas_construction(self,event):
        if self.preview_image is None: return
        if self.trademark_svg_canvas_filename is None: return
        try:
            svg = wx.svg.SVGimage.CreateFromFile(self.trademark_svg_canvas_filename)
            bmp = svg.ConvertToScaledBitmap(wx.Size(200,200))
            self.preview_image.SetBitmap(wx.Bitmap(bmp))
            self.preview_image.Refresh()
        except: pass
        
