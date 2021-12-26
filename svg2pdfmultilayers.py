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
import utils
from frozenclass import FrozenClass
from iotab import IOTab
from generationalgoinput import InputSelection
from generationalgooutput import OutputSelection
from custocanvastab import CustoCanvasTab
from trademarkcanvastab import TrademarkCanvasTab
from ressourcespath import resource_path
import re, uuid
import webbrowser
import wx.lib.buttons as buts

try:
    import pyi_splash
    pyi_splash.update_text('UI Loaded ...')
    pyi_splash.close()
except:
    pass
        
class byAnhorGUI(FrozenClass, wx.Frame):

    def __init__(self, *args, **kw):
        super(byAnhorGUI, self).__init__(*args, **kw)
        self.ToggleWindowStyle(wx.STAY_ON_TOP | wx.CLOSE_BOX)
        self.Centre(direction = wx.BOTH)
        self.Bind(wx.EVT_CLOSE, self.on_bye_pressed)

        self.working_dir = os.getcwd()
        self.temp_path = '%s/TEMP/'%self.working_dir
        if not os.path.exists(self.temp_path):
            os.makedirs(self.temp_path)

        self.gui_io = None
        self.gui_custo = None
        self.gui_trademark = None
        self.macadress = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
                
        self.draw_gui(kw['size'])
        
        self.manage_access_to_custo_or_trademark_canvas(False)
        
        if sys.platform == 'win32' or sys.platform == 'linux':
            self.SetIcon(wx.Icon(resource_path('icon.ico')))
       
        if len(sys.argv) > 1: self.gui_io.load_svg_file(sys.argv[1])       
        if len(sys.argv) > 2: self.gui_io.load_output_pdf_file(sys.argv[2])
            
        self._freeze()

    def draw_gui(self, size):
        splitter = wx.SplitterWindow(self,style=wx.SP_BORDER|wx.SP_LIVE_UPDATE)

        # create the notebook (top) and the panel (bottom)
        nb = wx.Notebook(splitter)
        pnl = wx.Panel(splitter)
        splitter.SplitHorizontally(nb,pnl)
        splitter.SetSashPosition(int(size[1]*3/4))
        splitter.SetMinimumPaneSize(10)        

        # The notebook (top) consists in 2 tabs
        self.gui_io = IOTab(nb,self)
        nb.AddPage(self.gui_io,'In/Out Options')
        self.gui_custo = CustoCanvasTab(nb,self)
        nb.AddPage(self.gui_custo,'Canvas customization')
        self.gui_trademark = TrademarkCanvasTab(nb,self)
        nb.AddPage(self.gui_trademark,'Trademark Canvas')

        # The panel (bottom) consists in 2 buttons ad the log window
        twolinessizer = wx.FlexGridSizer(2,1,0,0)
        twolinessizer.AddGrowableCol(0)
        twolinessizer.AddGrowableRow(1)
        pnl.SetSizer(twolinessizer)

        twocolumnssizer = wx.FlexGridSizer(1,3,0,0)
        # the go button and exit button and donate button
        go_btn = buts.GenBitmapTextButton(pnl, bitmap=None, label='Generate PDF', size=(120,30))
        go_btn.SetFont(go_btn.GetFont().Bold())
        go_btn.Bind(wx.EVT_BUTTON,self.on_go_pressed)
        twocolumnssizer.Add(go_btn)
        bye_btn = buts.GenBitmapTextButton(pnl, bitmap=None, label='Exit !', size=(120,30))
        bye_btn.SetFont(bye_btn.GetFont().Bold())
        bye_btn.Bind(wx.EVT_BUTTON,self.on_bye_pressed)
        twocolumnssizer.Add(bye_btn, flag = wx.LEFT, border = 20)
        donate = buts.GenBitmapTextButton(pnl, -1, bitmap=wx.Bitmap(resource_path("btn_donate_SM.gif")), size=(120,30))
        donate.Bind(wx.EVT_BUTTON,self.on_donate)
        twocolumnssizer.Add(donate, flag = wx.LEFT, border = 20)
        
        twolinessizer.Add(twocolumnssizer, flag = wx.EXPAND|wx.TOP|wx.LEFT, border = 20)
        
        # the log window and redirect console output
        log = wx.TextCtrl(pnl, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.HSCROLL)
        twolinessizer.Add(log, flag = wx.EXPAND|wx.ALL, border = 20)
        sys.stdout = log
        sys.stderr = log
        
    def on_donate(self, event):
        webbrowser.open('https://www.paypal.com/donate?business=V2YL9HEL2XHWQ&no_recurring=0&currency_code=EUR')

    def on_go_pressed(self,event):
        if self.gui_io.generation_algo_input.input_is_selected is InputSelection.NONE:
            print('Please select INPUT svg file before')
            return 
        if self.gui_io.generation_algo_input.input_is_selected is InputSelection.ONE_SVG and \
           self.gui_io.generation_algo_output.output_is_selected is OutputSelection.NONE:
            print('Please select OUTPUT pdf file before')
            self.gui_io.on_output_pdf(event)
            if self.gui_io.generation_algo_output.output_is_selected is OutputSelection.NONE:
                return
        if self.gui_io.use_trademark_canvas.GetValue() and self.gui_trademark.trademark_svg_canvas_filename is None:
            print('Please select INPUT svg own canvas file before')
            return
        self.gui_io.run()         

    def on_bye_pressed(self,event):
        print('BYE !!!!!!!!!!!!!!!!!')
        try:
            shutil.rmtree(self.temp_path)
        except Exception as e:
            print('Something went wrong in on_bye_pressed')
            print('Exception:', e)
        self.Destroy()

    def manage_access_to_custo_or_trademark_canvas(self,useTrademark):
        if self.gui_trademark is not None: 
            self.gui_trademark.Enable(useTrademark)
            self.gui_trademark.preview_image.Refresh()
        if self.gui_custo is not None: 
            self.gui_custo.Enable(not useTrademark)
            self.gui_custo.preview_image.Refresh()
           
if __name__ == '__main__':
    # When this module is run (not imported) then create the app, the
    # frame, show it, and start the event loop.

    language_warning = utils.setup_locale()

    app = wx.App()
    disp_h = wx.Display().GetGeometry().GetHeight()
    disp_w = wx.Display().GetGeometry().GetWidth()

    h = min(int(disp_h*0.95),1000)
    w = min(int(disp_w*0.80),1000)

    frm = byAnhorGUI(None, title='SVG -> PDF (multilayers)' + ' ' + utils.version_string, size=(w,h))

    if language_warning:
        print(language_warning)

    frm.Show()
    app.MainLoop()