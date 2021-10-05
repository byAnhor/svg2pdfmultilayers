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
from enum import Enum
from abc import abstractmethod
from frozenclass import FrozenClass

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class CanvasOnSheet(Enum):
     CENTERED = 0
     PIRATES = 1
class TapeMarks(Enum):
     NO = 0
     LXCY = 1
     AA = 2
     @classmethod
     def fromStr(cls, s):
         if s == "No" : return cls.NO
         if s == "LxCy" : return cls.LXCY
         if s == "A-A" : return cls.AA
         return None
class PagesOrdering(Enum):
     LEFTRIGHT = 0
     TOPDOWN = 1
class PagesOrientation(Enum):
     PORTRAIT = 0
     LANDSCAPE = 1
class PagesNumbering(Enum):
     NO = 0
     LXCY = 1
     NUMBER = 2
     @classmethod
     def fromStr(cls, s):
         if s == "No" : return cls.NO
         if s == "LxCy" : return cls.LXCY
         if s == "Page number" : return cls.NUMBER
         return None
class Areas(Enum):
    C = 0
    T = 1
    D = 2
    L = 3
    R = 4
    TL = 5
    TR = 6
    DL = 7
    DR = 8   
     

class PDFGenerator(FrozenClass):
    def __init__(self):
        self.maingui = None
        self.tempPath = None    
        self.fullPatternSvg = None
        self.fullPatternRect = None
        self.generateA0 = None
        self.generateA4 = None
        self.generateHiddenLayers = None
        self.generateSheetTrimming = None
        self.generateScanningOrder = None
        self.generatePagesOrientation = None
        self.generateMaskingTapeTxt = None
        self.generateMaskingTapeColor = None
        self.fullPatternSvgPerLayer = None
        self.pdfOutFilename = None
        self.generateMergeFilename = None

        self.orderedPageList = None
        self.needSheetW = None
        self.needSheetH = None
        self.pageNumberTxt = None
        self.pageNumberColor = None
        self.pageNumberSize = None
        self.pageNumberOpacity = None
        
        self.canvasClipRectsDico = None
        self.canvasShowRectsDico = None
        self.patternShowRectsDico = None
        self.patternClipRectsDico = None
        self.pageNumDico = None
        self.xrefOCG = None          
        self.xrefOCGA4In = None
        self.xrefOCGA4Out = None
        self.deltaW = None
        self.deltaH = None

        self._freeze()
        
        '''self.markercolortxt = (1,0,0)
        self.markerfillshape = (1,1,0.5)
        self.markercolorshape = (0,0,0)'''
    def __str__(self):
        return 'PDFGenerator\n    ' + ('\n    '.join("%s: %s" % item for item in vars(self).items()))
        
    @property
    def fullPatternSvg(self): return self.__fullPatternSvg
    @fullPatternSvg.setter
    def fullPatternSvg(self, v): 
        assert v is None or isinstance(v, str), "assert false fullPatternSvg"
        self.__fullPatternSvg = v

    @property
    def fullPatternRect(self): return self.__fullPatternRect
    @fullPatternRect.setter
    def fullPatternRect(self, v): 
        assert v is None or isinstance(v, fitz.Rect), "assert false fullPatternRect"
        self.__fullPatternRect = v

    @property
    def generateA0(self): return self.__generateA0
    @generateA0.setter
    def generateA0(self, v): 
        assert v is None or isinstance(v, bool), "assert false generateA0"
        self.__generateA0 = v

    @property
    def generateA4(self): return self.__generateA4
    @generateA4.setter
    def generateA4(self, v):
        assert v is None or isinstance(v, bool), "assert false generateA4"
        self.__generateA4 = v

    @property
    def tempPath(self): return self.__tempPath
    @tempPath.setter
    def tempPath(self, v):
        assert v is None or isinstance(v, str), "assert false tempPath"
        self.__tempPath = v

    @property
    def generateHiddenLayers(self): return self.__generateHiddenLayers
    @generateHiddenLayers.setter
    def generateHiddenLayers(self, v):
        assert v is None or isinstance(v, bool), "assert false generateHiddenLayers"
        self.__generateHiddenLayers = v

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
    def fullPatternSvgPerLayer(self): return self.__fullPatternSvgPerLayer
    @fullPatternSvgPerLayer.setter
    def fullPatternSvgPerLayer(self, v):
        assert v is None or isinstance(v, dict), "assert false fullPatternSvgPerLayer"
        self.__fullPatternSvgPerLayer = v

    @property
    def pdfOutFilename(self): return self.__pdfOutFilename
    @pdfOutFilename.setter
    def pdfOutFilename(self, v):
        assert v is None or isinstance(v, str), "assert false pdfOutFilename"
        self.__pdfOutFilename = v

    @property
    def generateMergeFilename(self): return self.__generateMergeFilename
    @generateMergeFilename.setter
    def generateMergeFilename(self, v):
        assert v is None or isinstance(v, str), "assert false generateMergeFilename"
        self.__generateMergeFilename = v

    @property
    def orderedPageList(self): return self.__orderedPageList
    @orderedPageList.setter
    def orderedPageList(self, v):
        assert v is None or isinstance(v, list), "assert false orderedPageList"
        self.__orderedPageList = v

    @property
    def needSheetW(self): return self.__needSheetW
    @needSheetW.setter
    def needSheetW(self, v):
        assert v is None or isinstance(v, int), "assert false needSheetW"
        self.__needSheetW = v

    @property
    def needSheetH(self): return self.__needSheetH
    @needSheetH.setter
    def needSheetH(self, v):
        assert v is None or isinstance(v, int), "assert false needSheetH"
        self.__needSheetH = v

    @property
    def pageNumberTxt(self): return self.__pageNumberTxt
    @pageNumberTxt.setter
    def pageNumberTxt(self, v):
        assert v is None or isinstance(v, PagesNumbering), "assert false pageNumberTxt"
        self.__pageNumberTxt = v

    @property
    def pageNumberColor(self): return self.__pageNumberColor
    @pageNumberColor.setter
    def pageNumberColor(self, v):
        assert v is None or isinstance(v, list), "assert false pageNumberColor"
        self.__pageNumberColor = v

    @property
    def pageNumberSize(self): return self.__pageNumberSize
    @pageNumberSize.setter
    def pageNumberSize(self, v):
        assert v is None or isinstance(v, str), "assert false pageNumberSize"
        self.__pageNumberSize = v

    @property
    def pageNumberOpacity(self): return self.__pageNumberOpacity
    @pageNumberOpacity.setter
    def pageNumberOpacity(self, v):
        assert v is None or isinstance(v, str), "assert false pageNumberOpacity"
        self.__pageNumberOpacity = v

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
              
    def runA0(self, outputfilenameA0):
        
        print('-------------- G E N E R A T E --- A 0 -----------------', outputfilenameA0 if self.generateA0 else 'N/A')
        if self.generateA0:

            doc = fitz.open()  
            xrefOCG = dict()                   
            for k in self.fullPatternSvgPerLayer.keys(): 
                if self.generateHiddenLayers or "show_LAYER" in self.fullPatternSvgPerLayer[k]:
                    xrefOCG[k] = doc.add_ocg('%s'%k)
            doc.new_page(-1, width = self.fullPatternRect.width, height = self.fullPatternRect.height)
            doc.save(outputfilenameA0)
            doc.close()
    
            doc = fitz.open(outputfilenameA0)  
            page0 = doc.load_page(0)
            try:
                for k in self.fullPatternSvgPerLayer.keys(): 
                    if self.generateHiddenLayers or "show_LAYER" in self.fullPatternSvgPerLayer[k]:
                        curfilename = self.fullPatternSvgPerLayer[k].replace('.svg', '.fitz.pdf')
                        tempsvg = fitz.open(self.tempPath + curfilename)
                        pdfbytes = tempsvg.convert_to_pdf()
                        tempsvg.close()
                        tempsvg = fitz.open("pdf", pdfbytes) 
                        page0.show_pdf_page(self.fullPatternRect, tempsvg, 0, oc=xrefOCG[k])
                        tempsvg.close()
                        doc.saveIncr()
                    else: print('Hidden', k)
                doc.close()
            except: doc.close()
               
    def runA4(self, outputfilenameA4):
        
        print('-------------- G E N E R A T E --- A 4 -----------------', outputfilenameA4 if self.generateA4 else 'N/A')
        if self.generateA4:

            canvasrect = self.getCanvasRectAndNbSheetWH()
            self.orderedPageList = self.getOrderedPages()
            doc = fitz.open()
            self.xrefOCGA4In = doc.add_ocg('A4CanvasIn', on=True)
            self.xrefOCGA4Out = doc.add_ocg('A4CanvasOut')
            doc.set_ocmd(xref=0, ocgs=[self.xrefOCGA4In,self.xrefOCGA4Out], policy="AnyOn", ve=None)
            self.xrefOCG = self.generateOneOCGperLayer(doc) 
              
            a4rect = self.generateAllBlankPages(doc)               
            print('Full size pattern (Pixel units 72 PPI) %sx%s'%(self.fullPatternRect.width, self.fullPatternRect.height))
            print('A4 size (Pixel units 72 PPI) %sx%s'%(a4rect.width, a4rect.height))
            print('Canvas size (Pixel units 72 PPI) %sx%s'%(canvasrect.width, canvasrect.height))
            if canvasrect.width > a4rect.width or canvasrect.height > a4rect.height:
                print('==> Please choose a canvas smaller than A4 format')                
                return 
            print('==> Need %s (%sx%s) sheets'%(self.needSheetW*self.needSheetH, self.needSheetW, self.needSheetH))
            self.buildRectDicos(a4rect, canvasrect)
            doc.save(outputfilenameA4)
            doc.close()
            
            doc = fitz.open(outputfilenameA4) 
            try:
                self.generatePattern(doc)
            except Exception as e:
                doc.close()
                print('Something went wrong during pattern generation')
                print('Exception:', e)

            doc = fitz.open(outputfilenameA4) 
            try:
                self.generateCanvas(doc)
            except Exception as e:
                doc.close()
                print('Something went wrong during canvas generation')
                print('Exception:', e)
            
            doc = fitz.open(outputfilenameA4) 
            try:
                self.generatePageNumber(doc)
            except Exception as e:
                doc.close()
                print('Something went wrong during page number generation')
                print('Exception:', e)

            try:
                print('self.generateMergeFilename', self.generateMergeFilename)
                if self.generateMergeFilename is not None:
                    if not os.path.isfile(self.generateMergeFilename):
                        mergedoc = fitz.open()
                        doc = fitz.open(outputfilenameA4)
                        mergedoc.insertPDF(doc)
                        doc.close()
                        mergedoc.save(self.generateMergeFilename)
                        mergedoc.close()
                    else:
                        ready = False
                        while not ready:
                            try:
                                mergedoc = fitz.open(self.generateMergeFilename) 
                                ready = True
                            except: pass
                        doc = fitz.open(outputfilenameA4)
                        mergedoc.insertPDF(doc)
                        doc.close()
                        mergedoc.saveIncr()
                        mergedoc.close()
            except: print('runA4 merge issue %s'%self.generateMergeFilename)

    @abstractmethod
    def generateCanvas(self, doc):
        pass
    @abstractmethod
    def getCanvasFile(self):
        pass

    def generatePageNumber(self, doc):
        print('Generate page number')
                
        if self.pageNumberTxt == PagesNumbering.NO: return
        
        myfont = fitz.Font(fontname='impact', fontfile=resource_path('impact.ttf'), fontbuffer=None, script=0, language=None, 
                           ordering=-1, is_bold=0, is_italic=0, is_serif=0)
             
        for hwi,hw in enumerate(self.orderedPageList):
            h,w = hw
            idwh = 'L%sC%s'%(h,w)
            canvasrect = self.canvasClipRectsDico[Areas.C]
            pagei = doc.load_page(self.pageNumDico[idwh])
            pgtxt = idwh if self.pageNumberTxt == PagesNumbering.LXCY else '%s'%hwi
            pgtxtwidth = myfont.text_length(pgtxt, int(self.pageNumberSize))
            pgtxtHmin = int(self.pageNumberSize) * min([myfont.glyph_bbox(ord(x)).y0 for x in pgtxt])
            pgtxtHmax = int(self.pageNumberSize) * max([myfont.glyph_bbox(ord(x)).y1 for x in pgtxt])
            pgtxtheight = pgtxtHmax-pgtxtHmin
            print('pgtxtwidth', pgtxtwidth)
            print('pgtxtheight', pgtxtHmax, pgtxtHmin, pgtxtHmax-pgtxtHmin)
            rgb = [x/255.0 for x in self.pageNumberColor[:-1]]
            
            x = (0 if self.generateSheetTrimming == CanvasOnSheet.PIRATES else self.deltaW) + canvasrect.width/2.0 - pgtxtwidth/2.0 
            y = (0 if self.generateSheetTrimming == CanvasOnSheet.PIRATES else self.deltaH) + canvasrect.height/2.0 - pgtxtheight/2.0 
            
            '''pivot = fitz.Point(rect.x0, rect.y0 + rect.height/2) #middle of left side
            matrix = fitz.Matrix(textwidth/rect.width, 1.0)
            r2 = page.insertTextbox(token.rect, f'{word}', color=(1,0,0), morph=(pivot, matrix))'''
            print(canvasrect, fitz.Rect(200,200,200+pgtxtwidth,200+pgtxtheight))
            pagei.insertTextbox(fitz.Rect(x,y,x+pgtxtwidth,y+pgtxtheight), pgtxt, fontsize=int(self.pageNumberSize), 
                                fontname='impact', fontfile=resource_path('impact.ttf'), color=rgb, 
                                fill=rgb, render_mode=0, border_width=1, encoding=fitz.TEXT_ENCODING_LATIN, 
                                expandtabs=8, align=fitz.TEXT_ALIGN_LEFT, rotate=0, morph=None, 
                                stroke_opacity=1, fill_opacity=int(self.pageNumberOpacity)/100.0, oc=self.xrefOCGA4In, overlay=True)

        doc.saveIncr()
        doc.close()            	
            
    def getCanvasRectAndNbSheetWH(self):
        canvasdoc = fitz.open(self.getCanvasFile())
        canvasdoc = canvasdoc.convert_to_pdf()
        canvasdoc = fitz.open("pdf", canvasdoc)
        canvasrect = canvasdoc.load_page(0).rect
        self.needSheetW = math.ceil(self.fullPatternRect.width / canvasrect.width)
        self.needSheetH = math.ceil(self.fullPatternRect.height / canvasrect.height)
        canvasdoc.close()
        print('getCanvasRectAndNbSheetWH', canvasrect)
        return canvasrect

    def generatePattern(self, doc):
        for k in self.fullPatternSvgPerLayer.keys(): 
            if self.generateHiddenLayers or "show_LAYER" in self.fullPatternSvgPerLayer[k]:
                curfilename = self.fullPatternSvgPerLayer[k].replace('.svg', '.fitz.pdf')
                tempsvg = fitz.open(self.tempPath + curfilename)
                pdfbytes = tempsvg.convert_to_pdf()
                tempsvg.close()
                tempsvg = fitz.open("pdf", pdfbytes) 
                print('Generate the layer %s on each page = central panel + (right/left/down/up) if existing'%k)
                for h,w in self.orderedPageList:
                    idwh = 'L%sC%s'%(h,w)
                    curPage = self.pageNumDico[idwh] 
                    pagei = doc.load_page(curPage)
                    
                    conddico = dict()
                    conddico[Areas.C] = True
                    conddico[Areas.T] = h > 0 and self.generateSheetTrimming == CanvasOnSheet.CENTERED
                    conddico[Areas.D] = h < self.needSheetH - 1
                    conddico[Areas.R] = w < self.needSheetW - 1
                    conddico[Areas.L] = w > 0 and self.generateSheetTrimming == CanvasOnSheet.CENTERED
                    conddico[Areas.TL] = conddico[Areas.T] and conddico[Areas.L]
                    conddico[Areas.TR] = conddico[Areas.T] and conddico[Areas.R]
                    conddico[Areas.DL] = conddico[Areas.D] and conddico[Areas.L]
                    conddico[Areas.DR] = conddico[Areas.D] and conddico[Areas.R]

                    for area in Areas:
                        if conddico[area]:
                            try:
                                pagei.show_pdf_page(self.patternShowRectsDico[idwh][area], tempsvg, 0, oc=self.xrefOCG[k], clip=self.patternClipRectsDico[idwh][area])
                                shape = pagei.new_shape()
                                shape.draw_rect(self.canvasShowRectsDico[idwh][area])
                                shape.finish(fill = (0.95,0.95,0.95), fill_opacity=0.1 if area == Areas.C else 0.3)
                                shape.commit()
                            except Exception as e: print('Warning : Cannot add %s margin to %s, %s'%(area, idwh, e))

                tempsvg.close()
                doc.saveIncr()
        doc.close()
                   
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
        
    def generateOneOCGperLayer(self, doc):
        xrefOCG = dict()                   
        print('Generate hidden layers', self.generateHiddenLayers)
        for k in self.fullPatternSvgPerLayer.keys(): 
            if self.generateHiddenLayers or "show_LAYER" in self.fullPatternSvgPerLayer[k]:
                print(k + ' => ' + str(self.fullPatternSvgPerLayer[k]))
                xrefOCG[k] = doc.add_ocg('%s'%k)
        return xrefOCG
        
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
        self.pageNumDico = dict()
        for h,w in self.orderedPageList:
            idwh = 'L%sC%s'%(h,w)
            self.pageNumDico[idwh] = len(self.pageNumDico.keys())
    
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
         
    def run(self):
        
        try:     
            pdfOutFilenameA0 = self.pdfOutFilename.replace('.pdf', '.A0.pdf')
            self.runA0(pdfOutFilenameA0)
        except Exception as e:  print('Except : run A0', e)
        try:     
            self.runA4(self.pdfOutFilename.replace('.pdf', '.A4.pdf'))
        except Exception as e:  print('Except : run A4', e)
        
        print('Done !')
        

if __name__ == '__main__':
    x = PDFGenerator() 
    print(x)
    print(x.generateA0)
    PDFGenerator.generateA0 = True
    print(x)
