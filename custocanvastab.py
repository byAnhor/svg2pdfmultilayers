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
import wx.svg
import fitz
import json
from ressourcespath import resource_path


class CustoCanvasTab(scrolled.ScrolledPanel):
    def __init__(self,parent,main_gui):
        super(CustoCanvasTab, self).__init__(parent)
        
        self.main_gui = main_gui
        self.preview_image = None
        self.temp_canvas_svg = self.main_gui.temp_path + '/canvasCUSTO.svg'
        self.temp_canvas_pdf = self.main_gui.temp_path + 'canvasCUSTO.pdf'

        globalsizer = wx.FlexGridSizer(2,10,10)
        globalsizer.SetSizeHints(self)

        right_sizer = self.construct_right_sizer()
        globalsizer.Add(right_sizer, proportion=0, flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT, border=10)
        left_sizer = self.construct_left_sizer()
        globalsizer.Add(left_sizer, proportion=0, flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT, border=10)

        self.auto_canvas_construction(event=None)
        self.on_generate_A4_landscape_or_portrait_toggle(event=None)
        
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

        newline = wx.BoxSizer(wx.HORIZONTAL)
        self.load_custo_btn = buts.GenBitmapTextButton(self, -1, bitmap=wx.Bitmap(resource_path("custoload.ico")), label= "Load customization")
        self.load_custo_btn.SetFont(self.load_custo_btn.GetFont().Bold())
        self.load_custo_btn.Bind(wx.EVT_BUTTON,self.on_load_custo_pressed)
        self.save_custo_btn = buts.GenBitmapTextButton(self, -1, bitmap=wx.Bitmap(resource_path("custosave.ico")), label= "Save customization")
        self.save_custo_btn.SetFont(self.save_custo_btn.GetFont().Bold())
        self.save_custo_btn.Bind(wx.EVT_BUTTON,self.on_save_custo_pressed)
        newline.Add(self.load_custo_btn, flag=wx.ALL|wx.EXPAND,border=5)
        newline.Add(self.save_custo_btn, flag=wx.ALL|wx.EXPAND,border=5)
        right_sizer.Add(newline, flag=wx.ALIGN_CENTER_HORIZONTAL)

        return right_sizer
        
    def construct_left_sizer(self):
        left_sizer = wx.FlexGridSizer(5,1,10,10)
      
        self.generate_A4 = dict()
        
        boxorientation = wx.StaticBox(self,label='Canvas', size=(180,100))
        boxorientationsizer = wx.StaticBoxSizer(boxorientation, wx.VERTICAL)
        self.generate_A4['landscape_or_portrait_toggle'] = wx.ToggleButton(self)
        self.generate_A4['landscape_or_portrait_toggle'].Bind(wx.EVT_TOGGLEBUTTON,self.on_generate_A4_landscape_or_portrait_toggle) 
        self.generate_A4['landscape_or_portrait_toggle'].SetValue(True)
        boxorientationsizer.Add(self.generate_A4['landscape_or_portrait_toggle'], flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, border=10)
        self.generate_A4['percent_slider'] = wx.Slider(self, value = 80, minValue = 70, maxValue = 100, size=(180,20), style = wx.SL_HORIZONTAL|wx.SL_VALUE_LABEL|wx.SL_TICKS|wx.SL_TOP)
        self.generate_A4['percent_slider'].SetTickFreq(5)
        self.generate_A4['percent_slider'].Bind(wx.EVT_COMMAND_SCROLL_THUMBRELEASE, self.auto_canvas_construction)
        self.generate_A4['percent_slider'].Bind(wx.EVT_SCROLL_THUMBRELEASE, self.auto_canvas_construction)
        self.generate_A4['percent_slider'].SetValue(80)
        boxorientationsizer.Add(self.generate_A4['percent_slider'], flag=wx.EXPAND|wx.ALL, border=10)
        boxorientationsizer.InsertSpacer(2,15)
        
        left_sizer.Add(boxorientationsizer, flag=wx.EXPAND)

        newline = wx.FlexGridSizer(3,3,10,10)
        self.corner_marks_symbol_mode = ['No', 'Square', 'Diamond', 'Round']   
        self.generate_A4['corner_mark_symbol'] = wx.RadioBox(self, label = 'Corner mark', choices = self.corner_marks_symbol_mode, majorDimension = 4, style = wx.RA_SPECIFY_ROWS)
        self.generate_A4['corner_mark_symbol'].Bind(wx.EVT_RADIOBOX,self.auto_canvas_construction) 
        boxcornermarkcolor = wx.StaticBox(self,label='Corner color')
        boxcornermarkcolorsizer = wx.StaticBoxSizer(boxcornermarkcolor, wx.VERTICAL)
        self.generate_A4['corner_mark_color'] = wx.ColourPickerCtrl(self)
        self.generate_A4['corner_mark_color'].SetColour('blue')
        self.generate_A4['corner_mark_color'].Bind(wx.EVT_COLOURPICKER_CHANGED,self.auto_canvas_construction) 
        boxcornermarkcolorsizer.Add(self.generate_A4['corner_mark_color'], flag=wx.ALL, border=10)        
        self.corner_marks_size_mode = ['Small', 'Medium', 'Large']   
        self.generate_A4['corner_mark_size'] = wx.RadioBox(self, label = 'Corner size', choices = self.corner_marks_size_mode, majorDimension = 4, style = wx.RA_SPECIFY_ROWS)
        self.generate_A4['corner_mark_size'].Bind(wx.EVT_RADIOBOX,self.auto_canvas_construction) 
        
        self.assembly_marks_symbol_mode = ['No', 'Square', 'Diamond', 'Round', 'Ticks']   
        self.generate_A4['assembly_mark_symbol'] = wx.RadioBox(self, label = 'Assembly mark', choices = self.assembly_marks_symbol_mode, majorDimension = 5, style = wx.RA_SPECIFY_ROWS)
        self.generate_A4['assembly_mark_symbol'].Bind(wx.EVT_RADIOBOX,self.auto_canvas_construction) 
        boxassemblymarkcolor = wx.StaticBox(self,label='Assembly color')
        boxassemblymarkcolorsizer = wx.StaticBoxSizer(boxassemblymarkcolor, wx.VERTICAL)
        self.generate_A4['assembly_mark_color'] = wx.ColourPickerCtrl(self)
        self.generate_A4['assembly_mark_color'].SetColour('blue')
        self.generate_A4['assembly_mark_color'].Bind(wx.EVT_COLOURPICKER_CHANGED,self.auto_canvas_construction) 
        boxassemblymarkcolorsizer.Add(self.generate_A4['assembly_mark_color'], flag=wx.ALL, border=10)        
        self.assembly_marks_size_mode = ['Small', 'Medium', 'Large']   
        self.generate_A4['assembly_mark_size'] = wx.RadioBox(self, label = 'Assembly size', choices = self.assembly_marks_size_mode, majorDimension = 4, style = wx.RA_SPECIFY_ROWS)
        self.generate_A4['assembly_mark_size'].Bind(wx.EVT_RADIOBOX,self.auto_canvas_construction) 

        self.maskingtape_txt_mode = ['No', 'LxCy', 'A-A']     
        self.generate_A4['maskingtap_mark_txt'] = wx.RadioBox(self, label = 'Masking tape text', choices = self.maskingtape_txt_mode, majorDimension = 3, style = wx.RA_SPECIFY_ROWS)
        self.generate_A4['maskingtap_mark_txt'].Bind(wx.EVT_RADIOBOX,self.auto_canvas_construction) 
        boxmaskingtapetxtcolor = wx.StaticBox(self,label='Text color')
        boxmaskingtapetxtcolorsizer = wx.StaticBoxSizer(boxmaskingtapetxtcolor, wx.VERTICAL)
        self.generate_A4['maskingtap_mark_color'] = wx.ColourPickerCtrl(self)
        self.generate_A4['maskingtap_mark_color'].SetColour('blue')
        self.generate_A4['maskingtap_mark_color'].Bind(wx.EVT_COLOURPICKER_CHANGED,self.auto_canvas_construction) 
        boxmaskingtapetxtcolorsizer.Add(self.generate_A4['maskingtap_mark_color'], flag=wx.ALL, border=10)        

        newline.AddMany([(self.generate_A4['corner_mark_symbol'], 1, wx.ALIGN_TOP|wx.EXPAND), 
                         (boxcornermarkcolorsizer, 1, wx.ALIGN_TOP|wx.EXPAND), 
                         (self.generate_A4['corner_mark_size'], 1, wx.ALIGN_TOP|wx.EXPAND), 
                         (self.generate_A4['assembly_mark_symbol'], 1, wx.ALIGN_TOP|wx.EXPAND), 
                         (boxassemblymarkcolorsizer, 1, wx.ALIGN_TOP|wx.EXPAND), 
                         (self.generate_A4['assembly_mark_size'], 1, wx.ALIGN_TOP|wx.EXPAND), 
                         (self.generate_A4['maskingtap_mark_txt'], 1, wx.ALIGN_TOP|wx.EXPAND), 
                         (boxmaskingtapetxtcolorsizer, 1, wx.ALIGN_TOP|wx.EXPAND)])
                         
        left_sizer.Add(newline, flag=wx.EXPAND)

        return left_sizer
    
    def on_generate_A4_landscape_or_portrait_toggle(self,event):  
        if self.generate_A4['landscape_or_portrait_toggle'].GetValue():
            self.generate_A4['landscape_or_portrait_toggle'].SetBitmap(wx.Bitmap(resource_path("landscape.png")))
        else:
            self.generate_A4['landscape_or_portrait_toggle'].SetBitmap(wx.Bitmap(resource_path("portrait.png")))
        self.auto_canvas_construction(event=None)

    def on_load_custo_pressed(self,event):
        with wx.FileDialog(self, 'Load customization', defaultDir=os.getcwd(),
                        wildcard='Custo files (*.custo)|*.custo',
                        style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL: return
            self.load_custo_pressed(fileDialog.GetPath())

    def load_custo_pressed(self,custofilename):
            with open(custofilename) as jsonfile:
                data = json.load(jsonfile)
                for k in data.keys():
                    print(k, data[k])
                    if data[k][0] == 'wx.ToggleButton':
                        cur = self.generate_A4[k].GetValue()
                        if data[k][1] != cur:
                            self.generate_A4[k].Unbind(wx.EVT_TOGGLEBUTTON)
                            self.generate_A4[k].SetValue(not cur)
                            self.generate_A4[k].Bind(wx.EVT_TOGGLEBUTTON, self.auto_canvas_construction)
                    elif data[k][0] == 'wx.Slider':
                        self.generate_A4[k].Unbind(wx.EVT_SLIDER)
                        self.generate_A4[k].SetValue(data[k][1])
                        self.generate_A4[k].Bind(wx.EVT_SLIDER, self.auto_canvas_construction)
                    elif data[k][0] == 'wx.CheckBox':
                        self.generate_A4[k].Unbind(wx.EVT_CHECKBOX)
                        self.generate_A4[k].SetValue(data[k][1])
                        self.generate_A4[k].Bind(wx.EVT_CHECKBOX, self.auto_canvas_construction)
                    elif data[k][0] == 'wx.RadioBox':
                        self.generate_A4[k].Unbind(wx.EVT_RADIOBUTTON)
                        self.generate_A4[k].SetSelection(data[k][1])
                        self.generate_A4[k].Bind(wx.EVT_RADIOBUTTON, self.auto_canvas_construction)
                    elif data[k][0] == 'wx.ColourPickerCtrl':
                        self.generate_A4[k].Unbind(wx.EVT_COLOURPICKER_CHANGED)
                        c = data[k][1].split('/')
                        c = wx.Colour(red=int(c[0]),green=int(c[1]),blue=int(c[2]),alpha=int(c[3]))
                        self.generate_A4[k].SetColour(c)                        
                        self.generate_A4[k].Bind(wx.EVT_COLOURPICKER_CHANGED, self.auto_canvas_construction)
                    else: print('Unknow instance')

                self.auto_canvas_construction(event=None)
                    
    def on_save_custo_pressed(self,event):
        with wx.FileDialog(self, 'Save customization as', defaultDir=os.getcwd(),
                        wildcard='Custo files (*.custo)|*.custo',
                        style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL: return
            
            custofilename = fileDialog.GetPath()
            
            data = {}
            for k in self.generate_A4.keys():
                if isinstance(self.generate_A4[k], wx.ToggleButton):       data[k] = ('wx.ToggleButton', self.generate_A4[k].GetValue())
                elif isinstance(self.generate_A4[k], wx.Slider):           data[k] = ('wx.Slider', self.generate_A4[k].GetValue())
                elif isinstance(self.generate_A4[k], wx.RadioBox):         data[k] = ('wx.RadioBox', self.generate_A4[k].GetSelection())
                elif isinstance(self.generate_A4[k], wx.CheckBox):         data[k] = ('wx.CheckBox', self.generate_A4[k].GetValue())
                elif isinstance(self.generate_A4[k], wx.ColourPickerCtrl): data[k] = ('wx.ColourPickerCtrl', '/'.join([str(rgb) for rgb in self.generate_A4[k].GetColour()]))
                else: print('Unknow instance')
                
            with open(custofilename, 'w') as outfile:
                json.dump(data, outfile, indent=4, sort_keys=False)
                  
    def on_paint(self,event):
        dc = wx.PaintDC(self.preview_image)
        ctx = wx.GraphicsContext.Create(dc)
        greycond = not self.preview_image.IsEnabled() or not os.path.isfile(self.temp_canvas_svg)
        dc.SetBackground(wx.Brush('grey' if greycond else 'white'))
        dc.Clear()
        svg = wx.svg.SVGimage.CreateFromFile(resource_path("nocanvas.svg") if greycond else self.temp_canvas_svg)
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
            
    def auto_canvas_construction(self,event):
        doc = fitz.open()  
        page = doc.new_page()
        sliderpercent = self.generate_A4['percent_slider'].GetValue() / 100.0
        if self.generate_A4['landscape_or_portrait_toggle'].GetValue():
            percentH = page.rect.width * sliderpercent
            percentW = page.rect.height * sliderpercent
        else:
            percentW = page.rect.width * sliderpercent
            percentH = page.rect.height * sliderpercent
        doc.delete_page(0)
        page = doc.new_page(width = percentW, height = percentH)
        shape = page.new_shape()
        
        if self.generate_A4['corner_mark_size'].GetStringSelection() == 'Small':
            cornersymbsize = 20
        elif self.generate_A4['corner_mark_size'].GetStringSelection() == 'Medium':
            cornersymbsize = 30
        elif self.generate_A4['corner_mark_size'].GetStringSelection() == 'Large':
            cornersymbsize = 40            

        if self.generate_A4['assembly_mark_size'].GetStringSelection() == 'Small':
            assemblysymbsize = 20
        elif self.generate_A4['assembly_mark_size'].GetStringSelection() == 'Medium':
            assemblysymbsize = 30
        elif self.generate_A4['assembly_mark_size'].GetStringSelection() == 'Large':
            assemblysymbsize = 40            

        cc = tuple(round(ti/255.0,2) for ti in self.generate_A4['corner_mark_color'].GetColour())
        ac = tuple(round(ti/255.0,2) for ti in self.generate_A4['assembly_mark_color'].GetColour())
                
        if self.generate_A4['corner_mark_symbol'].GetStringSelection() == 'Square':
            shape.draw_rect(fitz.Rect(0,0,cornersymbsize,cornersymbsize))       
            shape.draw_rect(fitz.Rect(percentW-cornersymbsize,0,percentW,cornersymbsize))
            shape.draw_rect(fitz.Rect(0,percentH-cornersymbsize,cornersymbsize,percentH))
            shape.draw_rect(fitz.Rect(percentW-cornersymbsize,percentH-cornersymbsize,percentW,percentH))
            shape.finish(width=1, color=(0,0,0), fill=cc[:-1], fill_opacity=0.5)
        elif self.generate_A4['corner_mark_symbol'].GetStringSelection() == 'Diamond':
            shape.draw_polyline([(0,0),(0,cornersymbsize),(cornersymbsize,0)])
            shape.draw_polyline([(percentW,0),(percentW,cornersymbsize),(percentW-cornersymbsize,0)])
            shape.draw_polyline([(0,percentH),(0,percentH-cornersymbsize),(cornersymbsize,percentH)])
            shape.draw_polyline([(percentW,percentH),(percentW,percentH-cornersymbsize),(percentW-cornersymbsize,percentH)])
            shape.finish(width=1, color=(0,0,0), fill=cc[:-1], fill_opacity=0.5)
        elif self.generate_A4['corner_mark_symbol'].GetStringSelection() == 'Round':
            shape.draw_sector((0,0), (0,cornersymbsize), 90, fullSector=True)   
            shape.draw_sector((percentW,0), (percentW-cornersymbsize,0), 90, fullSector=True)   
            shape.draw_sector((0, percentH), (cornersymbsize, percentH), 90, fullSector=True)   
            shape.draw_sector((percentW, percentH), (percentW-cornersymbsize, percentH), -90, fullSector=True)   
            shape.draw_line((0,0),(0,0))  
            shape.finish(width=1, color=(0,0,0), fill=cc[:-1], fill_opacity=0.5)

        if self.generate_A4['assembly_mark_symbol'].GetStringSelection() == 'Square':
            shape.draw_rect(fitz.Rect(0,percentH/2-assemblysymbsize/2,assemblysymbsize/2,percentH/2+assemblysymbsize/2))       
            shape.draw_rect(fitz.Rect(percentW-assemblysymbsize/2,percentH/2-assemblysymbsize/2,percentW,percentH/2+assemblysymbsize/2))       
            shape.draw_rect(fitz.Rect(percentW/2-assemblysymbsize/2, 0, percentW/2+assemblysymbsize/2, assemblysymbsize/2))      
            shape.draw_rect(fitz.Rect(percentW/2-assemblysymbsize/2, percentH-assemblysymbsize/2, percentW/2+assemblysymbsize/2, percentH))       
            shape.finish(width=1, color=(0,0,0), fill=ac[:-1], fill_opacity=0.5)
        elif self.generate_A4['assembly_mark_symbol'].GetStringSelection() == 'Diamond':
            shape.draw_polyline([(percentW/2-assemblysymbsize,0), (percentW/2,assemblysymbsize), (percentW/2+assemblysymbsize,0)])
            shape.draw_polyline([(percentW/2-assemblysymbsize,percentH), (percentW/2,percentH-assemblysymbsize), (percentW/2+assemblysymbsize,percentH)])
            shape.draw_polyline([(0, percentH/2-assemblysymbsize), (assemblysymbsize, percentH/2), (0, percentH/2+assemblysymbsize)])
            shape.draw_polyline([(percentW, percentH/2-assemblysymbsize), (percentW-assemblysymbsize, percentH/2), (percentW, percentH/2+assemblysymbsize)])
            shape.finish(width=1, color=(0,0,0), fill=ac[:-1], fill_opacity=0.5)     
        elif self.generate_A4['assembly_mark_symbol'].GetStringSelection() == 'Round':
            shape.draw_sector((percentW/2,0), (percentW/2-assemblysymbsize,0), 180, fullSector=True)   
            shape.draw_sector((percentW/2,percentH), (percentW/2+assemblysymbsize,percentH), 180, fullSector=True)   
            shape.draw_sector((0,percentH/2), (0,percentH/2+assemblysymbsize), 180, fullSector=True)   
            shape.draw_sector((percentW,percentH/2), (percentW,percentH/2-assemblysymbsize), 180, fullSector=True)   
            shape.draw_line((0,0),(0,0))  
            shape.finish(width=1, color=(0,0,0), fill=ac[:-1], fill_opacity=0.5)
        elif self.generate_A4['assembly_mark_symbol'].GetStringSelection() == 'Ticks':
            shape.draw_line((0, percentH/2), (assemblysymbsize, percentH/2))
            shape.draw_line((percentW, percentH/2), (percentW-assemblysymbsize, percentH/2))
            for i in range(1,3):
                shape.draw_line((i*percentW/3, 0), (i*percentW/3, assemblysymbsize))
                shape.draw_line((i*percentW/3, percentH), (i*percentW/3, percentH-assemblysymbsize))
            shape.finish(width=3, color=ac[:-1], fill=ac[:-1], fill_opacity=0.5)
            
        shape.draw_rect(fitz.Rect(0,0,percentW,percentH))
        shape.finish(width=2, color=(0,0,0), fill_opacity=0.5)
        shape.commit()
                  
        doc = doc.convert_to_pdf()
        doc = fitz.open("pdf", doc)
        doc.save(self.temp_canvas_pdf)
        ready = False
        while not ready:
            try:
                with open(self.temp_canvas_svg, "wb") as out:
                    out.write(page.get_svg_image().encode("UTF-8", "ignore"))  
                    ready = True
            except: pass
        doc.close()
        self.preview_image.Refresh()

