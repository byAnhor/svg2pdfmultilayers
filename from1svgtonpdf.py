# -*- coding: utf-8 -*-
"""
Created on Fri Sep 24 13:26:33 2021

@author: anita
"""

import os
import fitz
import json
from xml.dom import minidom
from frozenclass import FrozenClass

class From1svgToNpdf(FrozenClass):
    def __init__(self, temppath):
        self.temp_path = temppath
        self.svg_in = None
        self.json_file = None

    def set_SVG_in(self, filename):
        self.svg_in = filename
        self.json_file = self.temp_path + os.path.basename(filename).replace('.svg', '.json')

    def run(self):
        if self.svg_in is None: return self
        
        jsondata = dict()
        
        svgInBase = os.path.basename(self.svg_in)
        svgInFile = svgInBase.replace('.svg','')
        fullpdfInFile = self.temp_path + svgInFile + '.fitz.pdf'
            
        svgInFileFitz = fitz.open(self.svg_in)
        svgInFileFitzPage0 = svgInFileFitz.load_page(0)
        jsondata['full_pattern_svg'] = self.svg_in
        jsondata['full_pattern_width'] = svgInFileFitzPage0.rect.width
        jsondata['full_pattern_height'] = svgInFileFitzPage0.rect.height
        jsondata['temp_path'] = self.temp_path
        jsondata['layers_filenames'] = dict()
           
        pdfInFileFitz = svgInFileFitz.convert_to_pdf()
        pdfInFileFitz = fitz.open("pdf", pdfInFileFitz)
        print('SVG -> full PDF : %s'%fullpdfInFile)
        pdfInFileFitz.save(fullpdfInFile)
        
        svgInDoc = minidom.parse(self.svg_in)
        allL = [l for l in svgInDoc.getElementsByTagName('g') if l.getAttribute("inkscape:groupmode") == 'layer']   
        for l in reversed(allL):
            svgInDoc0 = minidom.parse(self.svg_in)
            allOL = [ol for ol in svgInDoc0.getElementsByTagName('g') if ol.getAttribute("inkscape:groupmode") == 'layer']
            for ol in allOL:
                if (l.getAttribute("id") != ol.getAttribute("id")):
                    parent = ol.parentNode
                    parent.removeChild(ol)
            str_ = svgInDoc0.toxml()
            displayStr = "_hidden" if "display:none" in l.getAttribute("style") else "_show"
            onesvgbase = svgInFile + displayStr + '_LAYER_%s.svg'%(l.getAttribute("inkscape:label"))
            jsondata['layers_filenames'][l.getAttribute("id")] = str(onesvgbase)
            with open(self.temp_path + onesvgbase, "wb") as out:
                out.write(str_.encode("UTF-8", "ignore")) 
            print('SVG -> %s layer SVG : %s'%(l.getAttribute("inkscape:label"), onesvgbase))

        for k in jsondata['layers_filenames'].keys(): 
            onesvgfile = jsondata['layers_filenames'][k]
            onepdffile = onesvgfile.replace('.svg', '.fitz.pdf')
            svgInFileFitz = fitz.open(self.temp_path + onesvgfile)
            svgInFileFitz = svgInFileFitz.convert_to_pdf()
            svgInFileFitz = fitz.open("pdf", svgInFileFitz)
            svgInFileFitz.save(self.temp_path + onepdffile)
            print('SVG -> 1 layer PDF : %s'%onepdffile)
            
        with open(self.json_file, 'w') as outfile:
            json.dump(jsondata, outfile)
        return self.json_file
