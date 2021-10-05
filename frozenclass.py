# -*- coding: utf-8 -*-
"""
Created on Fri Sep 24 12:27:58 2021

@author: anita
"""

class FrozenClass(object):
    __isfrozen = False
    def __setattr__(self, key, value):
        if self.__isfrozen and not hasattr(self, key):
            raise TypeError( "%r is a frozen class" % self )
        object.__setattr__(self, key, value)

    def _freeze(self):
        self.__isfrozen = True
