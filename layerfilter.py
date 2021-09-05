# svg2pdfmultilayers is a utility to export multilayered SVG to PDF.
# Copyright (C) 2021 Anita Orhand
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


import fitz
import pikepdf
import os
from pprint import pprint
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
    def __init__(self, onelayersvg = None, rect = None):
        self.onelayersvg = onelayersvg
        self.rect = rect
        
    def run(self, outdocpath):
        
        print('-------------- R U N -----------------')
        doc = fitz.open()  
        xrefOCG = dict()                   
        for k in self.onelayersvg.keys(): 
            print(k + ' => ' + str(self.onelayersvg[k]))
            xrefOCG[k] = doc.add_ocg('%s'%k)
        page = doc.new_page(-1, width = self.rect.width, height = self.rect.height)
        doc.save(outdocpath)
        doc.close()
        print('-------------- R U N -----------------')
        
        doc = fitz.open(outdocpath)  
        page0 = doc.load_page(0)
        try:
            for k in self.onelayersvg.keys(): 
                curfilename = self.onelayersvg[k].replace('.svg', '.fitz.pdf')
                print(curfilename)
                tempsvg = fitz.open(curfilename)
                pdfbytes = tempsvg.convert_to_pdf()
                tempsvg.close()
                tempsvg = fitz.open("pdf", pdfbytes) 
                page0.show_pdf_page(self.rect, tempsvg, 0, oc=xrefOCG[k])
                tempsvg.close()
                doc.saveIncr()
            doc.close()
        except: doc.close()
        
        for k in self.onelayersvg.keys(): 
            os.remove(self.onelayersvg[k])
            os.remove(self.onelayersvg[k].replace('.svg', '.fitz.pdf'))

        return outdocpath


        
