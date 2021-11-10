# -*- coding: utf-8 -*-
"""
Created on Sun Dec 26 13:51:54 2021

@author: anita
"""
import sys
import os


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if hasattr(sys,'_MEIPASS'):
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath('./ressources')

    return os.path.join(base_path, relative_path)