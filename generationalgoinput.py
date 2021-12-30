# -*- coding: utf-8 -*-
"""
Created on Wed Dec  8 10:56:45 2021

@author: anita
"""
import os
import wx
import json
from frozenclass import FrozenClass
from enum import Enum
from from1svgtonpdf import From1svgToNpdf
from from1svgto1svgflatten import From1svgTo1svgFlatten

class InputSelection(Enum):
     NONE = 0
     ONE_SVG = 1
     SEVERAL_SVG = 2
     
class GenerationAlgoInput(FrozenClass):
    
    def __init__(self, main_gui):
        self.main_gui = main_gui
        self.input_is_selected = InputSelection.NONE
        self.algo_Nsvg_as_1jsonfile = None
        self.algo_from_1svg_to_1svgflatten= From1svgTo1svgFlatten()
        self.algo_from_1svg_to_npdf = From1svgToNpdf()
        self._freeze()
        
    @property
    def algo_Nsvg_as_1jsonfile(self): return self.__algo_Nsvg_as_1jsonfile
    @algo_Nsvg_as_1jsonfile.setter
    def algo_Nsvg_as_1jsonfile(self, v): 
        assert v is None or isinstance(v, str), "assert false algo_Nsvg_as_1jsonfile"
        self.__algo_Nsvg_as_1jsonfile = v

    def load_input_filename_list(self, inputfilenamelist):
        if self.algo_Nsvg_as_1jsonfile is None: return 
        
        autogenpath = '%s/AutoGenPDF/'%os.path.dirname(inputfilenamelist[0])
        if not os.path.exists(autogenpath): os.makedirs(autogenpath)
        
        self.input_is_selected = InputSelection.ONE_SVG if len(inputfilenamelist) == 1 else InputSelection.SEVERAL_SVG
        try:
            jsondata = dict()
            for fni,fn in enumerate(inputfilenamelist):
                jsondata['SVG%s'%fni] = dict() 
                jsondata['SVG%s'%fni]['SVGraw'] = fn
                jsondata['SVG%s'%fni]['SVGflatten'] = self.main_gui.temp_path + os.path.basename(fn) + '.cssflatten.svg'
                self.algo_from_1svg_to_1svgflatten.svg_to_be_flatten_filename = jsondata['SVG%s'%fni]['SVGraw']
                self.algo_from_1svg_to_1svgflatten.svg_flatten_res_filename = jsondata['SVG%s'%fni]['SVGflatten']
                self.algo_from_1svg_to_1svgflatten.run()
                jsondata['SVG%s'%fni]['PDFflatten'] = self.main_gui.temp_path + os.path.basename(fn) + '.cssflatten.fitz.pdf'               
                jsondata['SVG%s'%fni]['LayersBasename'] = self.main_gui.temp_path + os.path.basename(fn).replace('.svg','') + '_Layer'               
                jsondata['SVG%s'%fni]['PageA4Basename'] = self.main_gui.temp_path + os.path.basename(fn).replace('.svg','') + '_PageA4'               
                self.algo_from_1svg_to_npdf.svg_to_be_layered_filename = jsondata['SVG%s'%fni]['SVGraw']
                self.algo_from_1svg_to_npdf.svg_to_be_layered_flatten_filename = jsondata['SVG%s'%fni]['SVGflatten']
                self.algo_from_1svg_to_npdf.svg_to_be_layered_fitz_pdf_filename = jsondata['SVG%s'%fni]['PDFflatten']
                self.algo_from_1svg_to_npdf.svg_layered_res_basename = jsondata['SVG%s'%fni]['LayersBasename']
                npdf = self.algo_from_1svg_to_npdf.run()
                jsondata['SVG%s'%fni]['SVGLayers'] = npdf
                jsondata['SVG%s'%fni]['PDFout'] = 'User choice' if len(inputfilenamelist) == 1 else '%s%s'%(autogenpath, os.path.basename(fn).replace('.svg','.pdf'))
                h = [x for x in npdf['LayersFilenames'] if npdf['LayersFilenames'][x]['display'] == 'hidden']
                d = [x for x in npdf['LayersFilenames'] if npdf['LayersFilenames'][x]['display'] == 'display']
                print('Load %s'%os.path.basename(fn), 'found %s hidden layers and %s displayed layers'%(len(h),len(d)))
            jsondata['PDFmergedout'] = '%smerged.pdf'%autogenpath
            with open(self.algo_Nsvg_as_1jsonfile, 'w') as jsonfile:
                json.dump(jsondata, jsonfile, indent=4, sort_keys=False)        
        except Exception as e:
            wx.LogError('Something went wrong in load_input_filename_list')
            wx.LogError('Exception:', e)

            
            
        
