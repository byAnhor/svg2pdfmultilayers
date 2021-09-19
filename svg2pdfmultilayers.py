# -*- coding: utf-8 -*-
#! /usr/bin/env python3

# svg2pdfmultilayers is a utility to export multilayered SVG to PDF.
# Copyright (C) 2021 Anita Orhand
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import wx
import os
import sys
import shutil
import pikepdf
import fitz
from xml.dom import minidom
import utils
from layerfilter import LayerFilter
from iotab import IOTab

try:
    import pyi_splash
    pyi_splash.update_text('UI Loaded ...')
    pyi_splash.close()
except:
    pass
        
class byAnhorGUI(wx.Frame):
        
    def __init__(self, *args, **kw):
        # ensure the parent's __init__ is called
        super(byAnhorGUI, self).__init__(*args, **kw)
        self.ToggleWindowStyle(wx.STAY_ON_TOP | wx.CLOSE_BOX)

        self.all_svg_filename_per_layer = None
        self.all_input_filenames = None
        self.all_output_filenames = None
        self.unic_output_filename = None
        self.all_layer_filters = None
        self.all_full_pattern_rect = None
        
        # split the bottom half from the notebook top
        splitter = wx.SplitterWindow(self,style=wx.SP_LIVE_UPDATE)

        # create the notebook for the various tab panes
        nb = wx.Notebook(splitter)
        self.io = IOTab(nb,self)
        nb.AddPage(self.io,_('Options'))

        # create a panel for the go button and log window
        pnl = wx.Panel(splitter)
        vert_sizer = wx.BoxSizer(wx.VERTICAL)
        pnl.SetSizer(vert_sizer)

        # the go button and exit button
        go_btn = wx.Button(pnl, label=_('Generate PDF'))
        go_btn.SetFont(go_btn.GetFont().Bold())
        go_btn.Bind(wx.EVT_BUTTON,self.on_go_pressed)
        vert_sizer.Add(go_btn,flag=wx.ALL,border=5)
        bye_btn = wx.Button(pnl, label=_('Exit !'))
        bye_btn.SetFont(bye_btn.GetFont().Bold())
        bye_btn.Bind(wx.EVT_BUTTON,self.on_bye_pressed)
        vert_sizer.Add(bye_btn,flag=wx.ALL,border=5)

        # create a log window and redirect console output
        self.log = wx.TextCtrl(pnl, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.HSCROLL)
        vert_sizer.Add(self.log,proportion=1,flag=wx.EXPAND|wx.ALL,border=5)
        sys.stdout = self.log
        sys.stderr = self.log
        
        splitter.SplitHorizontally(nb,pnl)
        splitter.SetSashPosition(int(kw['size'][1]*3/4))
        splitter.SetMinimumPaneSize(10)

        self.working_dir = os.getcwd()

        if sys.platform == 'win32' or sys.platform == 'linux':
            self.SetIcon(wx.Icon(utils.resource_path('icon.ico')))

        self.doc_in = None
        self.out_doc_path = None
        
        if len(sys.argv) > 1:
            self.load_file(sys.argv[1])
        
        if len(sys.argv) > 2:
            self.out_doc_path = sys.argv[2]
            self.io.output_fname_display.SetLabel(sys.argv[2])
            self.io.on_generate_a0a4_checked(event=None)

        self.io.on_generate_assembly_mark_checked(event=None)
        self.io.on_generate_assembly_page_checked(event=None)
        self.io.on_generate_order_leftright_or_topdown_toggle(event=None)        
            
        
    def on_open(self, event):
        with wx.FileDialog(self, _('Select input SVG'), defaultDir=self.working_dir,
                        wildcard='SVG files (*.svg)|*.svg',
                        style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            # Proceed loading the file chosen by the user
            inputfilenamelist = fileDialog.GetPaths()
            self.load_file(inputfilenamelist)
            
    def load_file(self,inputfilenamelist):
        self.all_svg_filename_per_layer = []
        self.all_input_filenames = []
        self.all_layer_filters = []
        self.all_full_pattern_rect = []
        for f in inputfilenamelist: 
            try:
                # open the svg
                print(_('Open %s and parse its layers'%f))
                self.one_pdf_per_layer(f)
                self.all_layer_filters.append(LayerFilter(self.svg_filename_per_layer_dict, self.all_full_pattern_rect[-1]))
                self.all_svg_filename_per_layer.append(self.svg_filename_per_layer_dict)
                self.all_input_filenames.append(f)                
            except IOError:
                wx.LogError(_('Cannot load file') + pathname)
        
        self.io.load_new(self.all_input_filenames)    
        self.out_doc_path = None # clear the output if it's already set

    def on_output(self, event):
        with wx.FileDialog(self, _('Save output as'), defaultDir=self.working_dir,
                        wildcard='PDF files (*.pdf)|*.pdf',
                        style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            ouputfilename = fileDialog.GetPath()
            try:
                self.unic_output_filename = ouputfilename
                self.io.output_fname_display.SetLabel(ouputfilename)

            except IOError:
                wx.LogError(_('unable to write to') + pathname)
                
    def one_pdf_per_layer(self, svgInput):

        svgInputPath = os.path.dirname(svgInput)
        svgInputBase = os.path.basename(svgInput)
        svgInputFile = svgInputBase.replace('.svg','')
        self.temp_path = '%s/temp/'%svgInputPath
        if not os.path.exists(self.temp_path):
            os.makedirs(self.temp_path)
            
        tempsvg = fitz.open(svgInput)
        page = tempsvg.load_page(0)
        self.all_full_pattern_rect.append(page.rect)
           
        tempsvg = tempsvg.convert_to_pdf()
        tempsvg = fitz.open("pdf", tempsvg)
        tempsvg.save(self.temp_path + svgInputFile + '.fitz.pdf')
        
        doc = minidom.parse(svgInput)
        allL = [l for l in doc.getElementsByTagName('g') if l.getAttribute("inkscape:groupmode") == 'layer']
        self.svg_filename_per_layer_dict = dict()
   
        for l in reversed(allL):
            doc0 = minidom.parse(svgInput)
            allOL = [ol for ol in doc0.getElementsByTagName('g') if ol.getAttribute("inkscape:groupmode") == 'layer']
            for ol in allOL:
                if (l.getAttribute("id") != ol.getAttribute("id")):
                    parent = ol.parentNode
                    parent.removeChild(ol)
                    str_ = doc0.toxml()
                    displayStr = "_hidden" if "display:none" in l.getAttribute("style") else "_show"
                    layersvgfilename = self.temp_path + svgInputFile + displayStr + '_LAYER_%s.svg'%(l.getAttribute("inkscape:label"))
                    self.svg_filename_per_layer_dict[l.getAttribute("id")] = str(layersvgfilename)
                    with open(layersvgfilename, "wb") as out:
                        out.write(str_.encode("UTF-8", "ignore")) 

        for k in self.svg_filename_per_layer_dict.keys(): 
            curfilename = self.svg_filename_per_layer_dict[k]
            layerpdffilename = curfilename.replace('.svg', '.fitz.pdf')
            tempsvg = fitz.open(curfilename)
            tempsvg = tempsvg.convert_to_pdf()
            tempsvg = fitz.open("pdf", tempsvg)
            tempsvg.save(layerpdffilename)

            
    def on_go_pressed(self,event):
        if self.all_svg_filename_per_layer is None:
            print(_('Please select INPUT svg file before'))
            return 
        if self.unic_output_filename is None and len(self.all_svg_filename_per_layer) == 1:
            print(_('Please select OUTPUT pdf file before'))
            self.on_output(event)
            if self.unic_output_filename is None:
                return
        
        self.all_output_filenames = []
        if len(self.all_svg_filename_per_layer) == 1:
            self.all_output_filenames.append(self.unic_output_filename)
        else:
            for f in self.all_input_filenames:
                tmp = '%s/AutoGenPDF/'%os.path.dirname(f)
                if not os.path.exists(tmp):
                    os.makedirs(tmp)
                self.all_output_filenames.append('%s%s'%(tmp, os.path.basename(f).replace('.svg','.pdf')))
                self.merge_all_output_filename = '%smergedA4.pdf'%tmp
                   
        # do it
        try:
            
            mergedoc = fitz.open() if self.io.generate_merged_pdf.GetValue() else None

            for lfi,lf in enumerate(self.all_layer_filters):
                filtered = lf.run(self.all_output_filenames[lfi], 
                                  bool(self.io.generate_hidden_layers.GetValue()), 
                                  self.io.generate_a0_checked, 
                                  self.io.generate_a4_checked,                                  
                                  self.io.generate_A4_landscape_or_portrait, 
                                  self.io.generate_assembly_page_choice, 
                                  self.io.generate_order_leftright_or_topdown, 
                                  self.io.generate_assembly_mark_choice)
                
                if mergedoc is not None:
                    doc = fitz.open(self.all_output_filenames[lfi].replace('.pdf', '.A4.pdf'))
                    mergedoc.insertPDF(doc)
                    doc.close()
            
            if mergedoc is not None: mergedoc.save(self.merge_all_output_filename)
                
        except Exception as e:
            print(_('Something went wrong'))
            print(_('Exception') + ':')
            print(e)

    def on_bye_pressed(self,event):
        print(_('BYE !!!!!!!!!!!!!!!!!'))
        try:
            shutil.rmtree(self.temp_path)
        except Exception as e:
            print(_('Something went wrong'))
            print(_('Exception') + ':')
            print(e)
        self.Destroy()
        
           
if __name__ == '__main__':
    # When this module is run (not imported) then create the app, the
    # frame, show it, and start the event loop.

    language_warning = utils.setup_locale()

    app = wx.App()
    disp_h = wx.Display().GetGeometry().GetHeight()
    disp_w = wx.Display().GetGeometry().GetWidth()

    h = min(int(disp_h*0.85),600)
    w = min(int(disp_w*0.60),700)

    frm = byAnhorGUI(None, title='SVG -> PDF (multilayers)' + ' ' + utils.version_string, size=(w,h))

    if language_warning:
        print(language_warning)

    frm.Show()
    app.MainLoop()