# -*- coding: utf-8 -*-
# svg2pdfmultilayers is a utility to export multilayered SVG to PDF.
# Copyright (C) 2021 Anita Orhand
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


import fitz
import string
from pdfgenerator import PDFGenerator, CanvasOnSheet, TapeMarks, Areas

class CustoPDFGenerator(PDFGenerator):
    def __init__(self, maingui):
        super(CustoPDFGenerator, self).__init__()
        self.maingui = maingui
       
    def getCanvasFile(self):
        return self.maingui.gui_custo.temp_canvas_pdf

    def generateCanvas(self, doc):
        print('Generate the canvas on each page = central panel + (right/left/down/up) if existing + LxCy textbox')
        for h,w in self.orderedPageList:
            idwh = 'L%sC%s '%(h,w)
            pagei = doc.load_page(self.pageNumDico[idwh])
            tempsvg = fitz.open(self.getCanvasFile())
            pdfbytes = tempsvg.convert_to_pdf()
            tempsvg.close()
            tempsvg = fitz.open("pdf", pdfbytes) 
            
            pagei.show_pdf_page(self.canvasShowRectsDico[idwh][Areas.C], tempsvg, 0, oc=self.xrefOCGA4In)

            condL = w > 0 and self.generateSheetTrimming == CanvasOnSheet.CENTERED
            condR = w < self.needSheetW - 1
            condT = h > 0 and self.generateSheetTrimming == CanvasOnSheet.CENTERED
            condD = h < self.needSheetH - 1
            
            if self.deltaW > 0:
                if condR:
                    pagei.show_pdf_page(self.canvasShowRectsDico[idwh][Areas.R], tempsvg, 0, oc=self.xrefOCGA4Out, clip=self.canvasClipRectsDico[Areas.R])
                if condL:
                    pagei.show_pdf_page(self.canvasShowRectsDico[idwh][Areas.L], tempsvg, 0, oc=self.xrefOCGA4Out, clip=self.canvasClipRectsDico[Areas.L])
            if self.deltaH > 0:
                if condT: 
                    pagei.show_pdf_page(self.canvasShowRectsDico[idwh][Areas.T], tempsvg, 0, oc=self.xrefOCGA4Out, clip=self.canvasClipRectsDico[Areas.T])
                if condD:                                    
                    pagei.show_pdf_page(self.canvasShowRectsDico[idwh][Areas.D], tempsvg, 0, oc=self.xrefOCGA4Out, clip=self.canvasClipRectsDico[Areas.D])
            if self.deltaW > 0 and self.deltaH > 0:
                if condT and condR:
                    pagei.show_pdf_page(self.canvasShowRectsDico[idwh][Areas.TR], tempsvg, 0, oc=self.xrefOCGA4Out, clip=self.canvasClipRectsDico[Areas.TR])
                if condT and condL:
                    pagei.show_pdf_page(self.canvasShowRectsDico[idwh][Areas.TL], tempsvg, 0, oc=self.xrefOCGA4Out, clip=self.canvasClipRectsDico[Areas.TL])
                if condD and condR:                                    
                    pagei.show_pdf_page(self.canvasShowRectsDico[idwh][Areas.DR], tempsvg, 0, oc=self.xrefOCGA4Out, clip=self.canvasClipRectsDico[Areas.DR])
                if condD and condL:                                    
                    pagei.show_pdf_page(self.canvasShowRectsDico[idwh][Areas.DL], tempsvg, 0, oc=self.xrefOCGA4Out, clip=self.canvasClipRectsDico[Areas.DL])
                
                
            tempsvg.close()
            shape = pagei.new_shape() # create Shape
            shape.insert_textbox(self.canvasShowRectsDico[idwh][Areas.C], 'L%sC%s'%(h,w), fontname = 'courier-bold', fontsize = 48, 
                                 color = (0.9, 0.9, 0.9), align = fitz.TEXT_ALIGN_CENTER, oc=self.xrefOCGA4In)
            shape.commit()
            
            if self.generateMaskingTapeTxt != TapeMarks.NO:
                
                txt = dict()
                if self.generateMaskingTapeTxt == TapeMarks.LXCY:
                    txt['C'] = 'L%sC%s'%(h,w)
                    txt['U'],txt['D'],txt['L'],txt['R'] = txt['C'],txt['C'],txt['C'],txt['C']
                    txt['UU'] = 'L%sC%s'%(h-1,w)
                    txt['DD'] = 'L%sC%s'%(h+1,w)
                    txt['LL'] = 'L%sC%s'%(h,w-1)
                    txt['RR'] = 'L%sC%s'%(h,w+1)
                elif self.generateMaskingTapeTxt == TapeMarks.AA:
                    txt['U'] = '%s-%s'%(string.ascii_uppercase[h],w)
                    txt['D'] = '%s-%s'%(string.ascii_uppercase[h+1],w)
                    txt['L'] = '%s-%s'%(h,string.ascii_lowercase[w])
                    txt['R'] = '%s-%s'%(h,string.ascii_lowercase[w+1])
                    txt['UU'],txt['DD'],txt['LL'],txt['RR'] = txt['U'],txt['D'],txt['L'],txt['R']
                    
                # Annote page number neighbourhood
                self.upmark(self.canvasShowRectsDico[idwh][Areas.C], pagei, txt, self.xrefOCGA4In , self.xrefOCGA4Out, h > 0)
                self.downmark(self.canvasShowRectsDico[idwh][Areas.C], pagei, txt, self.xrefOCGA4In , self.xrefOCGA4Out, h < self.needSheetH-1)
                self.leftmark(self.canvasShowRectsDico[idwh][Areas.C], pagei, txt, self.xrefOCGA4In , self.xrefOCGA4Out, w > 0)
                self.rightmark(self.canvasShowRectsDico[idwh][Areas.C], pagei, txt, self.xrefOCGA4In , self.xrefOCGA4Out, w < self.needSheetW-1)
            
            doc.saveIncr()
        doc.close()
    
    def upmark(self, CenterForCanvas, pagei, txt, xrefOCGA4In , xrefOCGA4Out, cond):

        #shape = pagei.new_shape() 
        CenterForCanvasXmin, CenterForCanvasXmax = CenterForCanvas.tl.x, CenterForCanvas.br.x
        CenterForCanvasYmax = CenterForCanvas.tl.y
        
        #shape.draw_sector((CenterForCanvasXhalf,CenterForCanvasYmax), (CenterForCanvasXhalf-30,CenterForCanvasYmax), 180)
        #shape.finish(fill = self.markerfillshape, color = self.markercolorshape, fill_opacity=1.0)
        #shape.commit()

        shape = pagei.new_shape() 
        rup = fitz.Rect(CenterForCanvasXmin, CenterForCanvasYmax, CenterForCanvasXmax, CenterForCanvasYmax+20)
        shape.insert_textbox(rup, txt['U'], fontname = 'courier-bold', fontsize = 14, 
                             color = self.markercolortxt, align = fitz.TEXT_ALIGN_CENTER, oc=xrefOCGA4In)
        shape.commit()
        #####
        if cond:
            #shape = pagei.new_shape() 
            #shape.draw_sector((CenterForCanvasXhalf,CenterForCanvasYmax), (CenterForCanvasXhalf+30,CenterForCanvasYmax), 180)
            #shape.finish(fill = self.markerfillshape, color = self.markercolorshape, fill_opacity=0.2)
            #shape.commit()

            rupup = fitz.Rect(CenterForCanvasXmin, CenterForCanvasYmax-20, CenterForCanvasXmax, CenterForCanvasYmax)
            shape.insert_textbox(rupup, txt['UU'], fontname = 'courier-bold', fontsize = 14, 
                                 color = self.markercolortxt, align = fitz.TEXT_ALIGN_CENTER, oc=xrefOCGA4Out)
            shape.commit()


    def downmark(self, CenterForCanvas, pagei, txt, xrefOCGA4In , xrefOCGA4Out, cond):

        #shape = pagei.new_shape() 
        CenterForCanvasXmin, CenterForCanvasXmax = CenterForCanvas.tl.x, CenterForCanvas.br.x
        CenterForCanvasYmin = CenterForCanvas.br.y
        
        #shape.draw_sector((CenterForCanvasXhalf,CenterForCanvasYmin), (CenterForCanvasXhalf+30,CenterForCanvasYmin), 180)
        #shape.finish(fill = self.markerfillshape, color = self.markercolorshape, fill_opacity=1.0)
        #shape.commit()

        shape = pagei.new_shape() 
        rdown = fitz.Rect(CenterForCanvasXmin, CenterForCanvasYmin-20, CenterForCanvasXmax, CenterForCanvasYmin)
        shape.insert_textbox(rdown, txt['D'], fontname = 'courier-bold', fontsize = 14, 
                             color = self.markercolortxt, align = fitz.TEXT_ALIGN_CENTER, oc=xrefOCGA4In)
        shape.commit()
        #####
        if cond:
            #shape = pagei.new_shape() 
            #shape.draw_sector((CenterForCanvasXhalf,CenterForCanvasYmin), (CenterForCanvasXhalf-30,CenterForCanvasYmin), 180)
            #shape.finish(fill = self.markerfillshape, color = self.markercolorshape, fill_opacity=0.2)
            #shape.commit()

            rdowndown = fitz.Rect(CenterForCanvasXmin, CenterForCanvasYmin, CenterForCanvasXmax, CenterForCanvasYmin+20)
            shape.insert_textbox(rdowndown, txt['DD'], fontname = 'courier-bold', fontsize = 14, 
                                 color = self.markercolortxt, align = fitz.TEXT_ALIGN_CENTER, oc=xrefOCGA4Out)
            shape.commit()


    def leftmark(self, CenterForCanvas, pagei, txt, xrefOCGA4In , xrefOCGA4Out, cond):
        
        #shape = pagei.new_shape() 
        CenterForCanvasXmin = CenterForCanvas.tl.x
        CenterForCanvasYmin, CenterForCanvasYmax = CenterForCanvas.br.y, CenterForCanvas.tl.y
        
        #shape.draw_sector((CenterForCanvasXmin,CenterForCanvasYhalf), (CenterForCanvasXmin,CenterForCanvasYhalf+30), 180)
        #shape.finish(fill = self.markerfillshape, color = self.markercolorshape, fill_opacity=1.0)
        #shape.commit()
        
        shape = pagei.new_shape() 
        rleft = fitz.Rect(CenterForCanvasXmin, CenterForCanvasYmax, CenterForCanvasXmin+20, CenterForCanvasYmin)
        shape.insert_textbox(rleft, txt['L'], fontname = 'courier-bold', fontsize = 14, 
                             color = self.markercolortxt, align = fitz.TEXT_ALIGN_CENTER, oc=xrefOCGA4In, rotate = 90)
        shape.commit()
        
        #####
        if cond:
            #shape = pagei.new_shape() 
            #shape.draw_sector((CenterForCanvasXmin,CenterForCanvasYhalf), (CenterForCanvasXmin,CenterForCanvasYhalf-30), 180)
            #shape.finish(fill = self.markerfillshape, color = self.markercolorshape, fill_opacity=0.2)
            #shape.commit()
            
            rleftleft = fitz.Rect(CenterForCanvasXmin-20, CenterForCanvasYmax, CenterForCanvasXmin, CenterForCanvasYmin)
            shape.insert_textbox(rleftleft, txt['LL'], fontname = 'courier-bold', fontsize = 14, 
                                 color = self.markercolortxt, align = fitz.TEXT_ALIGN_CENTER, oc=xrefOCGA4Out, rotate = 90)
            shape.commit()

    def rightmark(self, CenterForCanvas, pagei, txt, xrefOCGA4In , xrefOCGA4Out, cond):
        
        #shape = pagei.new_shape() 
        CenterForCanvasXmax = CenterForCanvas.br.x
        CenterForCanvasYmin, CenterForCanvasYmax = CenterForCanvas.br.y, CenterForCanvas.tl.y
        
        #shape.draw_sector((CenterForCanvasXmax,CenterForCanvasYhalf), (CenterForCanvasXmax,CenterForCanvasYhalf-30), 180)
        #shape.finish(fill = self.markerfillshape, color = self.markercolorshape, fill_opacity=1.0)
        #shape.commit()
        
        shape = pagei.new_shape() 
        rright = fitz.Rect(CenterForCanvasXmax-20, CenterForCanvasYmax, CenterForCanvasXmax, CenterForCanvasYmin)
        shape.insert_textbox(rright, txt['R'], fontname = 'courier-bold', fontsize = 14, 
                             color = self.markercolortxt, align = fitz.TEXT_ALIGN_CENTER, oc=xrefOCGA4In, rotate = 90)
        shape.commit()
        
        #####
        if cond:
            #shape = pagei.new_shape() 
            #shape.draw_sector((CenterForCanvasXmax,CenterForCanvasYhalf), (CenterForCanvasXmax,CenterForCanvasYhalf+30), 180)
            #shape.finish(fill = self.markerfillshape, color = self.markercolorshape, fill_opacity=0.2)
            #shape.commit()
            
            rrightright = fitz.Rect(CenterForCanvasXmax, CenterForCanvasYmax, CenterForCanvasXmax+20, CenterForCanvasYmin)
            shape.insert_textbox(rrightright, txt['RR'], fontname = 'courier-bold', fontsize = 14, 
                                 color = self.markercolortxt, align = fitz.TEXT_ALIGN_CENTER, oc=xrefOCGA4Out, rotate = 90)
            shape.commit()
        
        
        



        
