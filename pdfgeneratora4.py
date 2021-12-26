# -*- coding: utf-8 -*-
# svg2pdfmultilayers is a utility to export multilayered SVG to PDF.
# Copyright (C) 2021 Anita Orhand
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


import os
import sys
import fitz
import math
import PyPDF2
from abc import abstractmethod
from frozenclass import FrozenClass
from pdfgenerator import PDFGenerator
from ressourcespath import resource_path
from enums import CanvasOnSheet, TapeMarks, Areas, PagesOrdering, PagesOrientation, PagesNumbering
from PyPDF2 import PdfFileReader, PdfFileMerger, PdfFileWriter

class MyPdfFileWriter(PdfFileWriter):
    def __init__(self):
        super().__init__()
        self.ocgsDico = dict()
        
    def myCloneDocumentFromReader(self, reader, after_page_append=None):
        # Variables used for after cloning the root to improve pre- and post- cloning experience
        # Clone the reader's root document
        self._root_object = reader.trailer['/Root']
        self._root = self._addObject(self._root_object)
        # Sweep for all indirect references
        externalReferenceMap = {}
        self.stack = []
        newRootRef = self._sweepIndirectReferences(externalReferenceMap, self._root)
        ocProperties = self._root.getObject()["/OCProperties"]
        ocgs = ocProperties['/OCGs']   
        for ocg in ocgs:
            self.ocgsDico[ocg.getObject()['/Name']] = str(ocg)
        # Delete the stack to reset
        del self.stack
        #Clean-Up Time!!!
        # Get the new root of the PDF
        #realRoot = self.getObject(newRootRef)
        # Get the new pages tree root and its ID Number
        #tmpPages = realRoot[PyPDF2.generic.NameObject("/Pages")]
        #print('tmpPages', tmpPages)
        #newIdNumForPages = 1 + self._objects.index(tmpPages)
        # Make an IndirectObject just for the new Pages
        #self._pages = PyPDF2.generic.IndirectObject(newIdNumForPages, 0, self)
        # Bump up the info's reference b/c the old page's tree was bumped off
        #self._info = newInfoRef
        #print('newInfoRef', newInfoRef, '=>', newInfoRef.getObject())

    def myAddPage(self, page):
        print('myAddPage', page)
        print('myAddPage', page[PyPDF2.generic.NameObject("/Resources")])
        self.addPage(page)            
    
def LINE():
    return sys._getframe(1).f_lineno

class PDFGeneratorA4(FrozenClass):
    def __init__(self):
        super(PDFGeneratorA4, self).__init__()
        self.generateA4 = None
        self.generateCommun = PDFGenerator()
        self.pageA4Basename = None
        self.generateSheetTrimming = None
        self.generateScanningOrder = None
        self.generatePagesOrientation = None
        self.generateMaskingTapeTxt = None
        self.generateMaskingTapeColor = None
        self.orderedPageList = None
        self.needSheetW = None
        self.needSheetH = None
        self.deltaW = None
        self.deltaH = None
        self.pageNumberTxt = None
        self.pageNumberColor = None
        self.pageNumberSize = None
        self.pageNumberOpacity = None
        self.xrefOCGA4In = None
        self.xrefOCGA4Out = None
        self.canvasClipRectsDico = None
        self.canvasShowRectsDico = None
        self.patternShowRectsDico = None
        self.patternClipRectsDico = None

    @property
    def fullPatternRect(self): return self.generateCommun.fullPatternRect
    @property
    def fullPatternSvgPerLayer(self): return self.generateCommun.fullPatternSvgPerLayer
    @property
    def generateHiddenLayers(self): return self.generateCommun.generateHiddenLayers
    @property
    def xrefOCG(self): return self.generateCommun.xrefOCG
    def xrefOCG(self, v): self.generateCommun.xrefOCG(v)
    
    @property
    def generateA4(self): return self.__generateA4
    @generateA4.setter
    def generateA4(self, v):
        assert v is None or isinstance(v, bool), "assert false generateA4"
        self.__generateA4 = v

    @property
    def pageA4Basename(self): return self.__pageA4Basename
    @pageA4Basename.setter
    def pageA4Basename(self, v):
        assert v is None or isinstance(v, str), "assert false pageA4Basename"
        self.__pageA4Basename = v
        
    @property
    def generateSheetTrimming(self): return self.__generateSheetTrimming
    @generateSheetTrimming.setter
    def generateSheetTrimming(self, v):
        assert v is None or isinstance(v, CanvasOnSheet), "assert false generateSheetTrimming"
        self.__generateSheetTrimming = v

    @property
    def generateScanningOrder(self): return self.__generateScanningOrder
    @generateScanningOrder.setter
    def generateScanningOrder(self, v):
        assert v is None or isinstance(v, PagesOrdering), "assert false generateScanningOrder"
        self.__generateScanningOrder = v

    @property
    def generatePagesOrientation(self): return self.__generatePagesOrientation
    @generatePagesOrientation.setter
    def generatePagesOrientation(self, v):
        assert v is None or isinstance(v, PagesOrientation), "assert false generatePagesOrientation"
        self.__generatePagesOrientation = v
        
    @property
    def generateMaskingTapeTxt(self): return self.__generateMaskingTapeTxt
    @generateMaskingTapeTxt.setter
    def generateMaskingTapeTxt(self, v):
        assert v is None or isinstance(v, TapeMarks), "assert false generateMaskingTapeTxt"
        self.__generateMaskingTapeTxt = v

    @property
    def generateMaskingTapeColor(self): return self.__generateMaskingTapeColor
    @generateMaskingTapeColor.setter
    def generateMaskingTapeColor(self, v):
        assert v is None or isinstance(v, list), "assert false generateMaskingTapeColor"
        self.__generateMaskingTapeColor = v

    @property
    def pageNumberTxt(self): return self.__pageNumberTxt
    @pageNumberTxt.setter
    def pageNumberTxt(self, v):
        assert v is None or isinstance(v, PagesNumbering), "assert false pageNumberTxt"
        self.__pageNumberTxt = v

    @property
    def pageNumberOpacity(self): return self.__pageNumberOpacity
    @pageNumberOpacity.setter
    def pageNumberOpacity(self, v):
        assert v is None or isinstance(v, str), "assert false pageNumberOpacity"
        self.__pageNumberOpacity = v
        
    @property
    def canvasClipRectsDico(self): return self.__canvasClipRectsDico
    @canvasClipRectsDico.setter
    def canvasClipRectsDico(self, v):
        assert v is None or isinstance(v, dict), "assert false canvasClipRectsDico"
        self.__canvasClipRectsDico = v

    @property
    def canvasShowRectsDico(self): return self.__canvasShowRectsDico
    @canvasShowRectsDico.setter
    def canvasShowRectsDico(self, v):
        assert v is None or isinstance(v, dict), "assert false canvasShowRectsDico"
        self.__canvasShowRectsDico = v

    @property
    def patternShowRectsDico(self): return self.__patternShowRectsDico
    @patternShowRectsDico.setter
    def patternShowRectsDico(self, v):
        assert v is None or isinstance(v, dict), "assert false patternShowRectsDico"
        self.__patternShowRectsDico = v

    @property
    def patternClipRectsDico(self): return self.__patternClipRectsDico
    @patternClipRectsDico.setter
    def patternClipRectsDico(self, v):
        assert v is None or isinstance(v, dict), "assert false patternClipRectsDico"
        self.__patternClipRectsDico = v

    @abstractmethod
    def generateCanvas(self):
        pass
    @abstractmethod
    def getCanvasFile(self):
        pass

    def rect_top(self, r, d):
        return fitz.Rect(r.x0, r.y0 - d, r.x1, r.y0)
    def rect_down(self, r, d):
        return fitz.Rect(r.x0, r.y1, r.x1, r.y1 + d)
    def rect_left(self, r, d):
        return fitz.Rect(r.x0 - d, r.y0, r.x0, r.y1)
    def rect_right(self, r, d):
        return fitz.Rect(r.x1, r.y0, r.x1 + d, r.y1)
    def rect_topright(self, r, dw, dh):
        return fitz.Rect(r.x1, r.y0 - dh, r.x1 + dw, r.y0)
    def rect_topleft(self, r, dw, dh):
        return fitz.Rect(r.x0 - dw, r.y0 - dh, r.x0, r.y0)
    def rect_downright(self, r, dw, dh):
        return fitz.Rect(r.x1, r.y1, r.x1 + dw, r.y1 + dh)
    def rect_downleft(self, r, dw, dh):
        return fitz.Rect(r.x0 - dw, r.y1, r.x0, r.y1 + dh)

    def getCanvasRectAndNbSheetWH(self):
        canvasdoc = fitz.open(self.canvasFile)
        canvasdoc = canvasdoc.convert_to_pdf()
        canvasdoc = fitz.open("pdf", canvasdoc)
        canvasrect = canvasdoc.load_page(0).rect
        self.needSheetW = math.ceil(self.fullPatternRect.width / canvasrect.width)
        self.needSheetH = math.ceil(self.fullPatternRect.height / canvasrect.height)
        canvasdoc.close()
        #print('getCanvasRectAndNbSheetWH', canvasrect)
        return canvasrect

    def getOrderedPages(self):
        print('Page order', self.generateScanningOrder)
        pagesList = list()
        if self.generateScanningOrder == PagesOrdering.LEFTRIGHT:
            for h in range(self.needSheetH):
                for w in range(self.needSheetW):
                    pagesList.append((h,w))
        else:
            for w in range(self.needSheetW):
                for h in range(self.needSheetH):
                    pagesList.append((h,w))    
        return pagesList

    def generateAllBlankPages(self, doc):               
        print('Page orientation', self.generatePagesOrientation)
        for p in range(len(self.orderedPageList)):
            page = doc.new_page(-1)
            if self.generatePagesOrientation == PagesOrientation.LANDSCAPE:
                rotW = page.rect.width
                rotH = page.rect.height
                doc.delete_page(-1)
                page = doc.new_page(-1, width = rotH, height = rotW)
        return page.rect
    
    def generateOneOCGperLayer(self, doc):
        xrefOCG = dict()                   
        for k in self.fullPatternSvgPerLayer['LayersFilenames']: 
            if self.generateHiddenLayers or self.fullPatternSvgPerLayer['LayersFilenames'][k]['display'] == 'display':
                xrefOCG[k] = doc.add_ocg('%s'%k)
        return xrefOCG

    def generateOnePagePattern(self, idwh):
        docOnePage = dict()
        docOnePage[idwh] = fitz.open()
        self.xrefOCGA4In = docOnePage[idwh].add_ocg('A4CanvasIn', on=True)
        self.xrefOCGA4Out = docOnePage[idwh].add_ocg('A4CanvasOut')
        docOnePage[idwh].set_ocmd(xref=0, ocgs=[self.xrefOCGA4In,self.xrefOCGA4Out], policy="AnyOn", ve=None)
        self.xrefOCG = self.generateOneOCGperLayer(docOnePage[idwh]) 
        onepage = docOnePage[idwh].new_page(-1)
        if self.generatePagesOrientation == PagesOrientation.LANDSCAPE:
            rotW = onepage.rect.width
            rotH = onepage.rect.height
            docOnePage[idwh].delete_page(-1)
            onepage = docOnePage[idwh].new_page(-1, width = rotH, height = rotW) 
        res = onepage.rect
        docOnePage[idwh].save(self.pageA4Basename + '_%s.pdf'%idwh)
        docOnePage[idwh].close()
        return res

    def getAreasCondition(self):
        res = dict()
        for h,w in self.orderedPageList:
            idwh = 'L%sC%s'%(h,w)
            res[idwh] = dict()
            res[idwh][Areas.C] = True
            res[idwh][Areas.T] = h > 0 and self.generateSheetTrimming == CanvasOnSheet.CENTERED
            res[idwh][Areas.D] = h < self.needSheetH - 1
            res[idwh][Areas.R] = w < self.needSheetW - 1
            res[idwh][Areas.L] = w > 0 and self.generateSheetTrimming == CanvasOnSheet.CENTERED
            res[idwh][Areas.TL] = res[idwh][Areas.T] and res[idwh][Areas.L]
            res[idwh][Areas.TR] = res[idwh][Areas.T] and res[idwh][Areas.R]
            res[idwh][Areas.DL] = res[idwh][Areas.D] and res[idwh][Areas.L]
            res[idwh][Areas.DR] = res[idwh][Areas.D] and res[idwh][Areas.R]
        return res
    
    def buildRectDicos(self, a4rect, canvasrect):
        
        if self.generateSheetTrimming == CanvasOnSheet.CENTERED:
            deltaW = (a4rect.width-canvasrect.width)/2.0
            deltaH = (a4rect.height-canvasrect.height)/2.0
            print('==> Margin around the active area (Pixel units 72 PPI) left/right = %s up/down = %s'%(deltaW, deltaH))
        else:
            deltaW = (a4rect.width-canvasrect.width)
            deltaH = (a4rect.height-canvasrect.height)
            print('==> Margin around the active area (Pixel units 72 PPI) right = %s down = %s'%(deltaW, deltaH))
        self.deltaW, self.deltaH = deltaW, deltaH
        
        self.canvasClipRectsDico = dict()
        for e in Areas: self.canvasClipRectsDico[e] = None
        self.canvasClipRectsDico[Areas.C] = canvasrect
        self.canvasClipRectsDico[Areas.R] = fitz.Rect(0, 0, deltaW, canvasrect.height)
        self.canvasClipRectsDico[Areas.D] = fitz.Rect(0, 0, canvasrect.width, deltaH)
        self.canvasClipRectsDico[Areas.DR] = fitz.Rect(0, 0, deltaW, deltaH)
        if self.generateSheetTrimming != CanvasOnSheet.PIRATES:         
            self.canvasClipRectsDico[Areas.L] = fitz.Rect(canvasrect.width-deltaW, 0, canvasrect.width, canvasrect.height)
            self.canvasClipRectsDico[Areas.T] = fitz.Rect(0, canvasrect.height-deltaH, canvasrect.width, canvasrect.height)
            self.canvasClipRectsDico[Areas.TR] = fitz.Rect(0, canvasrect.height-deltaH, deltaW, canvasrect.height)
            self.canvasClipRectsDico[Areas.TL] = fitz.Rect(canvasrect.width-deltaW, canvasrect.height-deltaH, canvasrect.width, canvasrect.height)
            self.canvasClipRectsDico[Areas.DL] = fitz.Rect(canvasrect.width-deltaW, 0, canvasrect.width, deltaH)
        
        self.canvasShowRectsDico = dict()
        self.patternShowRectsDico = dict()
        self.patternClipRectsDico = dict()

        for h,w in self.orderedPageList:
            idwh = 'L%sC%s'%(h,w)

            condL = w > 0 and self.generateSheetTrimming == CanvasOnSheet.CENTERED
            condR = w < self.needSheetW - 1
            condT = h > 0 and self.generateSheetTrimming == CanvasOnSheet.CENTERED
            condD = h < self.needSheetH - 1
            
            # Canvas show
            self.canvasShowRectsDico[idwh] = dict()
            for e in Areas: self.canvasShowRectsDico[idwh][e] = None
            
            if self.generateSheetTrimming == CanvasOnSheet.CENTERED:
                self.canvasShowRectsDico[idwh][Areas.C] = fitz.Rect(canvasrect.x0+deltaW, canvasrect.y0+deltaH, canvasrect.x1+deltaW, canvasrect.y1+deltaH)
            else:
                self.canvasShowRectsDico[idwh][Areas.C] = fitz.Rect(canvasrect.x0+0, canvasrect.y0+0, canvasrect.x1+0, canvasrect.y1+0)
            self.canvasShowRectsDico[idwh][Areas.R] = self.rect_right(self.canvasShowRectsDico[idwh][Areas.C], deltaW)  
            self.canvasShowRectsDico[idwh][Areas.D] = self.rect_down(self.canvasShowRectsDico[idwh][Areas.C], deltaH) 
            self.canvasShowRectsDico[idwh][Areas.DR] = self.rect_downright(self.canvasShowRectsDico[idwh][Areas.C], deltaW, deltaH)            
            if self.generateSheetTrimming != CanvasOnSheet.PIRATES:
                self.canvasShowRectsDico[idwh][Areas.L] = self.rect_left(self.canvasShowRectsDico[idwh][Areas.C], deltaW)
                self.canvasShowRectsDico[idwh][Areas.T] = self.rect_top(self.canvasShowRectsDico[idwh][Areas.C], deltaH)
                self.canvasShowRectsDico[idwh][Areas.TR] = self.rect_topright(self.canvasShowRectsDico[idwh][Areas.C], deltaW, deltaH)
                self.canvasShowRectsDico[idwh][Areas.TL] = self.rect_topleft(self.canvasShowRectsDico[idwh][Areas.C], deltaW, deltaH)
                self.canvasShowRectsDico[idwh][Areas.DL] = self.rect_downleft(self.canvasShowRectsDico[idwh][Areas.C], deltaW, deltaH)
            
            # Pattern show
            self.patternShowRectsDico[idwh] = dict()
            for e in Areas: self.patternShowRectsDico[idwh][e] = None

            if h == self.needSheetH-1 and w == self.needSheetW-1 : # last page
                cutH = self.needSheetH*canvasrect.height - self.fullPatternRect.height
                cutW = self.needSheetW*canvasrect.width - self.fullPatternRect.width
                if self.generateSheetTrimming == CanvasOnSheet.CENTERED: self.patternShowRectsDico[idwh][Areas.C] = fitz.Rect(canvasrect.x0+deltaW, canvasrect.y0+deltaH, canvasrect.x1+deltaW-cutW, canvasrect.y1+deltaH-cutH)
                else:                                                    self.patternShowRectsDico[idwh][Areas.C] = fitz.Rect(canvasrect.x0+0, canvasrect.y0+0, canvasrect.x1+0-cutW, canvasrect.y1+0-cutH)
            elif h == self.needSheetH-1: # last line
                cutH = self.needSheetH*canvasrect.height - self.fullPatternRect.height
                if self.generateSheetTrimming == CanvasOnSheet.CENTERED: self.patternShowRectsDico[idwh][Areas.C] = fitz.Rect(canvasrect.x0+deltaW, canvasrect.y0+deltaH, canvasrect.x1+deltaW, canvasrect.y1+deltaH-cutH)
                else:                                                    self.patternShowRectsDico[idwh][Areas.C] = fitz.Rect(canvasrect.x0+0, canvasrect.y0+0, canvasrect.x1+0, canvasrect.y1+0-cutH)
            elif w == self.needSheetW-1: # last col
                cutW = self.needSheetW*canvasrect.width - self.fullPatternRect.width
                if self.generateSheetTrimming == CanvasOnSheet.CENTERED: self.patternShowRectsDico[idwh][Areas.C] = fitz.Rect(canvasrect.x0+deltaW, canvasrect.y0+deltaH, canvasrect.x1+deltaW-cutW, canvasrect.y1+deltaH)
                else:                                                    self.patternShowRectsDico[idwh][Areas.C] = fitz.Rect(canvasrect.x0+0, canvasrect.y0+0, canvasrect.x1+0-cutW, canvasrect.y1+0)
            else: self.patternShowRectsDico[idwh][Areas.C] = self.canvasShowRectsDico[idwh][Areas.C]
            self.patternShowRectsDico[idwh][Areas.R] = self.rect_right(self.patternShowRectsDico[idwh][Areas.C], deltaW)  
            self.patternShowRectsDico[idwh][Areas.D] = self.rect_down(self.patternShowRectsDico[idwh][Areas.C], deltaH)  
            self.patternShowRectsDico[idwh][Areas.DR] = self.rect_downright(self.patternShowRectsDico[idwh][Areas.C], deltaW, deltaH) 
            if self.generateSheetTrimming != CanvasOnSheet.PIRATES:
                self.patternShowRectsDico[idwh][Areas.L] = self.rect_left(self.patternShowRectsDico[idwh][Areas.C], deltaW)
                self.patternShowRectsDico[idwh][Areas.T] = self.rect_top(self.patternShowRectsDico[idwh][Areas.C], deltaH) 
                self.patternShowRectsDico[idwh][Areas.TL] = self.rect_topleft(self.patternShowRectsDico[idwh][Areas.C], deltaW, deltaH) 
                self.patternShowRectsDico[idwh][Areas.TR] = self.rect_topright(self.patternShowRectsDico[idwh][Areas.C], deltaW, deltaH) 
                self.patternShowRectsDico[idwh][Areas.DL] = self.rect_downleft(self.patternShowRectsDico[idwh][Areas.C], deltaW, deltaH) 
                
            # Pattern clip
            self.patternClipRectsDico[idwh] = dict()
            for e in Areas: self.patternClipRectsDico[idwh][e] = None

            l = w*canvasrect.width
            r = (w+1)*canvasrect.width
            maxw = self.fullPatternRect.width
            t = h*canvasrect.height
            b = (h+1)*canvasrect.height
            maxh = self.fullPatternRect.height

            self.patternClipRectsDico[idwh][Areas.C] = fitz.Rect(l, t, min(r,maxw), min(b,maxh))                    
            if condR:
                self.patternClipRectsDico[idwh][Areas.R] = fitz.Rect(r, t, min(r+deltaW,maxw), min(b,maxh))                    
            if condD:
                self.patternClipRectsDico[idwh][Areas.D] = fitz.Rect(l, b, min(r,maxw), min(b+deltaH,maxh))                    
            if condL:
                self.patternClipRectsDico[idwh][Areas.L] = fitz.Rect(l-deltaW, t, l, min(b,maxh))                    
            if condT:
                self.patternClipRectsDico[idwh][Areas.T] = fitz.Rect(l, t-deltaH, min(r,maxw), t)                 
            if condT and condR:
                self.patternClipRectsDico[idwh][Areas.TR] = fitz.Rect(r, t-deltaH, min(r+deltaW,maxw), t)                 
            if condT and condL:
                self.patternClipRectsDico[idwh][Areas.TL] = fitz.Rect(l-deltaW, t-deltaH, l, t)                 
            if condD and condR:
                self.patternClipRectsDico[idwh][Areas.DR] = fitz.Rect(r, b, min(r+deltaW,maxw), min(b+deltaH,maxh))                 
            if condD and condL:
                self.patternClipRectsDico[idwh][Areas.DL] = fitz.Rect(l-deltaW, b, l, min(b+deltaH,maxh))        
    
    def getShownLayersDocDico(self):
        res = dict()
        for k in self.fullPatternSvgPerLayer['LayersFilenames']: 
            if self.generateHiddenLayers or self.fullPatternSvgPerLayer['LayersFilenames'][k]['display'] == 'display':
                res[k] = dict()
                res[k]['FitzPdfFilename'] = self.fullPatternSvgPerLayer['LayersFilenames'][k]['fitzpdf']
                tempsvg = fitz.open(res[k]['FitzPdfFilename'])
                pdfbytes = tempsvg.convert_to_pdf()
                tempsvg.close()
                res[k]['FitzDocument'] = fitz.open("pdf", pdfbytes) 
        return res

    def generatePattern(self, shownLayersDocDico, areasCondition):
        print('Generate pattern')
        for h,w in self.orderedPageList:
            idwh = 'L%sC%s'%(h,w)
    
            b = open(self.pageA4Basename + '_%s.pdf'%idwh, "rb").read()
            with fitz.open("pdf", b) as doci:
                page0 = doci.load_page(0)
                for k in shownLayersDocDico: 
                    for area in Areas:
                        if areasCondition[idwh][area]:
                            page0.show_pdf_page(self.patternShowRectsDico[idwh][area], shownLayersDocDico[k]['FitzDocument'], 0, oc=self.xrefOCG[k], clip=self.patternClipRectsDico[idwh][area])
                            shape = page0.new_shape()
                            shape.draw_rect(self.canvasShowRectsDico[idwh][area])
                            shape.finish(fill = (0.95,0.95,0.95), fill_opacity=0.1 if area == Areas.C else 0.3)
                            shape.commit()
                            doci.save(self.pageA4Basename + '_%s.pdf'%idwh)

    def generatePageNumber(self):
        if self.pageNumberTxt == PagesNumbering.NO: return
        print('Generate page number')

        myfont = fitz.Font(fontname='impact', fontfile=resource_path('impact.ttf'), fontbuffer=None, script=0, language=None, 
                           ordering=-1, is_bold=0, is_italic=0, is_serif=0)
             
        for hwi,hw in enumerate(self.orderedPageList):
            h,w = hw
            idwh = 'L%sC%s'%(h,w)
            canvasrect = self.canvasClipRectsDico[Areas.C]
            
            b = open(self.pageA4Basename + '_%s.pdf'%idwh, "rb").read()
            with fitz.open("pdf", b) as doci:
                pagei = doci.load_page(0)
                pgtxt = idwh if self.pageNumberTxt == PagesNumbering.LXCY else '%s'%hwi
                pgtxtwidth = myfont.text_length(pgtxt, int(self.pageNumberSize))
                pgtxtHmin = int(self.pageNumberSize) * min([myfont.glyph_bbox(ord(x)).y0 for x in pgtxt])
                pgtxtHmax = int(self.pageNumberSize) * max([myfont.glyph_bbox(ord(x)).y1 for x in pgtxt])
                pgtxtheight = pgtxtHmax-pgtxtHmin
                rgb = [x/255.0 for x in self.pageNumberColor[:-1]]
                
                x = (0 if self.generateSheetTrimming == CanvasOnSheet.PIRATES else self.deltaW) + canvasrect.width/2.0 - pgtxtwidth/2.0 
                y = (0 if self.generateSheetTrimming == CanvasOnSheet.PIRATES else self.deltaH) + canvasrect.height/2.0 - pgtxtheight/2.0 
                
                '''pivot = fitz.Point(rect.x0, rect.y0 + rect.height/2) #middle of left side
                matrix = fitz.Matrix(textwidth/rect.width, 1.0)
                r2 = page.insert_textbox(token.rect, f'{word}', color=(1,0,0), morph=(pivot, matrix))'''
                pagei.insert_textbox(fitz.Rect(x,y,x+pgtxtwidth,y+pgtxtheight), pgtxt, fontsize=int(self.pageNumberSize), 
                                    fontname='impact', fontfile=resource_path('impact.ttf'), color=rgb, 
                                    fill=rgb, render_mode=0, border_width=1, encoding=fitz.TEXT_ENCODING_LATIN, 
                                    expandtabs=8, align=fitz.TEXT_ALIGN_LEFT, rotate=0, morph=None, 
                                    stroke_opacity=1, fill_opacity=int(self.pageNumberOpacity)/100.0, oc=self.xrefOCGA4In, overlay=True)
    
                doci.save(self.pageA4Basename + '_%s.pdf'%idwh)
            
    def generateWatermarkA4(self):
        print('Generate watermarking A4')
        for hwi,hw in enumerate(self.orderedPageList):
            h,w = hw
            idwh = 'L%sC%s'%(h,w)
            b = open(self.pageA4Basename + '_%s.pdf'%idwh, "rb").read()
            with fitz.open("pdf", b) as doci:
                pagei = doci.load_page(0)
                self.generateCommun.generateWatermark(doci, pagei, self.canvasClipRectsDico[Areas.C], (self.deltaW,self.deltaH) if self.generateSheetTrimming == CanvasOnSheet.CENTERED else None)
                doci.save(self.pageA4Basename + '_%s.pdf'%idwh)

    def runA4(self, outputfilenameA4):
        
        print('-------------- G E N E R A T E --- A 4 -----------------\n', outputfilenameA4 if self.generateA4 else 'N/A')
        if self.generateA4:

            canvasrect = self.getCanvasRectAndNbSheetWH()
            self.orderedPageList = self.getOrderedPages()
            
            try:
                for h,w in self.orderedPageList:
                    idwh = 'L%sC%s'%(h,w)
                    a4rect = self.generateOnePagePattern(idwh)
                    if self.orderedPageList.index((h,w)) == 0:
                        print('Full size pattern (Pixel units 72 PPI) %sx%s'%(self.fullPatternRect.width, self.fullPatternRect.height))
                        print('A4 size (Pixel units 72 PPI) %sx%s'%(a4rect.width, a4rect.height))
                        print('Canvas size (Pixel units 72 PPI) %sx%s'%(canvasrect.width, canvasrect.height))
                        if canvasrect.width > a4rect.width or canvasrect.height > a4rect.height:
                            print('==> Please choose a canvas smaller than A4 format')                
                            return 
                        print('==> Need %s (%sx%s) sheets'%(self.needSheetW*self.needSheetH, self.needSheetW, self.needSheetH))
                        self.buildRectDicos(a4rect, canvasrect)
            except Exception as e:
                print('Something went wrong during blank pages generation')
                print('Exception:', e)
                                
            try:
                shownLayersDocDico = self.getShownLayersDocDico()
                areasCondition = self.getAreasCondition()
                self.generatePattern(shownLayersDocDico, areasCondition)
            except Exception as e:
                print('Something went wrong during pattern generation')
                print('Exception:', e)

            try:
                self.generateCanvas()
            except Exception as e:
                print('Something went wrong during canvas generation')
                print('Exception:', e)
            
            try:
                self.generatePageNumber()
            except Exception as e:
                print('Something went wrong during page number generation')
                print('Exception:', e)

            try:
                self.generateWatermarkA4()
            except Exception as e:
                print('Something went wrong during watermarking generation')
                print('Exception:', e)
                
            try:
                print('Merge A4')
                
                
                pdfMerger = PdfFileMerger()
                with open(outputfilenameA4, 'wb') as pdfWB:
                    for hw in self.orderedPageList:
                        h,w = hw
                        idwh = 'L%sC%s'%(h,w)
                        with open(self.pageA4Basename + '_%s.pdf'%idwh, 'rb') as pdfRB:
                            if h==0 and w==0:
                                pdfReader = PdfFileReader(pdfRB)
                                pdfMerger.output.cloneReaderDocumentRoot(pdfReader)
                                print(pdfReader.trailer["/Root"].getObject().keys())
                                print(pdfReader.trailer["/Root"].getObject()["/OCProperties"])
                                print(pdfMerger.output._root_object)
                            pdfMerger.append(self.pageA4Basename + '_%s.pdf'%idwh)
                    pdfMerger.write(pdfWB)   
                    print(pdfMerger.output._root.getObject().keys())
                    #ocProperties = self._root.getObject()["/OCProperties"]
                    #ocgs = ocProperties['/OCGs']   


            except Exception as e:
                print('Something went wrong during A4 pages merging')
                print('Exception:', e)

            try:
                if self.generateCommun.generateMergeFilename is not None:
                    if not os.path.isfile(self.generateCommun.generateMergeFilename):
                        mergedoc = fitz.open()
                        doc = fitz.open(outputfilenameA4)
                        mergedoc.insertPDF(doc)
                        doc.close()
                        mergedoc.save(self.generateCommun.generateMergeFilename)
                        mergedoc.close()
                    else:
                        ready = False
                        while not ready:
                            try:
                                mergedoc = fitz.open(self.generateCommun.generateMergeFilename) 
                                ready = True
                            except: pass
                        doc = fitz.open(outputfilenameA4)
                        mergedoc.insertPDF(doc)
                        doc.close()
                        mergedoc.saveIncr()
                        mergedoc.close()
            except: print('runA4 merge issue %s'%self.generateCommun.generateMergeFilename)
            
if __name__ == '__main__':
    pass
