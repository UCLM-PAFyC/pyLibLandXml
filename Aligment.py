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

class Aligment:
    def __init__(self, land_xml):
        self.land_xml = land_xml
        self.position = None # from 0
        self.name = None
        self.length = None
        self.start_cumulative_distance = None

    def set_from_landxml_element(self,
                                 element,
                                 position,
                                 file_path):
        str_error = ''
        self.position = position
        if not dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_ATTRIBUTE_NAME_TAG in element:
            str_error = ('Not exists attribute: {} in element: {} in position in element: {} in LandXml file:\n{}'.
                         format(dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_ATTRIBUTE_NAME_TAG,
                                dlx.XML_ELEMENT_ALIGMENTS_ATTRIBUTE_NAME_TAG,
                                str(position + 1), dlx.XML_DOCUMENT_ALIGMENTS_TAG, file_path))
            return str_error
        self.name = element[dlx.XML_ELEMENT_ALIGMENTS_ATTRIBUTE_NAME_TAG]
        if not dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_ATTRIBUTE_STASTART_TAG in element:
            str_error = ('Not exists attribute: {} in element: {} in position in element: {} in LandXml file:\n{}'.
                         format(dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_ATTRIBUTE_NAME_TAG,
                                dlx.XML_ELEMENT_ALIGMENTS_ATTRIBUTE_NAME_TAG,
                                str(position + 1), dlx.XML_DOCUMENT_ALIGMENTS_TAG, file_path))
            return str_error
        value = element[dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_ATTRIBUTE_STASTART_TAG]
        try:
            self.start_cumulative_distance = float(value)
        except ValueError:
            str_error = ('Attribute: {} in element: {} in position in element: {} in LandXml file:\n{}\nmust be a float: {}'.
                         format(dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_ATTRIBUTE_NAME_TAG,
                                dlx.XML_ELEMENT_ALIGMENTS_ATTRIBUTE_NAME_TAG,
                                str(position + 1), dlx.XML_DOCUMENT_ALIGMENTS_TAG, file_path, value))
            return str_error
        if not dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_ATTRIBUTE_LENGTH_TAG in element:
            str_error = ('Not exists attribute: {} in element: {} in position in element: {} in LandXml file:\n{}'.
                         format(dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_ATTRIBUTE_LENGTH_TAG,
                                dlx.XML_ELEMENT_ALIGMENTS_ATTRIBUTE_NAME_TAG,
                                str(position + 1), dlx.XML_DOCUMENT_ALIGMENTS_TAG, file_path))
            return str_error
        value = element[dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_ATTRIBUTE_LENGTH_TAG]
        try:
            self.length = float(value)
        except ValueError:
            str_error = ('Attribute: {} in element: {} in position in element: {} in LandXml file:\n{}\nmust be a float: {}'.
                         format(dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_ATTRIBUTE_LENGTH_TAG,
                                dlx.XML_ELEMENT_ALIGMENTS_ATTRIBUTE_NAME_TAG,
                                str(position + 1), dlx.XML_DOCUMENT_ALIGMENTS_TAG, file_path, value))
            return str_error

        return str_error
