# -*- coding: utf-8 -*-
# svg2pdfmultilayers is a utility to export multilayered SVG to PDF.
# Copyright (C) 2021 Anita Orhand
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


import fitz
import math
import string
'''import pdf_operators as pdf_ops
from decimal import Decimal
import traceback
import copy
#from os import write
#import sys
#import utils

STATE_OPS = [k for k,v in pdf_ops.ops.items() if v[0] == 'state']
STATE_OPS += [k for k,v in pdf_ops.ops.items() if v[0] in ['begin','end'] and v[1] != 'image']
STROKE_OPS = [k for k,v in pdf_ops.ops.items() if v[0] == 'show' and v[1] == 'stroke'] 
SKIP_TYPES = ['/Font','/ExtGState']
SKIP_KEYS = ['/Parent','/Thumb','/PieceInfo']
DEBUG = False

# helper functions to dump page to file for debugging
def write_page(fname,page):
    with open(fname,'w') as f:
        commands = pikepdf.parse_content_stream(page)
        f.write(pikepdf.unparse_content_stream(commands).decode('pdfdoc'))
'''

class LayerFilter:
    def __init__(self, onelayersvg = None, rect = None, canvas = None):
        self.canvas = canvas
        self.onelayersvg = onelayersvg
        self.rect = rect
        
        self.markercolortxt = (1,0,0)
        self.markerfillshape = (1,1,0.5)
        self.markercolorshape = (0,0,0)
        
    def set_canvas(self, canvas):
        self.canvas = canvas
        
    def rect_up(self, r, d):
        return fitz.Rect(r.x0, r.y0 - d, r.x1, r.y0)
    def rect_down(self, r, d):
        return fitz.Rect(r.x0, r.y1, r.x1, r.y1 + d)
    def rect_left(self, r, d):
        return fitz.Rect(r.x0 - d, r.y0, r.x0, r.y1)
    def rect_right(self, r, d):
        return fitz.Rect(r.x1, r.y0, r.x1 + d, r.y1)
    
               
    def run(self, outdocpath, generatea0, generatea4, generateassemblypagechoice, generateorderleftrightorleftright, generateassemblymarkchoice):
        
        outdocpathA0 = outdocpath.replace('.pdf', '.A0.pdf')
        outdocpathA4 = outdocpath.replace('.pdf', '.A4.pdf')
        
        if generatea0:

            print('-------------- G E N E R A T E --- A 0 -----------------', outdocpathA0)
            

            doc = fitz.open()  
            xrefOCG = dict()                   
            for k in self.onelayersvg.keys(): 
                xrefOCG[k] = doc.add_ocg('%s'%k)
            page = doc.new_page(-1, width = self.rect.width, height = self.rect.height)
            doc.save(outdocpathA0)
            doc.close()
    
            doc = fitz.open(outdocpathA0)  
            page0 = doc.load_page(0)
            try:
                for k in self.onelayersvg.keys(): 
                    curfilename = self.onelayersvg[k].replace('.svg', '.fitz.pdf')
                    print('Temporary create file ', curfilename)
                    tempsvg = fitz.open(curfilename)
                    pdfbytes = tempsvg.convert_to_pdf()
                    tempsvg.close()
                    tempsvg = fitz.open("pdf", pdfbytes) 
                    page0.show_pdf_page(self.rect, tempsvg, 0, oc=xrefOCG[k])
                    tempsvg.close()
                    doc.saveIncr()
                doc.close()
            except: doc.close()
            
        if generatea4:
            print('-------------- G E N E R A T E --- A 4 -----------------', outdocpathA4)
            
            if self.canvas is None:
                print('Please choose a canvas for A4 generation')
                return 
            
            canvassvgfilename = self.canvas
            canvaspdffilename = canvassvgfilename.replace('.svg', '.fitz.pdf')
            canvasdoc = fitz.open(canvassvgfilename)
            canvasdoc = canvasdoc.convert_to_pdf()
            canvasdoc = fitz.open("pdf", canvasdoc)
            canvaspage0 = canvasdoc.load_page(0)
            canvasrect = canvaspage0.rect
            sheetW = math.ceil(self.rect.width / canvasrect.width)
            sheetH = math.ceil(self.rect.height / canvasrect.height)
            canvasdoc.save(canvaspdffilename)
            canvasdoc.close()

            pageorder = list()
            if generateorderleftrightorleftright:
                for h in range(sheetH):
                    for w in range(sheetW):
                        pageorder.append((h,w))
            else:
                for w in range(sheetW):
                    for h in range(sheetH):
                        pageorder.append((h,w))
            
            doc = fitz.open()  
            xrefOCG = dict()                   
            for k in self.onelayersvg.keys(): 
                print(k + ' => ' + str(self.onelayersvg[k]))
                xrefOCG[k] = doc.add_ocg('%s'%k)
            xrefOCGA4In = doc.add_ocg('A4CanvasIn')
            xrefOCGA4Out = doc.add_ocg('A4CanvasOut')
            for p in range(len(pageorder)):
                page = doc.new_page(-1)#, width = self.rect.width, height = self.rect.height)
            print('Full size pattern (Pixel units 72 PPI) %sx%s'%(self.rect.width, self.rect.height))
            a4W = page.rect.width
            a4H = page.rect.height
            print('A4 size (Pixel units 72 PPI) %sx%s'%(a4W, a4H))
            print('Canvas size (Pixel units 72 PPI) %sx%s'%(canvasrect.width, canvasrect.height))
            if canvasrect.width > a4W or canvasrect.height > a4H:
                print('==> Please choose a canvas smaller than A4 format')                
                return 
            print('==> Need %s (%sx%s) sheets'%(sheetW*sheetH, sheetW, sheetH))
            if generateassemblypagechoice == 0:
                deltaW = (page.rect.width-canvasrect.width)/2.0
                deltaH = (page.rect.height-canvasrect.height)/2.0
                print('==> Margin around the active area (Pixel units 72 PPI) left/right = %s up/down = %s'%(deltaW, deltaH))
            else:
                deltaW = (page.rect.width-canvasrect.width)
                deltaH = (page.rect.height-canvasrect.height)
                print('==> Margin around the active area (Pixel units 72 PPI) right = %s down = %s'%(deltaW, deltaH))
                  
            canvasClipDico = dict()
            canvasClipDico['Right'] = fitz.Rect(0, 0, deltaW, canvasrect.height)
            canvasClipDico['Down'] = fitz.Rect(0, 0, canvasrect.width, deltaH)
            canvasClipDico['Left'] = None if generateassemblypagechoice == 1 else fitz.Rect(canvasrect.width-deltaW, 0, canvasrect.width, canvasrect.height)
            canvasClipDico['Up'] = None if generateassemblypagechoice == 1 else fitz.Rect(0, canvasrect.height-deltaH, canvasrect.width, canvasrect.height)
            
            pageRectDico = dict()
            patternClipDico = dict()
            pageNumDico = dict()
            curPage = 0
            for h,w in pageorder:
                idwh = 'L%sC%s '%(h,w)
                pageNumDico[idwh] = curPage
                
                pageRectDico[idwh] = dict()
                
                if generateassemblypagechoice == 0:
                    pageRectDico[idwh]['CenterForCanvas'] = fitz.Rect(canvasrect.x0+deltaW, canvasrect.y0+deltaH, canvasrect.x1+deltaW, canvasrect.y1+deltaH)
                else:
                    pageRectDico[idwh]['CenterForCanvas'] = fitz.Rect(canvasrect.x0+0, canvasrect.y0+0, canvasrect.x1+0, canvasrect.y1+0)

                pageRectDico[idwh]['RightForCanvas'] = self.rect_right(pageRectDico[idwh]['CenterForCanvas'], deltaW)  
                pageRectDico[idwh]['DownForCanvas'] = self.rect_down(pageRectDico[idwh]['CenterForCanvas'], deltaH)  
                pageRectDico[idwh]['LeftForCanvas'] = None if generateassemblypagechoice == 1 else self.rect_left(pageRectDico[idwh]['CenterForCanvas'], deltaW)
                pageRectDico[idwh]['UpForCanvas'] = None if generateassemblypagechoice == 1 else self.rect_up(pageRectDico[idwh]['CenterForCanvas'], deltaH) 
                
                if h == sheetH-1 and w == sheetW-1 : # last page
                    cutH = sheetH*canvasrect.height - self.rect.height
                    cutW = sheetW*canvasrect.width - self.rect.width
                    if generateassemblypagechoice == 0:
                        pageRectDico[idwh]['CenterForPattern'] = fitz.Rect(canvasrect.x0+deltaW, canvasrect.y0+deltaH, canvasrect.x1+deltaW-cutW, canvasrect.y1+deltaH-cutH)
                    else:
                        pageRectDico[idwh]['CenterForPattern'] = fitz.Rect(canvasrect.x0+0, canvasrect.y0+0, canvasrect.x1+0-cutW, canvasrect.y1+0-cutH)
                elif h == sheetH-1: # last line
                    cutH = sheetH*canvasrect.height - self.rect.height
                    if generateassemblypagechoice == 0:
                        pageRectDico[idwh]['CenterForPattern'] = fitz.Rect(canvasrect.x0+deltaW, canvasrect.y0+deltaH, canvasrect.x1+deltaW, canvasrect.y1+deltaH-cutH)
                    else:
                        pageRectDico[idwh]['CenterForPattern'] = fitz.Rect(canvasrect.x0+0, canvasrect.y0+0, canvasrect.x1+0, canvasrect.y1+0-cutH)
                elif w == sheetW-1: # last col
                    cutW = sheetW*canvasrect.width - self.rect.width
                    if generateassemblypagechoice == 0:
                        pageRectDico[idwh]['CenterForPattern'] = fitz.Rect(canvasrect.x0+deltaW, canvasrect.y0+deltaH, canvasrect.x1+deltaW-cutW, canvasrect.y1+deltaH)
                    else:
                        pageRectDico[idwh]['CenterForPattern'] = fitz.Rect(canvasrect.x0+0, canvasrect.y0+0, canvasrect.x1+0-cutW, canvasrect.y1+0)
                else:
                    pageRectDico[idwh]['CenterForPattern'] = pageRectDico[idwh]['CenterForCanvas'] 

                pageRectDico[idwh]['RightForPattern'] = self.rect_right(pageRectDico[idwh]['CenterForPattern'], deltaW)  
                pageRectDico[idwh]['DownForPattern'] = self.rect_down(pageRectDico[idwh]['CenterForPattern'], deltaH)  
                pageRectDico[idwh]['LeftForPattern'] = None if generateassemblypagechoice == 1 else self.rect_left(pageRectDico[idwh]['CenterForPattern'], deltaW)
                pageRectDico[idwh]['UpForPattern'] = None if generateassemblypagechoice == 1 else self.rect_up(pageRectDico[idwh]['CenterForPattern'], deltaH) 
                
                
                patternClipDico[idwh] = dict()
                patternClipDico[idwh]['Center'] = fitz.Rect(w*canvasrect.width, h*canvasrect.height, 
                                                  min((w+1)*canvasrect.width,self.rect.width),
                                                  min((h+1)*canvasrect.height,self.rect.height))                    
                patternClipDico[idwh]['Right'] = None if w == sheetW-1 else fitz.Rect((w+1)*canvasrect.width, h*canvasrect.height, 
                                                                                      min((w+1)*canvasrect.width+deltaW,self.rect.width),
                                                                                      min((h+1)*canvasrect.height,self.rect.height))                    
                patternClipDico[idwh]['Down'] = None if h == sheetH-1 else fitz.Rect(w*canvasrect.width, (h+1)*canvasrect.height, 
                                                                                      min((w+1)*canvasrect.width,self.rect.width),
                                                                                      min((h+1)*canvasrect.height+deltaH,self.rect.height))                    
                patternClipDico[idwh]['Left'] = None if w == 0 or generateassemblypagechoice == 1 else fitz.Rect(w*canvasrect.width-deltaW, h*canvasrect.height, 
                                                                              w*canvasrect.width,
                                                                              min((h+1)*canvasrect.height,self.rect.height))                    
                patternClipDico[idwh]['Up'] = None if h == 0 or generateassemblypagechoice == 1 else fitz.Rect(w*canvasrect.width, h*canvasrect.height-deltaH, 
                                                                          min((w+1)*canvasrect.width,self.rect.width),
                                                                          h*canvasrect.height)                    
                curPage = curPage + 1
           
            doc.save(outdocpathA4)
            doc.close()

            doc = fitz.open(outdocpathA4)  
            try:
                print(_('Generate the canvas on each page = central panel + (right/left/down/up) if existing + LxCy textbox'))
                for h,w in pageorder:
                    idwh = 'L%sC%s '%(h,w)
                    pagei = doc.load_page(pageNumDico[idwh])
                    tempsvg = fitz.open(canvaspdffilename)
                    pdfbytes = tempsvg.convert_to_pdf()
                    tempsvg.close()
                    tempsvg = fitz.open("pdf", pdfbytes) 
                    
                    pagei.show_pdf_page(pageRectDico[idwh]['CenterForCanvas'], tempsvg, 0, oc=xrefOCGA4In)
                        
                    if w < sheetW - 1:                            pagei.show_pdf_page(pageRectDico[idwh]['RightForCanvas'], tempsvg, 0, oc=xrefOCGA4Out, clip=canvasClipDico['Right'])
                    if h < sheetH - 1:                            pagei.show_pdf_page(pageRectDico[idwh]['DownForCanvas'], tempsvg, 0, oc=xrefOCGA4Out, clip=canvasClipDico['Down'])
                    if w > 0 and generateassemblypagechoice == 0: pagei.show_pdf_page(pageRectDico[idwh]['LeftForCanvas'], tempsvg, 0, oc=xrefOCGA4Out, clip=canvasClipDico['Left'])
                    if h > 0 and generateassemblypagechoice == 0: pagei.show_pdf_page(pageRectDico[idwh]['UpForCanvas'], tempsvg, 0, oc=xrefOCGA4Out, clip=canvasClipDico['Up'])
                        
                    tempsvg.close()
                    shape = pagei.new_shape() # create Shape
                    rc = shape.insert_textbox(pageRectDico[idwh]['CenterForCanvas'], 'L%sC%s'%(h,w), fontname = 'courier-bold', fontsize = 48, 
                                              color = (0.9, 0.9, 0.9), align = fitz.TEXT_ALIGN_CENTER, oc=xrefOCGA4In)
                    shape.commit()
                    
                    if generateassemblymarkchoice != 0:
                        
                        txt = dict()
                        if generateassemblymarkchoice == 1:
                            txt['C'] = 'L%sC%s'%(h,w)
                            txt['U'],txt['D'],txt['L'],txt['R'] = txt['C'],txt['C'],txt['C'],txt['C']
                            txt['UU'] = 'L%sC%s'%(h-1,w)
                            txt['DD'] = 'L%sC%s'%(h+1,w)
                            txt['LL'] = 'L%sC%s'%(h,w-1)
                            txt['RR'] = 'L%sC%s'%(h,w+1)
                        elif generateassemblymarkchoice == 2:
                            txt['U'] = '%s-%s'%(string.ascii_uppercase[h],w)
                            txt['D'] = '%s-%s'%(string.ascii_uppercase[h+1],w)
                            txt['L'] = '%s-%s'%(h,string.ascii_lowercase[w])
                            txt['R'] = '%s-%s'%(h,string.ascii_lowercase[w+1])
                            txt['UU'],txt['DD'],txt['LL'],txt['RR'] = txt['U'],txt['D'],txt['L'],txt['R']
                            
                        # Annote page number neighbourhood
                        self.upmark(pageRectDico[idwh]['CenterForCanvas'], pagei, txt, xrefOCGA4In , xrefOCGA4Out, h > 0 and generateassemblypagechoice == 0)
                        self.downmark(pageRectDico[idwh]['CenterForCanvas'], pagei, txt, xrefOCGA4In , xrefOCGA4Out, h < sheetH-1)
                        self.leftmark(pageRectDico[idwh]['CenterForCanvas'], pagei, txt, xrefOCGA4In , xrefOCGA4Out, w > 0 and generateassemblypagechoice == 0)
                        self.rightmark(pageRectDico[idwh]['CenterForCanvas'], pagei, txt, xrefOCGA4In , xrefOCGA4Out, w < sheetW-1)
                    
                    doc.saveIncr()
                doc.close()
            except Exception as e:
                doc.close()
                print(_('Something went wrong during phase 1'))
                print(_('Exception') + ':')
                print(e)
             
            try:
                doc = fitz.open(outdocpathA4)  
                for k in self.onelayersvg.keys(): 
                    curfilename = self.onelayersvg[k].replace('.svg', '.fitz.pdf')
                    tempsvg = fitz.open(curfilename)
                    pdfbytes = tempsvg.convert_to_pdf()
                    tempsvg.close()
                    tempsvg = fitz.open("pdf", pdfbytes) 
                    print(_('Generate the layer %s on each page = central panel + (right/left/down/up) if existing')%k)
                    for h,w in pageorder:
                        idwh = 'L%sC%s '%(h,w)
                        curPage = pageNumDico[idwh] 
                        pagei = doc.load_page(curPage)
                        
                        pagei.show_pdf_page(pageRectDico[idwh]['CenterForPattern'], tempsvg, 0, oc=xrefOCG[k], clip=patternClipDico[idwh]['Center'])
                        
                        if w < sheetW - 1:
                            try: 
                                pagei.show_pdf_page(pageRectDico[idwh]['RightForPattern'], tempsvg, 0, oc=xrefOCG[k], overlays=False, clip=patternClipDico[idwh]['Right'])
                                shape = pagei.new_shape()
                                shape.draw_rect(pageRectDico[idwh]['RightForCanvas'])
                                shape.finish(fill = (0.95,0.95,0.95), fill_opacity=0.2)
                                shape.commit()
                            except Exception as e: print('Warning : Cannot add RIGHT margin to %s'%idwh)
                        if h < sheetH - 1:
                            try: 
                                pagei.show_pdf_page(pageRectDico[idwh]['DownForPattern'], tempsvg, 0, oc=xrefOCG[k], overlays=False, clip=patternClipDico[idwh]['Down'])
                                shape = pagei.new_shape()
                                shape.draw_rect(pageRectDico[idwh]['DownForCanvas'])
                                shape.finish(fill = (0.95,0.95,0.95), fill_opacity=0.2)
                                shape.commit()
                            except Exception as e: print('Warning : Cannot add DOWN margin to %s'%idwh)
                        if w > 0 and generateassemblypagechoice == 0:
                            try: 
                                pagei.show_pdf_page(pageRectDico[idwh]['LeftForPattern'], tempsvg, 0, oc=xrefOCG[k], overlays=False, clip=patternClipDico[idwh]['Left'])
                                shape = pagei.new_shape()
                                shape.draw_rect(pageRectDico[idwh]['LeftForCanvas'])
                                shape.finish(fill = (0.95,0.95,0.95), fill_opacity=0.2)
                                shape.commit()
                            except Exception as e: print('Warning : Cannot add LEFT margin to %s'%idwh)
                        if h > 0 and generateassemblypagechoice == 0:
                            try:
                                pagei.show_pdf_page(pageRectDico[idwh]['UpForPattern'], tempsvg, 0, oc=xrefOCG[k], overlays=False, clip=patternClipDico[idwh]['Up'])
                                shape = pagei.new_shape()
                                shape.draw_rect(pageRectDico[idwh]['UpForCanvas'])
                                shape.finish(fill = (0.95,0.95,0.95), fill_opacity=0.2)
                                shape.commit()
                            except Exception as e: print('Warning : Cannot add UP margin to %s'%idwh)
                    tempsvg.close()
                    doc.saveIncr()
                doc.close()
            except Exception as e:
                doc.close()
                print(_('Something went wrong during phase 2'))
                print(_('Exception') + ':')
                print(e)

        print(_('Done !'))
        return outdocpath
    
    def upmark(self, CenterForCanvas, pagei, txt, xrefOCGA4In , xrefOCGA4Out, cond):

        shape = pagei.new_shape() 
        CenterForCanvasXmin, CenterForCanvasXmax = CenterForCanvas.tl.x, CenterForCanvas.br.x
        CenterForCanvasXhalf = (CenterForCanvasXmin+CenterForCanvasXmax)/2.0
        CenterForCanvasYmin, CenterForCanvasYmax = CenterForCanvas.br.y, CenterForCanvas.tl.y
        CenterForCanvasYhalf = (CenterForCanvasYmin+CenterForCanvasYmax)/2.0
        
        shape.draw_sector((CenterForCanvasXhalf,CenterForCanvasYmax), (CenterForCanvasXhalf-30,CenterForCanvasYmax), 180)
        shape.finish(fill = self.markerfillshape, color = self.markercolorshape, fill_opacity=1.0)
        shape.commit()

        shape = pagei.new_shape() 
        rup = fitz.Rect(CenterForCanvasXmin, CenterForCanvasYmax, CenterForCanvasXmax, CenterForCanvasYmax+20)
        rc = shape.insert_textbox(rup, txt['U'], fontname = 'courier-bold', fontsize = 14, 
                                  color = self.markercolortxt, align = fitz.TEXT_ALIGN_CENTER, oc=xrefOCGA4In)
        shape.commit()
        #####
        if cond:
            shape = pagei.new_shape() 
            shape.draw_sector((CenterForCanvasXhalf,CenterForCanvasYmax), (CenterForCanvasXhalf+30,CenterForCanvasYmax), 180)
            shape.finish(fill = self.markerfillshape, color = self.markercolorshape, fill_opacity=0.2)
            shape.commit()

            rupup = fitz.Rect(CenterForCanvasXmin, CenterForCanvasYmax-20, CenterForCanvasXmax, CenterForCanvasYmax)
            rc = shape.insert_textbox(rupup, txt['UU'], fontname = 'courier-bold', fontsize = 14, 
                                  color = self.markercolortxt, align = fitz.TEXT_ALIGN_CENTER, oc=xrefOCGA4Out)
            shape.commit()


    def downmark(self, CenterForCanvas, pagei, txt, xrefOCGA4In , xrefOCGA4Out, cond):

        shape = pagei.new_shape() 
        CenterForCanvasXmin, CenterForCanvasXmax = CenterForCanvas.tl.x, CenterForCanvas.br.x
        CenterForCanvasXhalf = (CenterForCanvasXmin+CenterForCanvasXmax)/2.0
        CenterForCanvasYmin, CenterForCanvasYmax = CenterForCanvas.br.y, CenterForCanvas.tl.y
        CenterForCanvasYhalf = (CenterForCanvasYmin+CenterForCanvasYmax)/2.0
        
        shape.draw_sector((CenterForCanvasXhalf,CenterForCanvasYmin), (CenterForCanvasXhalf+30,CenterForCanvasYmin), 180)
        shape.finish(fill = self.markerfillshape, color = self.markercolorshape, fill_opacity=1.0)
        shape.commit()

        shape = pagei.new_shape() 
        rdown = fitz.Rect(CenterForCanvasXmin, CenterForCanvasYmin-20, CenterForCanvasXmax, CenterForCanvasYmin)
        rc = shape.insert_textbox(rdown, txt['D'], fontname = 'courier-bold', fontsize = 14, 
                                  color = self.markercolortxt, align = fitz.TEXT_ALIGN_CENTER, oc=xrefOCGA4In)
        shape.commit()
        #####
        if cond:
            shape = pagei.new_shape() 
            shape.draw_sector((CenterForCanvasXhalf,CenterForCanvasYmin), (CenterForCanvasXhalf-30,CenterForCanvasYmin), 180)
            shape.finish(fill = self.markerfillshape, color = self.markercolorshape, fill_opacity=0.2)
            shape.commit()

            rdowndown = fitz.Rect(CenterForCanvasXmin, CenterForCanvasYmin, CenterForCanvasXmax, CenterForCanvasYmin+20)
            rc = shape.insert_textbox(rdowndown, txt['DD'], fontname = 'courier-bold', fontsize = 14, 
                                  color = self.markercolortxt, align = fitz.TEXT_ALIGN_CENTER, oc=xrefOCGA4Out)
            shape.commit()


    def leftmark(self, CenterForCanvas, pagei, txt, xrefOCGA4In , xrefOCGA4Out, cond):
        
        shape = pagei.new_shape() 
        CenterForCanvasXmin, CenterForCanvasXmax = CenterForCanvas.tl.x, CenterForCanvas.br.x
        CenterForCanvasXhalf = (CenterForCanvasXmin+CenterForCanvasXmax)/2.0
        CenterForCanvasYmin, CenterForCanvasYmax = CenterForCanvas.br.y, CenterForCanvas.tl.y
        CenterForCanvasYhalf = (CenterForCanvasYmin+CenterForCanvasYmax)/2.0
        
        shape.draw_sector((CenterForCanvasXmin,CenterForCanvasYhalf), (CenterForCanvasXmin,CenterForCanvasYhalf+30), 180)
        shape.finish(fill = self.markerfillshape, color = self.markercolorshape, fill_opacity=1.0)
        shape.commit()
        
        shape = pagei.new_shape() 
        rleft = fitz.Rect(CenterForCanvasXmin, CenterForCanvasYmax, CenterForCanvasXmin+20, CenterForCanvasYmin)
        rc = shape.insert_textbox(rleft, txt['L'], fontname = 'courier-bold', fontsize = 14, 
                                  color = self.markercolortxt, align = fitz.TEXT_ALIGN_CENTER, oc=xrefOCGA4In, rotate = 90)
        shape.commit()
        
        #####
        if cond:
            shape = pagei.new_shape() 
            shape.draw_sector((CenterForCanvasXmin,CenterForCanvasYhalf), (CenterForCanvasXmin,CenterForCanvasYhalf-30), 180)
            shape.finish(fill = self.markerfillshape, color = self.markercolorshape, fill_opacity=0.2)
            shape.commit()
            
            rleftleft = fitz.Rect(CenterForCanvasXmin-20, CenterForCanvasYmax, CenterForCanvasXmin, CenterForCanvasYmin)
            rc = shape.insert_textbox(rleftleft, txt['LL'], fontname = 'courier-bold', fontsize = 14, 
                                  color = self.markercolortxt, align = fitz.TEXT_ALIGN_CENTER, oc=xrefOCGA4Out, rotate = 90)
            shape.commit()

    def rightmark(self, CenterForCanvas, pagei, txt, xrefOCGA4In , xrefOCGA4Out, cond):
        
        shape = pagei.new_shape() 
        CenterForCanvasXmin, CenterForCanvasXmax = CenterForCanvas.tl.x, CenterForCanvas.br.x
        CenterForCanvasXhalf = (CenterForCanvasXmin+CenterForCanvasXmax)/2.0
        CenterForCanvasYmin, CenterForCanvasYmax = CenterForCanvas.br.y, CenterForCanvas.tl.y
        CenterForCanvasYhalf = (CenterForCanvasYmin+CenterForCanvasYmax)/2.0
        
        shape.draw_sector((CenterForCanvasXmax,CenterForCanvasYhalf), (CenterForCanvasXmax,CenterForCanvasYhalf-30), 180)
        shape.finish(fill = self.markerfillshape, color = self.markercolorshape, fill_opacity=1.0)
        shape.commit()
        
        shape = pagei.new_shape() 
        rright = fitz.Rect(CenterForCanvasXmax-20, CenterForCanvasYmax, CenterForCanvasXmax, CenterForCanvasYmin)
        rc = shape.insert_textbox(rright, txt['R'], fontname = 'courier-bold', fontsize = 14, 
                                  color = self.markercolortxt, align = fitz.TEXT_ALIGN_CENTER, oc=xrefOCGA4In, rotate = 90)
        shape.commit()
        
        #####
        if cond:
            shape = pagei.new_shape() 
            shape.draw_sector((CenterForCanvasXmax,CenterForCanvasYhalf), (CenterForCanvasXmax,CenterForCanvasYhalf+30), 180)
            shape.finish(fill = self.markerfillshape, color = self.markercolorshape, fill_opacity=0.2)
            shape.commit()
            
            rrightright = fitz.Rect(CenterForCanvasXmax, CenterForCanvasYmax, CenterForCanvasXmax+20, CenterForCanvasYmin)
            rc = shape.insert_textbox(rrightright, txt['RR'], fontname = 'courier-bold', fontsize = 14, 
                                  color = self.markercolortxt, align = fitz.TEXT_ALIGN_CENTER, oc=xrefOCGA4Out, rotate = 90)
            shape.commit()
        
        
        


        
