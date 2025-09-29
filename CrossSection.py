# authors:
# David Hernandez Lopez, david.hernandez@uclm.es

import os, sys
import math
import pathlib
import datetime
import json
import xmltodict
import numpy as np

current_path = os.path.dirname(__file__)
sys.path.append(os.path.join(current_path, '..'))
sys.path.append(os.path.join(current_path))

# from . import defs_landxml as dlx
import defs_landxml as dlx
from CrossSectionSurface import CrossSectionSurface

# http://www.landxml.org/schema/landxml-1.2/documentation/LandXML-1.2Doc_CrossSectSurf.html#Link07F1F4F0
class CrossSection:
    def __init__(self, aligment):
        self.aligment = aligment
        self.start_cumulative_distance = None
        self.cross_section_surface = None

    def set_from_landxml_element(self,
                                 element):
        str_error = ''
        if not dlx.XML_ELEMENT_CROSS_SECT_ATTRIBUTE_STA_TAG in element:
            str_error = ('Not exists attribute: {}'.format(dlx.XML_ELEMENT_CROSS_SECT_ATTRIBUTE_STA_TAG))
            return str_error
        value = element[dlx.XML_ELEMENT_CROSS_SECT_ATTRIBUTE_STA_TAG]
        try:
            self.start_cumulative_distance = float(value)
        except ValueError:
            str_error = (
                'Attribute: {} must be a float: {}'.
                format(dlx.XML_ELEMENT_CROSS_SECT_ATTRIBUTE_STA_TAG, value))
            return str_error
        if not dlx.XML_ELEMENT_CROSS_SECT_CROSS_SECT_SURF_TAG in element:
            str_error = ('Not exists element: {}'.format(dlx.XML_ELEMENT_CROSS_SECT_CROSS_SECT_SURF_TAG))
            return str_error
        element_cross_section_surface = element[dlx.XML_ELEMENT_CROSS_SECT_CROSS_SECT_SURF_TAG]
        cross_section_surface = CrossSectionSurface(self)
        str_error = cross_section_surface.set_from_landxml_element(element_cross_section_surface)
        if str_error:
            str_error = (
                'Setting elememnt: {} error:\n{}'.
                format(dlx.XML_ELEMENT_CROSS_SECT_CROSS_SECT_SURF_TAG, str_error))
            return str_error
        self.cross_section_surface = cross_section_surface
        return str_error


