# -*- coding: utf-8 -*-
"""
Created on Wed Dec  8 10:56:45 2021

@author: anita
"""
from frozenclass import FrozenClass
from enum import Enum

class OutputSelection(Enum):
     NONE = 0
     ONE_SVG = 1
     SEVERAL_SVG = 2
     
class GenerationAlgoOutput(FrozenClass):
    
    def __init__(self, main_gui):
        self.main_gui = main_gui
        self.output_is_selected = OutputSelection.NONE
        self._freeze()
        


            
            
        
