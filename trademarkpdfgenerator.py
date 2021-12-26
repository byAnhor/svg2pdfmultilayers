# -*- coding: utf-8 -*-
# svg2pdfmultilayers is a utility to export multilayered SVG to PDF.
# Copyright (C) 2021 Anita Orhand
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


import fitz
import string
from pdfgeneratora4 import PDFGeneratorA4
from enums import CanvasOnSheet, TapeMarks, Areas

class TrademarkPDFGenerator(PDFGeneratorA4):
    def __init__(self):
        super(TrademarkPDFGenerator, self).__init__()
        self.canvasFile = None
        self._freeze()
        
    @property
    def canvasFile(self): return self.__canvasFile
    @canvasFile.setter
    def canvasFile(self, v):
        assert v is None or isinstance(v, str), "assert false canvasFile"
        self.__canvasFile = v

    def generateCanvas(self, doc):
        print('Generate the canvas on each page = central panel + (right/left/down/up) if existing + LxCy textbox')
        for h,w in self.orderedPageList:
            idwh = 'L%sC%s'%(h,w)
            pagei = doc.load_page(self.pageNumDico[idwh])
            tempsvg = fitz.open(self.canvasFile)
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
            #shape = pagei.new_shape() # create Shape
            #shape.insert_textbox(self.canvasShowRectsDico[idwh][Areas.C], 'L%sC%s'%(h,w), fontname = 'courier-bold', fontsize = 48, 
            #                     color = (0.9, 0.9, 0.9), align = fitz.TEXT_ALIGN_CENTER, oc=self.xrefOCGA4In)
            #shape.commit()
            
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
        

    


        
