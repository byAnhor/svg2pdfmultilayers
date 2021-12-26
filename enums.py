# -*- coding: utf-8 -*-
# svg2pdfmultilayers is a utility to export multilayered SVG to PDF.
# Copyright (C) 2021 Anita Orhand
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from enum import Enum

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

if __name__ == '__main__':
    pass
