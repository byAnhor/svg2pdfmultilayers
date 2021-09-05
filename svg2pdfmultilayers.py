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
import pikepdf
import fitz
from xml.dom import minidom
from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg
import utils
from layerfilter import LayerFilter
from iotab import IOTab

class byAnhorGUI(wx.Frame):
    def __init__(self, *args, **kw):
        # ensure the parent's __init__ is called
        super(byAnhorGUI, self).__init__(*args, **kw)

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

        # the go button
        go_btn = wx.Button(pnl, label=_('Generate PDF'))
        go_btn.SetFont(go_btn.GetFont().Bold())
        go_btn.Bind(wx.EVT_BUTTON,self.on_go_pressed)
        vert_sizer.Add(go_btn,flag=wx.ALL,border=5)

        # create a log window and redirect console output
        self.log = wx.TextCtrl(pnl, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.HSCROLL)
        vert_sizer.Add(self.log,proportion=1,flag=wx.EXPAND|wx.ALL,border=5)
        sys.stdout = self.log
        sys.stderr = self.log
        
        splitter.SplitHorizontally(nb,pnl)
        splitter.SetSashPosition(int(kw['size'][1]*1/4))
        splitter.SetMinimumPaneSize(10)

        self.working_dir = os.getcwd()

        if len(sys.argv) > 1:
            self.load_file(sys.argv[1])
        
        if len(sys.argv) > 2:
            self.out_doc_path = sys.argv[2]
            self.io.output_fname_display.SetLabel(sys.argv[2])
        
    def on_open(self, event):
        with wx.FileDialog(self, _('Select input SVG'), defaultDir=self.working_dir,
                        wildcard='SVG files (*.svg)|*.svg',
                        style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            # Proceed loading the file chosen by the user
            pathname = fileDialog.GetPath()
            self.load_file(pathname)

    def load_file(self,pathname):
        self.working_dir = os.path.dirname(pathname)
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
        
        tempsvg = fitz.open(svgInput)
        page = tempsvg.load_page(0)
        self.rect = page.rect
        #tempsvg = tempsvg.convert_to_pdf()
        #tempsvg = fitz.open("pdf", tempsvg)
        #tempsvg.save(svgInput.replace('.svg', '.fitz.pdf'))
        
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
                    layersvgfilename = svgInput.replace('.svg', 'LAYER_%s.svg'%(l.getAttribute("id")))
                    self.onelayersvg[l.getAttribute("id")] = str(layersvgfilename)
                    with open(layersvgfilename, "w") as out:
                        out.write(str_) 

        for k in self.onelayersvg.keys(): 
            curfilename = self.onelayersvg[k]
            layerpdffilename = curfilename.replace('.svg', '.fitz.pdf')
            tempsvg = fitz.open(curfilename)
            tempsvg = tempsvg.convert_to_pdf()
            tempsvg = fitz.open("pdf", tempsvg)
            tempsvg.save(layerpdffilename)

            
    def on_go_pressed(self,event):
        # retrieve the selected options
        if self.out_doc_path is None:
            self.on_output(event)
            
            if self.out_doc_path is None:
                return

        # do it
        try:
            filtered = self.layer_filter.run(self.out_doc_path)
        except Exception as e:
            print(_('Something went wrong'))
            print(_('Exception') + ':')
            print(e)
        
            
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