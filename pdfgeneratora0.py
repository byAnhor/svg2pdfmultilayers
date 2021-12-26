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
from pdfgenerator import PDFGenerator

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

   
class PDFGeneratorA0(FrozenClass):
    def __init__(self):
        super(PDFGeneratorA0, self).__init__()
        self.generateA0 = None
        self.generateCommun = PDFGenerator()
        self.xrefOCG = None
        self._freeze()     

    @property
    def fullPatternSvgPerLayer(self): return self.generateCommun.fullPatternSvgPerLayer
    @property
    def generateHiddenLayers(self): return self.generateCommun.generateHiddenLayers
    @property
    def fullPatternRect(self): return self.generateCommun.fullPatternRect

    def generateWatermarkA0(self, doc):
        page0 = doc.load_page(0) 
        self.generateCommun.generateWatermark(doc, page0, page0.rect, None)
        doc.saveIncr()

    def runA0(self, outputfilenameA0):
        
        print('-------------- G E N E R A T E --- A 0 -----------------\n', outputfilenameA0 if self.generateA0 else 'N/A')
        if self.generateA0:

            with fitz.open() as doc:
                doc.new_page(-1, width = self.fullPatternRect.width, height = self.fullPatternRect.height)
                doc.save(outputfilenameA0)

            try:

                with fitz.open(outputfilenameA0) as doc:
                    self.xrefOCG = dict()    
                    for k in self.fullPatternSvgPerLayer['LayersFilenames'].keys(): 
                        if self.generateHiddenLayers or self.fullPatternSvgPerLayer['LayersFilenames'][k]['display'] == 'display':
                            self.xrefOCG[k] = doc.add_ocg('%s'%k)
                            doc.saveIncr()
    
                    page0 = doc.load_page(0)
                    for k in self.fullPatternSvgPerLayer['LayersFilenames'].keys(): 
                        if self.generateHiddenLayers or self.fullPatternSvgPerLayer['LayersFilenames'][k]['display'] == 'display':
                            curfilename = self.fullPatternSvgPerLayer['LayersFilenames'][k]['svg'].replace('.svg', '.fitz.pdf')
                            tempsvg = fitz.open(curfilename)
                            pdfbytes = tempsvg.convert_to_pdf()
                            tempsvg.close()
                            tempsvg = fitz.open("pdf", pdfbytes) 
                            page0.show_pdf_page(self.fullPatternRect, tempsvg, 0, oc=self.xrefOCG[k])
                            tempsvg.close()
                            doc.saveIncr()
                        else: print('Hidden', k)

                    self.generateWatermarkA0(doc)
                    
            except Exception as e:
                print('Something went wrong during runA0')
                print('Exception:', e)
                
if __name__ == '__main__':
    pass