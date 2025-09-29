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

# http://www.landxml.org/schema/landxml-1.2/documentation/LandXML-1.2Doc_CrossSectSurf.html#Link07F1F4F0
class CrossSectionSurface:
    def __init__(self, cross_section):
        self.cross_section = cross_section
        self.name = None
        self.description = None
        self.state = None
        self.points = None # [dis_to_axis, elevation]
        self.feature_code = None
        self.feature_text = None

    def set_from_landxml_element(self,
                                 element):
        str_error = ''
        if not dlx.XML_ELEMENT_CROSS_SECT_SURF_ATTRIBUTE_NAME_TAG in element:
            str_error = ('Not exists attribute: {}'.format(dlx.XML_ELEMENT_CROSS_SECT_SURF_ATTRIBUTE_NAME_TAG))
            return str_error
        self.name = element[dlx.XML_ELEMENT_CROSS_SECT_SURF_ATTRIBUTE_NAME_TAG]
        if dlx.XML_ELEMENT_CROSS_SECT_SURF_ATTRIBUTE_DESC_TAG in element:
            self.description = element[dlx.XML_ELEMENT_CROSS_SECT_SURF_ATTRIBUTE_DESC_TAG]
        if dlx.XML_ELEMENT_CROSS_SECT_SURF_ATTRIBUTE_STATE_TAG in element:
            self.state = element[dlx.XML_ELEMENT_CROSS_SECT_SURF_ATTRIBUTE_STATE_TAG]
        if dlx.XML_ELEMENT_CROSS_SECT_SURF_FEATURE_TAG in element:
            element_feature = element[dlx.XML_ELEMENT_CROSS_SECT_SURF_FEATURE_TAG]
            if (dlx.XML_ELEMENT_CROSS_SECT_SURF_FEATURE_ATTRIBUTE_CODE_TAG in element_feature):
                self.feature_code = element_feature[dlx.XML_ELEMENT_CROSS_SECT_SURF_FEATURE_ATTRIBUTE_CODE_TAG]
            if (dlx.XML_ELEMENT_CROSS_SECT_SURF_FEATURE_ATTRIBUTE_TEXT_TAG in element_feature):
                self.feature_text = element_feature[dlx.XML_ELEMENT_CROSS_SECT_SURF_FEATURE_ATTRIBUTE_TEXT_TAG]
        if not dlx.XML_ELEMENT_CROSS_SECT_SURF_PNT_LIST_2D_TAG in element:
            str_error = ('Not exists attribute: {}'.format(dlx.XML_ELEMENT_CROSS_SECT_SURF_PNT_LIST_2D_TAG))
            return str_error
        value = element[dlx.XML_ELEMENT_CROSS_SECT_SURF_PNT_LIST_2D_TAG]
        value_list = value.split(' ')
        try:
            values = [float(char) for char in value_list]
        except ValueError:
            str_error = (
                'Attribute: {} must be a list of even floats: {}'.
                format(dlx.XML_ELEMENT_CROSS_SECT_SURF_PNT_LIST_2D_TAG, value))
            return str_error
        if not len(values) % 2 == 0:
            str_error = (
                'Attribute: {} must be a list of even floats: {}'.
                format(dlx.XML_ELEMENT_CROSS_SECT_SURF_PNT_LIST_2D_TAG, value))
            return str_error
        self.points = []
        nop = int(len(values) / 2)
        for i in range(nop):
            self.points.append([values[i * 2], values[i * 2 + 1]])
        return str_error






