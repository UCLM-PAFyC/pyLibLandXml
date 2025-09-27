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
        self.description = None
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
        if dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_ATTRIBUTE_DESCRIPTION_TAG in element:
            self.description = element[dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_ATTRIBUTE_DESCRIPTION_TAG]
        if not dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_COORD_GEOM_TAG in element:
            str_error = ('Not exists element: {} in element: {} in position in element: {} in LandXml file:\n{}'.
                         format(dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_COORD_GEOM_TAG,
                                dlx.XML_ELEMENT_ALIGMENTS_ATTRIBUTE_NAME_TAG,
                                str(position + 1), dlx.XML_DOCUMENT_ALIGMENTS_TAG, file_path))
            return str_error
        element_coord_geom_content = element[dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_COORD_GEOM_TAG]
        if not isinstance(element_coord_geom_content, dict):
            str_error = ('Element: {} in element: {} in position in element: {} in LandXml file:\n{}\nmust be a dict'.
                         format(dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_COORD_GEOM_TAG,
                                dlx.XML_ELEMENT_ALIGMENTS_ATTRIBUTE_NAME_TAG,
                                str(position + 1), dlx.XML_DOCUMENT_ALIGMENTS_TAG, file_path))
            return str_error
        cont = 0
        for element_geometry_tag in element_coord_geom_content:
            cont = cont + 1
            if not element_geometry_tag.lower() in [s.lower() for s in dlx.coord_geom_types]:
                str_error = (
                    'Invalid value: {} in component position: {} in element: {}\nin element: {} in position in element: {} in LandXml file:\n{}'.
                    format(element_geometry_tag, str(cont), dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_COORD_GEOM_TAG,
                           dlx.XML_ELEMENT_ALIGMENTS_ATTRIBUTE_NAME_TAG,
                           str(position + 1), dlx.XML_DOCUMENT_ALIGMENTS_TAG, file_path))
                return str_error
            element_geometry = element_coord_geom_content[element_geometry_tag]
            if element_geometry_tag.casefold() == dlx.XML_ELEMENT_CURVE_TAG.casefold():
                element_curve_list = []
                if isinstance(element_geometry, list):
                    element_curve_list = element_geometry
                else:
                    element_curve_list.append(element_geometry)
                for i in range(len(element_curve_list)):
                    element_curve = element_curve_list[i]
                    yo = 1
            
            yo = 1

        return str_error
