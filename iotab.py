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
from enum import Enum
from frozenclass import FrozenClass
from from1svgtonpdf import From1svgToNpdf
from pdfgenerator import CanvasOnSheet, PagesOrdering, PagesOrientation, TapeMarks, PagesNumbering
from custopdfgenerator import CustoPDFGenerator
from trademarkpdfgenerator import TrademarkPDFGenerator
import json
import fitz

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class InOutSelection(Enum):
     NONE = 0
     ONE_SVG = 1
     SEVERAL_SVG = 2

class IOTab(FrozenClass, scrolled.ScrolledPanel):
    def __init__(self,parent,main_gui):
        super(IOTab, self).__init__(parent)
        
        self.main_gui = main_gui
        self.algo_from_1svg_to_npdf = From1svgToNpdf(self.main_gui.temp_path)
        self.input_is_selected = InOutSelection.NONE
        self.output_is_selected = InOutSelection.NONE
        self.all_insvg_json = None
        
        globalsizer = wx.FlexGridSizer(6,1,10,10)

        newline = wx.BoxSizer(wx.HORIZONTAL)
        in_doc_btn = buts.GenBitmapTextButton(self, -1, bitmap=wx.Bitmap(resource_path("openXS.ico")), label= "Select input SVG with layers")
        in_doc_btn.Bind(wx.EVT_BUTTON,self.on_open_svg)
        newline.Add(in_doc_btn, flag=wx.ALIGN_CENTRE_VERTICAL)
        self.input_fname_display = wx.StaticText(self, label='None')
        newline.Add(self.input_fname_display, flag=wx.ALIGN_CENTRE_VERTICAL|wx.LEFT, border=5)
        globalsizer.Add(newline,flag=wx.TOP|wx.LEFT|wx.RIGHT,border=10)

        newline = wx.BoxSizer(wx.HORIZONTAL)
        self.out_doc_btn = buts.GenBitmapTextButton(self, -1, bitmap=wx.Bitmap(resource_path("savepdfXS.ico")), label= "Save output as PDF")
        self.out_doc_btn.Bind(wx.EVT_BUTTON,self.on_output_pdf)
        newline.Add(self.out_doc_btn, flag=wx.ALIGN_CENTRE_VERTICAL)
        self.output_fname_display = wx.StaticText(self, label='None')
        newline.Add(self.output_fname_display, flag=wx.ALIGN_CENTRE_VERTICAL|wx.LEFT, border=5)
        globalsizer.Add(newline,flag=wx.TOP|wx.LEFT|wx.RIGHT,border=10)

        newline = wx.BoxSizer(wx.HORIZONTAL)
        self.generate_hidden_layers = wx.CheckBox(self,label='Generate hidden layers')
        self.generate_hidden_layers.SetValue(0)
        newline.Add(self.generate_hidden_layers, flag=wx.ALL, border=10)
        globalsizer.Add(newline,flag=wx.TOP|wx.LEFT|wx.RIGHT,border=10)

        leftrightsizer = wx.FlexGridSizer(1,2,0,0)
        globalsizer.Add(leftrightsizer,flag=wx.TOP|wx.LEFT|wx.RIGHT,border=10)

        leftsizer = wx.BoxSizer(wx.VERTICAL)
        rightsizer = wx.BoxSizer(wx.VERTICAL)
        leftrightsizer.AddMany([(leftsizer, wx.ALIGN_TOP|wx.EXPAND),(rightsizer, wx.ALIGN_TOP|wx.EXPAND)])
        
        self.boxA0 = wx.StaticBox(self,label='Full size PDF generation')
        boxA0sizer = wx.StaticBoxSizer(self.boxA0, wx.VERTICAL)
        self.generate_a0 = wx.CheckBox(self,label='Generate full size PDF')
        self.generate_a0.SetValue(1)
        self.generate_a0.Bind(wx.EVT_CHECKBOX,self.on_generate_a0a4_checked)
        boxA0sizer.Add(self.generate_a0, flag=wx.ALL, border=10)
        leftsizer.Add(boxA0sizer, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=10)

        self.boxA4 = wx.StaticBox(self,label='A4 PDF generation')
        boxA4sizer = wx.StaticBoxSizer(self.boxA4, wx.VERTICAL)
        self.generate_a4 = wx.CheckBox(self,label='Generate A4')
        self.generate_a4.SetValue(1)
        self.generate_a4.Bind(wx.EVT_CHECKBOX,self.on_generate_a0a4_checked)
        boxA4sizer.Add(self.generate_a4, flag=wx.ALL, border=10)
        
        newline = wx.BoxSizer(wx.HORIZONTAL)
        self.generate_merged_pdf = wx.CheckBox(self,label='Generate merged PDF')
        self.generate_merged_pdf.SetValue(0)
        newline.Add(self.generate_merged_pdf, flag=wx.ALIGN_TOP)
        boxA4sizer.Add(newline, flag=wx.ALL, border=10)

        newline = wx.BoxSizer(wx.HORIZONTAL)
        boxsheettrimming = wx.StaticBox(self,label='Sheet trimming before assembling/taping')
        boxsheettrimmingsizer = wx.StaticBoxSizer(boxsheettrimming, wx.HORIZONTAL)
        self.generate_sheet_trimming_toggle = wx.ToggleButton(self)
        self.generate_sheet_trimming_toggle.Bind(wx.EVT_TOGGLEBUTTON,self.on_generate_sheet_trimming_toggle) 
        self.generate_sheet_trimming_toggle.SetValue(True)
        boxsheettrimmingsizer.Add(self.generate_sheet_trimming_toggle, flag=wx.ALL, border=10)
        self.sheet_trimming_infobulle = wx.StaticText(self, label='None')
        boxsheettrimmingsizer.Add(self.sheet_trimming_infobulle, flag=wx.LEFT|wx.RIGHT|wx.ALIGN_CENTRE_VERTICAL, border=5)
        newline.Add(boxsheettrimmingsizer, flag=wx.ALIGN_TOP)

        boxscanningorder = wx.StaticBox(self,label='Generation order')
        boxscanningordersizer = wx.StaticBoxSizer(boxscanningorder, wx.HORIZONTAL)
        self.generate_scanning_order_toggle = wx.ToggleButton(self)
        self.generate_scanning_order_toggle.Bind(wx.EVT_TOGGLEBUTTON,self.on_generate_scanning_order_toggle) 
        self.generate_scanning_order_toggle.SetValue(True)
        boxscanningordersizer.Add(self.generate_scanning_order_toggle, flag=wx.ALL, border=10)
        self.scanning_order_infobulle = wx.StaticText(self, label='None')
        boxscanningordersizer.Add(self.scanning_order_infobulle, flag=wx.LEFT|wx.RIGHT|wx.ALIGN_CENTRE_VERTICAL, border=5)
        newline.Add(boxscanningordersizer, flag=wx.ALIGN_TOP)
        boxA4sizer.Add(newline, flag=wx.ALL, border=10)
        
        newline = wx.BoxSizer(wx.HORIZONTAL)
        boxusepersonalcanvas = wx.StaticBox(self,label='Personal canvas', size=(180,100))
        boxusepersonalcanvassizer = wx.StaticBoxSizer(boxusepersonalcanvas, wx.VERTICAL)
        self.use_trademark_canvas = wx.CheckBox(self,label='Use your trademark canvas')
        self.use_trademark_canvas.SetValue(0)
        self.use_trademark_canvas.Bind(wx.EVT_CHECKBOX,self.on_use_trademark_canvas_checked)
        boxusepersonalcanvassizer.Add(self.use_trademark_canvas, flag=wx.ALL, border=10)
        newline.Add(boxusepersonalcanvassizer, flag=wx.ALIGN_TOP)
        boxA4sizer.Add(newline, flag=wx.ALL, border=10)

        newline = wx.FlexGridSizer(4,10,10)
        self.pagenumber_txt_mode = ['No', 'LxCy', 'Page number']     
        self.pagenumber_txt = wx.RadioBox(self, label = 'Pager number text', choices = self.pagenumber_txt_mode, majorDimension = 3, style = wx.RA_SPECIFY_ROWS)
        newline.Add(self.pagenumber_txt, flag=wx.ALIGN_TOP)
        boxpagenumbertxtcolor = wx.StaticBox(self,label='Text color')
        boxpagenumbertxtcolorsizer = wx.StaticBoxSizer(boxpagenumbertxtcolor, wx.VERTICAL)
        self.pagenumber_color = wx.ColourPickerCtrl(self)
        self.pagenumber_color.SetColour('grey')
        boxpagenumbertxtcolorsizer.Add(self.pagenumber_color, flag=wx.ALL, border=10)        
        newline.Add(boxpagenumbertxtcolorsizer, flag=wx.ALIGN_TOP|wx.EXPAND)
        boxpagenumbertxtsize = wx.StaticBox(self,label='Text size')
        boxpagenumbertxtsizesizer = wx.StaticBoxSizer(boxpagenumbertxtsize, wx.HORIZONTAL)
        self.pagenumber_size = wx.TextCtrl(self, -1, "150", size=(30,20))
        self.pagenumber_size.Bind(wx.EVT_TEXT, self.on_change_page_number_size) 
        pagenumber_h = self.pagenumber_size.GetSize().height
        pagenumber_w = self.pagenumber_size.GetSize().width + self.pagenumber_size.GetPosition().x + 2
        self.pagenumber_size_spinButton = wx.SpinButton(self, -1, (pagenumber_w, 50),
                                          (pagenumber_h * 2 / 3, pagenumber_h),
                                          wx.SP_VERTICAL)
        self.pagenumber_size_spinButton.SetRange(20,400)
        self.pagenumber_size_spinButton.SetValue(150)
        self.pagenumber_size_spinButton.Bind(wx.EVT_SPIN, self.on_spin_page_number_size)
        boxpagenumbertxtsizesizer.Add(self.pagenumber_size, flag=wx.ALIGN_TOP)
        boxpagenumbertxtsizesizer.Add(self.pagenumber_size_spinButton, flag=wx.ALIGN_TOP)
        newline.Add(boxpagenumbertxtsizesizer, flag=wx.ALIGN_TOP|wx.EXPAND)
        boxpagenumbertxtopacity = wx.StaticBox(self,label='Text opacity')
        boxpagenumbertxtopacitysizer = wx.StaticBoxSizer(boxpagenumbertxtopacity, wx.HORIZONTAL)
        self.pagenumber_opacity = wx.TextCtrl(self, -1, "20", size=(30,20))
        self.pagenumber_opacity.Bind(wx.EVT_TEXT, self.on_change_page_number_opacity) 
        pagenumber_h = self.pagenumber_opacity.GetSize().height
        pagenumber_w = self.pagenumber_opacity.GetSize().width + self.pagenumber_opacity.GetPosition().x + 2
        self.pagenumber_opacity_spinButton = wx.SpinButton(self, -1, (pagenumber_w, 50),
                                                          (pagenumber_h * 2 / 3, pagenumber_h),
                                                           wx.SP_VERTICAL)
        self.pagenumber_opacity_spinButton.SetRange(1,100)
        self.pagenumber_opacity_spinButton.SetValue(20)
        self.pagenumber_opacity_spinButton.Bind(wx.EVT_SPIN, self.on_spin_page_number_opacity)
        boxpagenumbertxtopacitysizer.Add(self.pagenumber_opacity, flag=wx.ALIGN_TOP)
        boxpagenumbertxtopacitysizer.Add(self.pagenumber_opacity_spinButton, flag=wx.ALIGN_TOP)
        newline.Add(boxpagenumbertxtopacitysizer, flag=wx.ALIGN_TOP|wx.EXPAND)
        boxA4sizer.Add(newline, flag=wx.ALL, border=10)
 
        leftsizer.Add(boxA4sizer, flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT, border=10)

        boxwatermark = wx.StaticBox(self,label='Watermarking top/down/left/right')
        boxwatermarksizer = wx.StaticBoxSizer(boxwatermark, wx.VERTICAL)
        newline = wx.FlexGridSizer(4,4,10,10)
        self.generate_watermarking = dict()
        for ii,i in enumerate(['top','down','left','right']):
            self.generate_watermarking['watermark_%s'%i] = wx.CheckBox(self,label='Add watermark at %s'%i)
            self.generate_watermarking['watermark_%s'%i].Bind(wx.EVT_CHECKBOX, self.on_generate_watermark_enabled)
            self.generate_watermarking['watermark_%s'%i].SetValue(0)
            self.generate_watermarking['watermark_%s_basename'%i] = wx.StaticText(self,label=self.main_gui.macadress)
            self.generate_watermarking['watermark_%s_basename'%i].Enable(False)
            self.generate_watermarking['watermark_%s_fullpath'%i] = wx.StaticText(self,label='')
            self.generate_watermarking['watermark_%s_fullpath'%i].Show(False)
            self.generate_watermarking['watermark_%s_button'%i] = buts.GenBitmapTextButton(self, bitmap=wx.Bitmap(resource_path("openXS.ico")), size=(15,15), label= "")
            self.generate_watermarking['watermark_%s_button'%i].Bind(wx.EVT_BUTTON,self.on_generate_watermark_filename)
            self.generate_watermarking['watermark_%s_button'%i].Enable(False)
            
        newline.AddMany([(self.generate_watermarking['watermark_top']),
                         (self.generate_watermarking['watermark_top_button']), 
                         (self.generate_watermarking['watermark_top_basename']), 
                         (self.generate_watermarking['watermark_top_fullpath']), 
                         (self.generate_watermarking['watermark_down']),
                         (self.generate_watermarking['watermark_down_button']), 
                         (self.generate_watermarking['watermark_down_basename']),
                         (self.generate_watermarking['watermark_down_fullpath']),
                         (self.generate_watermarking['watermark_left']),
                         (self.generate_watermarking['watermark_left_button']), 
                         (self.generate_watermarking['watermark_left_basename']),
                         (self.generate_watermarking['watermark_left_fullpath']),
                         (self.generate_watermarking['watermark_right']),
                         (self.generate_watermarking['watermark_right_button']), 
                         (self.generate_watermarking['watermark_right_basename']), 
                         (self.generate_watermarking['watermark_right_fullpath'])])
        boxwatermarksizer.Add(newline, flag=wx.ALL|wx.EXPAND, border=10)

        rightsizer.Add(boxwatermarksizer, flag=wx.EXPAND)

        self.on_generate_a0a4_checked(event=None)
        self.on_generate_scanning_order_toggle(event=None)  
        self.on_generate_sheet_trimming_toggle(event=None)  
        self.on_use_trademark_canvas_checked(event=None)

        self.SetSizer(globalsizer)
        self.SetupScrolling()
        self.SetBackgroundColour(parent.GetBackgroundColour())
        
        self.current_pagenumber_size = None
        self.current_pagenumber_opacity = None
                
        self._freeze()
                     
    def load_new_canvas(self,filename):
        self.input_canevas_fname_display.SetLabel(filename)
        
    def on_generate_a0a4_checked(self,event):
        self.generate_a0_checked = bool(self.generate_a0.GetValue())
        self.generate_a4_checked = bool(self.generate_a4.GetValue())
        self.generate_scanning_order_toggle.Enable(self.generate_a4_checked)
        self.use_trademark_canvas.Enable(self.generate_a4_checked)
        self.pagenumber_txt.Enable(self.generate_a4_checked)
        self.pagenumber_color.Enable(self.generate_a4_checked)
        self.pagenumber_size.Enable(self.generate_a4_checked)
        self.pagenumber_opacity.Enable(self.generate_a4_checked)
        if self.main_gui.gui_custo is not None: 
            self.main_gui.gui_custo.Enable(self.generate_a4_checked)
        self.generate_sheet_trimming_toggle.Enable(self.generate_a4_checked)
        self.generate_merged_pdf.Enable(self.generate_a4_checked)
        if self.generate_a0_checked and self.output_fname_display.Label != 'None':
            self.boxA0.SetLabel("Full size PDF generation : %s"%self.output_fname_display.Label.replace('.pdf', '.A0.pdf'))
        else:
            self.boxA0.SetLabel("Full size PDF generation")
        if self.generate_a4_checked and self.output_fname_display.Label != 'None':
            self.boxA4.SetLabel("A4 PDF generation : %s"%self.output_fname_display.Label.replace('.pdf', '.A4.pdf'))
        else:
            self.boxA4.SetLabel("A4 PDF generation")
            
    def on_generate_watermark_enabled(self, event):
        for ii,i in enumerate(['top','down','left','right']):
            if event.GetId() == self.generate_watermarking['watermark_%s'%i].GetId():
                self.generate_watermarking['watermark_%s_button'%i].Enable(event.IsChecked())        
                self.generate_watermarking['watermark_%s_basename'%i].Enable(event.IsChecked()) 
                if event.IsChecked() is False:
                    self.generate_watermarking['watermark_%s_basename'%i].SetLabel(self.main_gui.macadress)
                    self.generate_watermarking['watermark_%s_fullpath'%i].SetLabel('')
            
    def on_generate_watermark_filename(self, event):
        with wx.FileDialog(self, 'Select input SVG', defaultDir=self.main_gui.working_dir,
                           wildcard='SVG files (*.svg)|*.svg',
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL: return
            allrotatetdlr = [180,0,90,-90]
            for ii,i in enumerate(['top','down','left','right']):
                if event.GetId() == self.generate_watermarking['watermark_%s_button'%i].GetId():
                    self.generate_watermarking['watermark_%s_basename'%i].SetLabel(os.path.basename(fileDialog.GetPath())) 
                    self.generate_watermarking['watermark_%s_fullpath'%i].SetLabel("watermark_rot_%s.pdf"%i)
                    docw = fitz.open(fileDialog.GetPath())
                    docw = docw.convertToPDF()
                    docw = fitz.open("pdf", docw)
                    docw.save(self.main_gui.temp_path + "watermark_rot_%s.pdf"%i) 
                    pagew = docw.load_page(0)
                    pagew.setRotation(allrotatetdlr[ii])
                    docw.save(self.main_gui.temp_path + "watermark_rot_%s.pdf"%i) 

    def on_generate_scanning_order_toggle(self,event):
        if self.generate_scanning_order_toggle.GetValue():
            self.generate_scanning_order_toggle.SetBitmap(wx.Bitmap(resource_path("leftright.png")))
            self.scanning_order_infobulle.SetLabel('Horizontally first')  
        else:
            self.generate_scanning_order_toggle.SetBitmap(wx.Bitmap(resource_path("topdown.png")))
            self.scanning_order_infobulle.SetLabel('Vertically first')  

    def on_generate_sheet_trimming_toggle(self,event):
        if self.generate_sheet_trimming_toggle.GetValue():
            self.generate_sheet_trimming_toggle.SetBitmap(wx.Bitmap(resource_path("center.png")))
            self.sheet_trimming_infobulle.SetLabel('Need to cut 2 sides\nbefore assembling')
        else:
            self.generate_sheet_trimming_toggle.SetBitmap(wx.Bitmap(resource_path("topleft.png")))
            self.sheet_trimming_infobulle.SetLabel('Only superimpose\nsheets')

    def on_use_trademark_canvas_checked(self,event):
        self.main_gui.manage_access_to_custo_or_trademark_canvas(self.use_trademark_canvas.GetValue())
        
    def on_spin_page_number_size(self, event):
        self.current_pagenumber_size = str(event.GetPosition())
        self.pagenumber_size.SetValue(self.current_pagenumber_size)

    def on_change_page_number_size(self, event):
        self.current_pagenumber_size = str(event.GetString())
        self.pagenumber_size_spinButton.SetValue(int(self.current_pagenumber_size))

    def on_spin_page_number_opacity(self, event):
        self.current_pagenumber_opacity = str(event.GetPosition())
        self.pagenumber_opacity.SetValue(self.current_pagenumber_opacity)

    def on_change_page_number_opacity(self, event):
        self.current_pagenumber_opacity = str(event.GetString())
        self.pagenumber_opacity_spinButton.SetValue(int(self.current_pagenumber_opacity))

    def on_open_svg(self, event):
        with wx.FileDialog(self, 'Select input SVG', defaultDir=self.main_gui.working_dir,
                           wildcard='SVG files (*.svg)|*.svg',
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL: return
            self.load_svg_file(fileDialog.GetPaths())
            
    def get_landscape_or_portrait(self):
        landscape_or_portrait = self.main_gui.gui_custo.generate_A4['landscape_or_portrait_toggle'].GetValue()
        if self.use_trademark_canvas.GetValue() and self.main_gui.gui_trademark.trademark_svg_canvas_filename is not None:
            svg = wx.svg.SVGimage.CreateFromFile(self.main_gui.gui_trademark.temp_canvas_svg)
            landscape_or_portrait = svg.height < svg.width           
            print('Your own canvas seams to be %s'%('LANDSCAPE' if landscape_or_portrait else 'PORTRAIT'))
        return landscape_or_portrait

    def run_layer_filter(self, jsonfilename, index):
        
        pdfgen = TrademarkPDFGenerator(self.main_gui) if self.use_trademark_canvas.GetValue() else CustoPDFGenerator(self.main_gui)
        pdfgen.generateA0 = self.generate_a0_checked
        pdfgen.generateA4 = self.generate_a4_checked
        pdfgen.generateHiddenLayers = self.generate_hidden_layers.GetValue()
        pdfgen.generateSheetTrimming = CanvasOnSheet.CENTERED if self.generate_sheet_trimming_toggle.GetValue() else CanvasOnSheet.PIRATES
        pdfgen.generateScanningOrder = PagesOrdering.LEFTRIGHT if self.generate_scanning_order_toggle.GetValue() else PagesOrdering.TOPDOWN
        pdfgen.generatePagesOrientation = PagesOrientation.LANDSCAPE if self.get_landscape_or_portrait() else PagesOrientation.PORTRAIT
        pdfgen.generateMaskingTapeTxt = TapeMarks.fromStr(self.main_gui.gui_custo.generate_A4['maskingtap_mark_txt'].GetStringSelection())
        pdfgen.generateMaskingTapeColor = list(self.main_gui.gui_custo.generate_A4['maskingtap_mark_color'].GetColour())
        pdfgen.pageNumberTxt = PagesNumbering.fromStr(self.pagenumber_txt.GetStringSelection())
        print(pdfgen.pageNumberTxt, self.pagenumber_txt.GetStringSelection())
        pdfgen.pageNumberColor = list(self.pagenumber_color.GetColour())
        pdfgen.pageNumberSize = self.pagenumber_size.GetValue()
        pdfgen.pageNumberOpacity = self.pagenumber_opacity.GetValue()
        pdfgen.watermark = self.generate_watermarking
        print(pdfgen.watermark)
      
        #pdfgen.pdfOutFilename = self.output_fname_display

        with open(jsonfilename) as jsonfile:
            patterndata = json.load(jsonfile)
            pdfgen.tempPath = patterndata['temp_path']
            pdfgen.fullPatternSvg = patterndata['full_pattern_svg']
            pdfgen.fullPatternRect = fitz.Rect(0,0,patterndata['full_pattern_width'],patterndata['full_pattern_height'])
            pdfgen.fullPatternSvgPerLayer = patterndata['layers_filenames']

        with open(self.main_gui.temp_path + 'output.json') as jsonfile:
            outdata = json.load(jsonfile)
            pdfgen.generateMergeFilename = None if not self.generate_merged_pdf.GetValue() else outdata['output_merge_pdf_filename']
            if index == 0 and pdfgen.generateMergeFilename is not None and os.path.isfile(pdfgen.generateMergeFilename):
                os.remove(pdfgen.generateMergeFilename)
            if outdata['out_%s'%pdfgen.fullPatternSvg] == 'User choice':
                pdfgen.pdfOutFilename = outdata['output_unic_pdf_filename']
            else:
                pdfgen.pdfOutFilename = outdata['out_%s'%pdfgen.fullPatternSvg]

        #for l in pdfgen.fullPatternSvgPerLayer.keys():
        pdfgen.run()
        
            
    def load_svg_file(self,inputfilenamelist):
        self.all_insvg_json = list()
        for f in inputfilenamelist: 
            try:
                # open the svg
                print('Open and parse layers of %s'%f)
                self.algo_from_1svg_to_npdf.set_SVG_in(f)
                self.all_insvg_json.append(self.algo_from_1svg_to_npdf.run())
            except IOError:
                wx.LogError('Cannot load file' + f)
                
        self.output_is_selected = InOutSelection.NONE
        
        autogenpath = '%s/AutoGenPDF/'%os.path.dirname(inputfilenamelist[0])
        if not os.path.exists(autogenpath): os.makedirs(autogenpath)

        jsondata = dict()
        jsondata['output_merge_pdf_filename'] = '%smerged.pdf'%autogenpath
        
        self.input_fname_display.SetLabel(' '.join(inputfilenamelist))
        if len(inputfilenamelist) == 1:
            self.output_fname_display.SetLabel(label='Select the output PDF filename')
            self.out_doc_btn.Enable(True)
            self.input_is_selected = InOutSelection.ONE_SVG
            jsondata['out_%s'%inputfilenamelist[0]] = 'User choice'
        else:
            self.output_fname_display.SetLabel(label='PDF filename automatically build (see AutoGenPDF directory)')
            self.out_doc_btn.Enable(False)
            self.input_is_selected = InOutSelection.SEVERAL_SVG                           
            for f in inputfilenamelist:
                jsondata['out_%s'%f] = '%s%s'%(autogenpath, os.path.basename(f).replace('.svg','.pdf'))

        with open(self.main_gui.temp_path + 'output.json', 'w') as outfile:
            json.dump(jsondata, outfile, indent=4, sort_keys=True)        

    def on_output_pdf(self, event):
        with wx.FileDialog(self, 'Save output as', defaultDir=self.main_gui.working_dir,
                           wildcard='PDF files (*.pdf)|*.pdf',
                           style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL: return
            self.load_output_pdf_file(fileDialog.GetPath())
                            
    def load_output_pdf_file(self,outputfilename):
        self.output_fname_display.SetLabel(outputfilename)
        self.output_is_selected = InOutSelection.ONE_SVG
        with open(self.main_gui.temp_path + 'output.json') as jsonfile:
            jsondata = json.load(jsonfile)

        jsondata['output_unic_pdf_filename'] = outputfilename
        with open(self.main_gui.temp_path + 'output.json', 'w') as outfile:
            json.dump(jsondata, outfile, indent=4, sort_keys=True)    
            


