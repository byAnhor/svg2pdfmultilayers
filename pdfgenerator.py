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
from frozenclass import FrozenClass
from ressourcespath import resource_path
from enums import CanvasOnSheet



class PDFGenerator(FrozenClass):
    def __init__(self):
        self.fullPatternSvg = None
        self.fullPatternRect = None
        self.fullPatternSvgCSSFlatten = None
        self.generateHiddenLayers = None
        self.fullPatternSvgPerLayer = None
        self.pdfOutFilename = None
        self.generateMergeFilename = None
        
        self.watermark = None
        self.watermarkOpacity = None
        self.macadress = None

        self.canvasShowRectsDico = None
        self.patternShowRectsDico = None
        self.patternClipRectsDico = None
        self.pageNumDico = None
        
        self.myfont = fitz.Font(fontname='impact', fontfile=resource_path('impact.ttf'), fontbuffer=None, script=0, language=None, 
                                ordering=-1, is_bold=0, is_italic=0, is_serif=0)

        self._freeze()
        
    def __str__(self):
        return 'PDFGenerator\n    ' + ('\n    '.join("%s: %s" % item for item in vars(self).items()))
        
    @property
    def fullPatternSvg(self): return self.__fullPatternSvg
    @fullPatternSvg.setter
    def fullPatternSvg(self, v): 
        assert v is None or isinstance(v, str), "assert false fullPatternSvg"
        self.__fullPatternSvg = v

    @property
    def fullPatternSvgCSSFlatten(self): return self.__fullPatternSvgCSSFlatten
    @fullPatternSvgCSSFlatten.setter
    def fullPatternSvgCSSFlatten(self, v): 
        assert v is None or isinstance(v, str), "assert false fullPatternSvgCSSFlatten"
        self.__fullPatternSvgCSSFlatten = v

    @property
    def fullPatternRect(self): return self.__fullPatternRect
    @fullPatternRect.setter
    def fullPatternRect(self, v): 
        assert v is None or isinstance(v, fitz.Rect), "assert false fullPatternRect"
        self.__fullPatternRect = v

    @property
    def generateHiddenLayers(self): return self.__generateHiddenLayers
    @generateHiddenLayers.setter
    def generateHiddenLayers(self, v):
        assert v is None or isinstance(v, bool), "assert false generateHiddenLayers"
        self.__generateHiddenLayers = v

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
    def watermark(self): return self.__watermark
    @watermark.setter
    def watermark(self, v):
        assert v is None or isinstance(v, dict), "assert false watermark"
        self.__watermark = v

    @property
    def macadress(self): return self.__macadress
    @macadress.setter
    def macadress(self, v):
        assert v is None or isinstance(v, str), "assert false macadress"
        self.__macadress = v
        
    @property
    def watermarkOpacity(self): return self.__watermarkOpacity
    @watermarkOpacity.setter
    def watermarkOpacity(self, v):
        assert v is None or isinstance(v, str), "assert false watermarkOpacity"
        self.__watermarkOpacity = v

            
    def generateWatermark(self, doc, pagei, centerrect, deltaWH):
        for ii,i in enumerate(['top','down','left','right']):
            if self.watermark['watermark_%s'%i].GetValue() is True:
                ipwatermark = len(self.watermark['watermark_%s_fullpath'%i].GetLabel()) == 0
                if not ipwatermark:
                    docw = fitz.open(self.tempPath + "watermark_rot_%s.pdf"%i)
                    docw = docw.convertToPDF()
                    docw = fitz.open("pdf", docw)
                    pagew = docw.load_page(0)
                    pgtxtwidth = pagew.rect.width
                    pgtxtheight = pagew.rect.height                       
                else:
                    pgtxt = self.macadress
                    pgtxtwidth = self.myfont.text_length(pgtxt, 10)
                    pgtxtHmin = 10 * min([self.myfont.glyph_bbox(ord(x)).y0 for x in pgtxt])
                    pgtxtHmax = 10 * max([self.myfont.glyph_bbox(ord(x)).y1 for x in pgtxt])
                    pgtxtheight = pgtxtHmax-pgtxtHmin
                    
                x = (0 if deltaWH is None or self.generateSheetTrimming == CanvasOnSheet.PIRATES else deltaWH[0])
                y = (0 if deltaWH is None or self.generateSheetTrimming == CanvasOnSheet.PIRATES else deltaWH[1])
                
                if i == 'top':
                    x = x + centerrect.width/2.0 - pgtxtwidth/2.0 
                    y = y 
                    morph = None
                elif i == 'down':
                    x = x + centerrect.width/2.0 - pgtxtwidth/2.0 
                    y = y + centerrect.height - pgtxtheight 
                    morph = None
                elif i == 'left':
                    if not ipwatermark:
                        x = x 
                    else:
                        x = x - pgtxtwidth/2.0 + pgtxtheight/2.0
                    y = y + centerrect.height/2.0 - pgtxtheight/2.0 
                    pivot = fitz.Point(x+pgtxtwidth/2.0,y+pgtxtheight/2.0) 
                    matrix = fitz.Matrix(-90)
                    morph = (pivot, matrix)
                elif i == 'right':
                    if not ipwatermark:
                        x = x + centerrect.width - pgtxtwidth
                    else:
                        x = x + centerrect.width - pgtxtwidth/2.0 - pgtxtheight/2.0 
                    y = y + centerrect.height/2.0 - pgtxtheight/2.0 
                    pivot = fitz.Point(x+pgtxtwidth/2.0,y+pgtxtheight/2.0) 
                    matrix = fitz.Matrix(90)
                    morph = (pivot, matrix)
                    
                if not ipwatermark:
                    pagei.showPDFpage(fitz.Rect(x,y,x+pgtxtwidth,y+pgtxtheight), docw, pno=0, keep_proportion=True, overlay=True, oc=0, rotate=0, clip=None)
                    docw.close()
                else:
                    pagei.insert_textbox(fitz.Rect(x,y,x+pgtxtwidth,y+pgtxtheight), pgtxt, fontsize=10, 
                                        fontname='impact', fontfile=resource_path('impact.ttf'), color=(0,0,0), 
                                        fill=(0,0,0), render_mode=0, border_width=1, encoding=fitz.TEXT_ENCODING_LATIN, 
                                        expandtabs=8, align=fitz.TEXT_ALIGN_LEFT, rotate=0, morph=morph, 
                                        stroke_opacity=1, fill_opacity=int(self.watermarkOpacity)/100.0, oc=None, overlay=True)

            

    

                   
                    

        '''for k in self.fullPatternSvgPerLayer.keys(): 
            tic = time.perf_counter()
            if self.generateHiddenLayers or "show_LAYER" in self.fullPatternSvgPerLayer[k]:
                curfilename = self.fullPatternSvgPerLayer[k].replace('.svg', '.fitz.pdf')
                tempsvg = fitz.open(self.tempPath + curfilename)
                pdfbytes = tempsvg.convert_to_pdf()
                tempsvg.close()
                tempsvg = fitz.open("pdf", pdfbytes) 
                print('Generate the layer %s on each page = central panel + (right/left/down/up) if existing'%k)
                for h,w in self.orderedPageList:
                    idwh = 'L%sC%s'%(h,w)
                    print('idwh %s'%idwh)
                    curPage = self.pageNumDico[idwh] 
                    pagei = doc.load_page(curPage)
                    for area in Areas:
                        if conddico[idwh][area]:
                            try:
                                pagei.show_pdf_page(self.patternShowRectsDico[idwh][area], tempsvg, 0, oc=self.xrefOCG[k], clip=self.patternClipRectsDico[idwh][area])
                                shape = pagei.new_shape()
                                shape.draw_rect(self.canvasShowRectsDico[idwh][area])
                                shape.finish(fill = (1.0,1.0,1.0) if area == Areas.C else (0.98,0.98,0.98), 
                                             fill_opacity=0.1 if area == Areas.C else 0.3)
                                shape.commit()
                                pagei = doc.reload_page(pagei)
                            except Exception as e: print('Warning : Cannot add %s margin to %s, %s'%(area, idwh, e))
                tempsvg.close()
                doc.saveIncr()
            toc = time.perf_counter()
            print(f"{toc - tic:0.4f} seconds")
        doc.close()'''
                          


        
    def run(self):
        
        try:     
            pdfOutFilenameA0 = self.pdfOutFilename.replace('.pdf', '.A0.pdf')
            self.runA0(pdfOutFilenameA0)
        except Exception as e:  
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print('Except : run A0', e, exc_type, fname, exc_tb.tb_lineno)
        try:     
            self.runA4(self.pdfOutFilename.replace('.pdf', '.A4.pdf'))
        except Exception as e:  
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print('Except : run A4', e, exc_type, fname, exc_tb.tb_lineno)
        
        print('Done !')
        
if __name__ == '__main__':
    pass
