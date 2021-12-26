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
    def __init__(self):
        self.parent = None
        self.svg_to_be_layered_filename = None
        self.svg_to_be_layered_flatten_filename = None
        self.svg_to_be_layered_fitz_pdf_filename = None
        self.svg_layered_res_basename = None
        self._freeze()

    @property
    def svg_to_be_layered_filename(self): return self.__svg_to_be_layered_filename
    @svg_to_be_layered_filename.setter
    def svg_to_be_layered_filename(self, v): 
        assert v is None or isinstance(v, str), "assert false svg_to_be_layered_filename"
        self.__svg_to_be_layered_filename = v

    @property
    def svg_to_be_layered_flatten_filename(self): return self.__svg_to_be_layered_flatten_filename
    @svg_to_be_layered_flatten_filename.setter
    def svg_to_be_layered_flatten_filename(self, v): 
        assert v is None or isinstance(v, str), "assert false svg_to_be_layered_flatten_filename"
        self.__svg_to_be_layered_flatten_filename = v

    @property
    def svg_to_be_layered_fitz_pdf_filename(self): return self.__svg_to_be_layered_fitz_pdf_filename
    @svg_to_be_layered_fitz_pdf_filename.setter
    def svg_to_be_layered_fitz_pdf_filename(self, v): 
        assert v is None or isinstance(v, str), "assert false svg_to_be_layered_fitz_pdf_filename"
        self.__svg_to_be_layered_fitz_pdf_filename = v

    @property
    def svg_layered_res_basename(self): return self.__svg_layered_res_basename
    @svg_layered_res_basename.setter
    def svg_layered_res_basename(self, v): 
        assert v is None or isinstance(v, str), "assert false svg_layered_res_basename"
        self.__svg_layered_res_basename = v

   
    def run(self):
        if self.svg_to_be_layered_filename is None: return 
        if self.svg_to_be_layered_flatten_filename is None: return 
        if self.svg_layered_res_basename is None: return 
        if self.svg_to_be_layered_fitz_pdf_filename is None: return 
        
        print("Generate SVG with splitted layers", self.svg_to_be_layered_filename)
        
        svgToBeLayeredFitzPdfFile = fitz.open(self.svg_to_be_layered_flatten_filename)
        svgToBeLayeredFitzPdfFilePage0 = svgToBeLayeredFitzPdfFile.load_page(0)
        svgToBeLayeredFitzPdfFilePageWidth = svgToBeLayeredFitzPdfFilePage0.rect.width
        svgToBeLayeredFitzPdfFilePageHeight = svgToBeLayeredFitzPdfFilePage0.rect.height

        # Save a full size PDF version of the flatten SVG file
        svgToBeLayeredFitzPdfFile = svgToBeLayeredFitzPdfFile.convert_to_pdf()
        svgToBeLayeredFitzPdfFile = fitz.open("pdf", svgToBeLayeredFitzPdfFile)
        svgToBeLayeredFitzPdfFile.save(self.svg_to_be_layered_fitz_pdf_filename)

        svgInDoc = minidom.parse(self.svg_to_be_layered_flatten_filename)
        
        # Build the group/layer hierarchy
        allL = [l for l in svgInDoc.getElementsByTagName('g') if l.getAttribute("inkscape:groupmode") == 'layer']   
        layersHierarchy = dict()
        for l in allL:
            layersHierarchy[l] = list()
            lpn = l.parentNode
            while lpn is not None:
                if lpn in allL : layersHierarchy[l].append(lpn.getAttribute("inkscape:label"))
                lpn = lpn.parentNode                

        
        jsondata = dict()
                      
        jsondata['FullSizeWidth'] = svgToBeLayeredFitzPdfFilePageWidth
        jsondata['FullSizeHeight'] = svgToBeLayeredFitzPdfFilePageHeight
        jsondata['LayersFilenames'] = dict()
                   
        for l in reversed(allL):
            svgInDoc0 = minidom.parse(self.svg_to_be_layered_flatten_filename)
            allOL = [ol for ol in svgInDoc0.getElementsByTagName('g') if ol.getAttribute("inkscape:groupmode") == 'layer']
            for ol in allOL:
                if l.getAttribute("id") != ol.getAttribute("id") and ol.getAttribute("inkscape:label") not in layersHierarchy[l]:
                    parent = ol.parentNode
                    parent.removeChild(ol)
            str_ = svgInDoc0.toxml()
            onesvgbase = self.svg_layered_res_basename +  '_%s.svg'%(l.getAttribute("inkscape:label"))
            hord = 'hidden' if "display:none" in l.getAttribute("style") else 'display'
            jsondata['LayersFilenames'][l.getAttribute("inkscape:label")] = dict()
            jsondata['LayersFilenames'][l.getAttribute("inkscape:label")]['display'] = hord
            jsondata['LayersFilenames'][l.getAttribute("inkscape:label")]['svg'] = str(onesvgbase)
             
            with open(jsondata['LayersFilenames'][l.getAttribute("inkscape:label")]['svg'], "wb") as out:
                out.write(str_.encode("UTF-8", "ignore")) 

        for k in jsondata['LayersFilenames'].keys(): 
            onesvgfile = jsondata['LayersFilenames'][k]['svg']
            onepdffile = onesvgfile.replace('.svg', '.fitz.pdf')
            svgToBeLayeredFitzPdfFile = fitz.open(onesvgfile)
            svgToBeLayeredFitzPdfFile = svgToBeLayeredFitzPdfFile.convert_to_pdf()
            svgToBeLayeredFitzPdfFile = fitz.open("pdf", svgToBeLayeredFitzPdfFile)
            svgToBeLayeredFitzPdfFile.save(onepdffile)
            
        with open(self.svg_layered_res_basename + '.json', 'w') as outfile:
            json.dump(jsondata, outfile)
        return jsondata
