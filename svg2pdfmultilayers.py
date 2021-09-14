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

        if len(sys.argv) > 3:
            self.load_canvas_file(sys.argv[3])

        self.io.on_generate_hidden_layers_checked(event=None)
        self.io.on_generate_assembly_mark_checked(event=None)
        self.io.on_generate_assembly_page_checked(event=None)
        self.io.on_generate_order_leftright_or_leftright_toggle(event=None)        
            
        
    def on_open(self, event):
        with wx.FileDialog(self, _('Select input SVG'), defaultDir=self.working_dir,
                        wildcard='SVG files (*.svg)|*.svg',
                        style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            # Proceed loading the file chosen by the user
            pathname = fileDialog.GetPath()
            self.load_file(pathname)
            
    def on_open_canvas(self, event):
        with wx.FileDialog(self, _('Select input A4 SVG canvas'), defaultDir=self.working_dir,
                        wildcard='SVG files (*.svg)|*.svg',
                        style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            # Proceed loading the file chosen by the user
            pathname = fileDialog.GetPath()
            self.load_canvas_file(pathname)

    def load_canvas_file(self,pathname):
            self.canvas = pathname
            self.io.load_new_canvas(self.canvas)
            self.layer_filter.set_canvas(self.canvas)

    def load_file(self,pathname):
        try:
            # open the svg
            print(_('Opening') + ' ' + pathname)
            self.one_pdf_per_layer(pathname)
            
            self.in_doc = self.onelayersvg
            self.io.load_new(pathname)

            # create the processing objects
            self.layer_filter = LayerFilter(self.in_doc, self.rect)
            '''self.lt.load_new(self.layer_filter.get_layer_names(self.layer_filter.pdf))

            self.tiler = PageTiler()'''
            
            # clear the output if it's already set
            self.out_doc_path = None

        except IOError:
            wx.LogError(_('Cannot open file') + pathname)
            
    def on_output(self, event):
        with wx.FileDialog(self, _('Save output as'), defaultDir=self.working_dir,
                        wildcard='PDF files (*.pdf)|*.pdf',
                        style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            pathname = fileDialog.GetPath()
            try:
                self.out_doc_path = pathname
                self.io.output_fname_display.SetLabel(pathname)

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
        self.rect = page.rect
           
        tempsvg = tempsvg.convert_to_pdf()
        tempsvg = fitz.open("pdf", tempsvg)
        tempsvg.save(self.temp_path + svgInputFile + '.fitz.pdf')
        
        doc = minidom.parse(svgInput)
        allL = [l for l in doc.getElementsByTagName('g') if l.getAttribute("inkscape:groupmode") == 'layer']
        self.onelayersvg = dict()
   
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
                    self.onelayersvg[l.getAttribute("id")] = str(layersvgfilename)
                    with open(layersvgfilename, "wb") as out:
                        out.write(str_.encode("UTF-8", "ignore")) 

        for k in self.onelayersvg.keys(): 
            curfilename = self.onelayersvg[k]
            layerpdffilename = curfilename.replace('.svg', '.fitz.pdf')
            tempsvg = fitz.open(curfilename)
            tempsvg = tempsvg.convert_to_pdf()
            tempsvg = fitz.open("pdf", tempsvg)
            tempsvg.save(layerpdffilename)

            
    def on_go_pressed(self,event):
        if self.in_doc is None:
            print(_('Please select INPUT svg file before'))
            return 
        if self.in_doc is None:
            print(_('Please select OUTPUT pdf file before'))
            return 
        
        # retrieve the selected options
        if self.out_doc_path is None:
            self.on_output(event)
            if self.out_doc_path is None:
                return

        # do it
        try:
            filtered = self.layer_filter.run(self.out_doc_path, self.io.generate_hidden_layers_checked, self.io.generate_a0_checked, self.io.generate_a4_checked, self.io.generate_assembly_page_choice, self.io.generate_order_leftright_or_leftright, self.io.generate_assembly_mark_choice)
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