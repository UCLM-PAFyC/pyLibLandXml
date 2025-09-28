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
from Curve import Curve
from Line import Line
from Spiral import Spiral
from ProfAlign import ProfAlign

class Aligment:
    def __init__(self, land_xml):
        self.land_xml = land_xml
        self.position = None # from 0
        self.name = None
        self.length = None
        self.description = None
        self.start_cumulative_distance = None
        self.coord_geoms_shorted_by_distance = None

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
        coord_geom_by_distance = {}
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
            element_list = []
            if isinstance(element_geometry, list):
                element_list = element_geometry
            else:
                element_list.append(element_geometry)
            for i in range(len(element_list)):
                element_coord_geom = element_list[i]
                coord_geom = None
                if element_geometry_tag.casefold() == dlx.XML_ELEMENT_CURVE_TAG.casefold():
                    coord_geom = Curve(self)
                elif element_geometry_tag.casefold() == dlx.XML_ELEMENT_LINE_TAG.casefold():
                    coord_geom = Line(self)
                elif element_geometry_tag.casefold() == dlx.XML_ELEMENT_SPIRAL_TAG.casefold():
                    coord_geom = Spiral(self)
                else:
                    str_error = (
                        'Invalid value: {} in component position: {} in element: {}\nin element: {} in position in element: {} in LandXml file:\n{}'.
                        format(element_geometry_tag, str(cont), dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_COORD_GEOM_TAG,
                               dlx.XML_ELEMENT_ALIGMENTS_ATTRIBUTE_NAME_TAG,
                               str(position + 1), dlx.XML_DOCUMENT_ALIGMENTS_TAG, file_path))
                    return str_error
                str_error = coord_geom.set_from_landxml_element(element_coord_geom)
                if str_error:
                    str_error = (
                        'Setting element: {} in position: {} in component position: {} in element: {}'
                        '\nin element: {} in position in element: {} in LandXml file:\n{}'.
                        format(element_geometry_tag, str(i + 1), element_geometry_tag,
                               str(cont), dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_COORD_GEOM_TAG,
                               dlx.XML_ELEMENT_ALIGMENTS_ATTRIBUTE_NAME_TAG,
                               str(position + 1), dlx.XML_DOCUMENT_ALIGMENTS_TAG, file_path))
                    return str_error
                sta_start_mm_int = int(coord_geom.sta_start * 1000.)
                coord_geom_by_distance[sta_start_mm_int] = coord_geom
        self.coord_geoms_shorted_by_distance = dict(sorted(coord_geom_by_distance.items()))
        if not dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_PROFILE_TAG in element:
            str_error = ('Not exists element: {} in element: {} in position in element: {} in LandXml file:\n{}'.
                         format(dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_PROFILE_TAG,
                                dlx.XML_ELEMENT_ALIGMENTS_ATTRIBUTE_NAME_TAG,
                                str(position + 1), dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_PROFILE_TAG, file_path))
            return str_error
        element_profile = element[dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_PROFILE_TAG]
        profile_list = []
        if isinstance(element_profile, list):
            profile_list = element_profile
        else:
            profile_list.append(element_profile)
        for i in range(len(profile_list)):
            element_profile_content = profile_list[i]
            if not isinstance(element_profile_content, dict):
                str_error = ('Element: {} in position: {} in element: {} in position in element: {} in LandXml file:\n{}\nmust be a dict'.
                             format(dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_PROFILE_TAG, str(i + 1),
                                    dlx.XML_ELEMENT_ALIGMENTS_ATTRIBUTE_NAME_TAG,
                                    str(position + 1), dlx.XML_DOCUMENT_ALIGMENTS_TAG, file_path))
                return str_error
            if not dlx.XML_ELEMENT_PROFILE_PROF_ALIGN_TAG in element_profile_content:
                str_error = ('Not exists element: {} in element: {}\nin element: {} in position in element: {} in LandXml file:\n{}'.
                         format(dlx.XML_ELEMENT_PROFILE_PROF_ALIGN_TAG,
                                dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_PROFILE_TAG,
                                dlx.XML_ELEMENT_ALIGMENTS_ATTRIBUTE_NAME_TAG,
                                str(position + 1), dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_PROFILE_TAG, file_path))
                return str_error
            element_profile_prof_aling_content = element_profile_content[dlx.XML_ELEMENT_PROFILE_PROF_ALIGN_TAG]
            prof_align = ProfAlign(self)
            str_error = prof_align.set_from_landxml_element(element_profile_prof_aling_content)
            if str_error:
                str_error = (
                    'Setting element: {} in position: {} in component position: {} in element: {}'
                    '\nin element: {} in position in element: {} in LandXml file:\n{}'.
                    format(dlx.XML_ELEMENT_PROFILE_PROF_ALIGN_TAG, str(i + 1),
                           str(cont), dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_PROFILE_TAG,
                           dlx.XML_ELEMENT_ALIGMENTS_ATTRIBUTE_NAME_TAG,
                           str(position + 1), dlx.XML_DOCUMENT_ALIGMENTS_TAG, file_path))
                return str_error

            yo = 1
        return str_error
