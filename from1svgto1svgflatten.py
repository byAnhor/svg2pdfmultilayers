# -*- coding: utf-8 -*-
"""
Created on Fri Sep 24 13:26:33 2021

@author: anita
"""

import json
from xml.dom import minidom
from frozenclass import FrozenClass

class From1svgTo1svgFlatten(FrozenClass):
    def __init__(self):
        self.svg_to_be_flatten_filename = None
        self.svg_flatten_res_filename = None
        self._freeze()

    @property
    def svg_to_be_flatten_filename(self): return self.__svg_to_be_flatten_filename
    @svg_to_be_flatten_filename.setter
    def svg_to_be_flatten_filename(self, v): 
        assert v is None or isinstance(v, str), "assert false svg_to_be_flatten_filename"
        self.__svg_to_be_flatten_filename = v

    @property
    def svg_flatten_res_filename(self): return self.__svg_flatten_res_filename
    @svg_flatten_res_filename.setter
    def svg_flatten_res_filename(self, v): 
        assert v is None or isinstance(v, str), "assert false svg_flatten_res_filename"
        self.__svg_flatten_res_filename = v

    def getAllPathsDico(self, doc):
        res = dict()
        for p in doc.getElementsByTagName('path'): 
            res[p.getAttribute('id')] = {'obj':p}
            res[p.getAttribute('id')]['class'] = (p.getAttribute('class')) if p.hasAttribute('class') else None
            res[p.getAttribute('id')]['style'] = (p.getAttribute('style')) if p.hasAttribute('style') else ""
            res[p.getAttribute('id')]['parent'] = []
            cur = p
            while cur.parentNode is not None and not isinstance(cur.parentNode, minidom.Document) and cur.parentNode.tagName != 'svg':
                res[p.getAttribute('id')]['parent'].append(cur.parentNode)
                cur = cur.parentNode
        return res

    def getAllGroupsDico(self, doc):
        res = dict()
        for g in doc.getElementsByTagName('g'):
            res[g.getAttribute('id')] = {'obj':g}
            res[g.getAttribute('id')]['class'] = (g.getAttribute('class')) if g.hasAttribute('class') else None
            res[g.getAttribute('id')]['style'] = (g.getAttribute('style')) if g.hasAttribute('style') else ""
            res[g.getAttribute('id')]['parent'] = []
            cur = g
            while cur.parentNode is not None and not isinstance(cur.parentNode, minidom.Document):
                res[g.getAttribute('id')]['parent'].append(cur.parentNode)
                cur = cur.parentNode
        return res

    def getStyleTag(self, doc):
        styleTagList = doc.getElementsByTagName('style')
        if len(styleTagList) == 0: return None
        else: return styleTagList[0]     
               
    def getAllClassesDico(self, styleTag):
        # retrieve the <style></style> text
        styleTagText = styleTag.firstChild.data
        styleTagText = styleTagText.replace('\n','').replace(' ','')
        # remove the <style></style> tag from the minidom tree
        styleTagParent = styleTag.parentNode
        styleTagParent.removeChild(styleTag)
        # Parse the <style></style> text according to {...}
        res = dict()
        while '{' in styleTagText:
            facco = styleTagText.index('{')
            lacco = styleTagText.index('}')
            k = styleTagText[0:facco]
            res[k] = styleTagText[facco+1:lacco]
            styleTagText = styleTagText[lacco+1:]
        return res        

    def injectClasses(self, allClassesDico, allGroupsDico, allPathsDico):
        for p in allPathsDico:
            curPath = allPathsDico[p]
            oldstyle = curPath['obj'].getAttribute('style').replace(' ','').split(';')
            addstyle = []
            if curPath['class'] is not None:
                for c in curPath['class'].split():
                    addstyle += allClassesDico['.%s'%c].replace(' ','').split(';') if '.%s'%c in allClassesDico else ""
            parentstyle = []
            for f in curPath['parent']:
                parentstyle += allGroupsDico[f.getAttribute('id')]['style'].replace(' ','').split(';')
                if allGroupsDico[f.getAttribute('id')]['class'] is not None:
                    for c in allGroupsDico[f.getAttribute('id')]['class'].split():
                        parentstyle += allClassesDico['.%s'%c].replace(' ','').split(';') if '.%s'%c in allClassesDico else "" 
            curPath['obj'].setAttribute('style', ';'.join([x for x in oldstyle + addstyle + parentstyle if len(x)>0])+';')
        
    def run(self):
        if self.svg_to_be_flatten_filename is None: return 
        
        print("Generate SVG with flatten CSS", self.svg_to_be_flatten_filename)

        svgInDoc = minidom.parse(self.svg_to_be_flatten_filename)
        allPathsDico = self.getAllPathsDico(svgInDoc)
        allGroupsDico = self.getAllGroupsDico(svgInDoc)
        styleTag = self.getStyleTag(svgInDoc)
        
        if styleTag is not None: 
            allClassesDico = self.getAllClassesDico(styleTag)
            self.injectClasses(allClassesDico, allGroupsDico, allPathsDico)

        for g in allGroupsDico:
            allGroupsDico[g]['obj'].setAttribute('style', '')
            allGroupsDico[g]['obj'].setAttribute('class', '')
        
        with open(self.svg_flatten_res_filename, 'w', encoding='utf-8') as outfile: 
            svgInDoc.writexml(outfile, indent='', addindent='  ', newl='\n', encoding='UTF-8')
        crlf = b'\r\n'
        cr = b'\n'
        with open(self.svg_flatten_res_filename, 'rb') as f:
            content = f.read()
        content = content.replace(crlf, cr)
        with open(self.svg_flatten_res_filename, 'wb') as f:
            f.write(content) 

if __name__ == '__main__':
    x = From1svgTo1svgFlatten() 
    x.svg_to_be_flatten_filename = './tests/Lamericana_Pantalon_Douce_Projection_color.svg'
    x.svg_flatten_res_filename = './TEMP/unitary_test_flatten_svg.svg'
    x.run()

