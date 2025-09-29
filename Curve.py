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

# http://www.landxml.org/schema/landxml-1.2/documentation/LandXML-1.2Doc_Curve.html
class Curve:
    def __init__(self, aligment):
        self.aligment = aligment
        self.start_cumulative_distance = None
        self.rotation = None
        self.curve_type = None
        self.radius = None
        self.length = None
        self.direction_start = None
        self.direction_end = None
        self.point_start = None  # point
        self.point_center = None  # point
        self.point_end = None  # point

    def set_from_landxml_element(self,
                                 element):
        str_error = ''
        if not dlx.XML_ELEMENT_CURVE_ATTRIBUTE_STA_START_TAG in element:
            str_error = ('Not exists attribute: {}'.format(dlx.XML_ELEMENT_CURVE_ATTRIBUTE_STA_START_TAG))
            return str_error
        value = element[dlx.XML_ELEMENT_CURVE_ATTRIBUTE_STA_START_TAG]
        try:
            self.start_cumulative_distance = float(value)
        except ValueError:
            str_error = (
                'Attribute: {} must be a float: {}'.
                format(dlx.XML_ELEMENT_CURVE_ATTRIBUTE_STA_START_TAG, value))
            return str_error
        if not dlx.XML_ELEMENT_CURVE_ATTRIBUTE_ROT_TAG in element:
            str_error = ('Not exists attribute: {}'.format(dlx.XML_ELEMENT_CURVE_ATTRIBUTE_ROT_TAG))
            return str_error
        value = element[dlx.XML_ELEMENT_CURVE_ATTRIBUTE_ROT_TAG]
        if not value in dlx.rotation_types:
            str_error = ('Invalid attribute value: {}\nmust be in: {}'.format(value, dlx.rotation_types))
            return str_error
        self.rotation = value
        if not dlx.XML_ELEMENT_CURVE_START_TAG in element:
            str_error = ('Not exists attribute: {}'.format(dlx.XML_ELEMENT_CURVE_START_TAG))
            return str_error
        value_list = element[dlx.XML_ELEMENT_CURVE_START_TAG].split(' ')
        try:
            self.point_start = [float(char) for char in value_list]
        except ValueError:
            str_error = (
                'Attribute: {} must be a list of two float: {}'.
                format(dlx.XML_ELEMENT_CURVE_START_TAG, element[dlx.XML_ELEMENT_CURVE_START_TAG]))
            return str_error
        if len(self.point_start) != 2:
            str_error = (
                'Attribute: {} must be a list of two float: {}'.
                format(dlx.XML_ELEMENT_CURVE_ATTRIBUTE_STA_START_TAG, element[dlx.XML_ELEMENT_CURVE_START_TAG]))
            return str_error
        if dlx.XML_FIRST_COORDINATE_IS_NORTH:
            fc = self.point_start[1]
            sc = self.point_start[0]
            self.point_start = [fc, sc]
        if not dlx.XML_ELEMENT_CURVE_CENTER_TAG in element:
            str_error = ('Not exists attribute: {}'.format(dlx.XML_ELEMENT_CURVE_CENTER_TAG))
            return str_error
        value_list = element[dlx.XML_ELEMENT_CURVE_CENTER_TAG].split(' ')
        try:
            self.point_center = [float(char) for char in value_list]
        except ValueError:
            str_error = (
                'Attribute: {} must be a list of two float: {}'.
                format(dlx.XML_ELEMENT_CURVE_CENTER_TAG, element[dlx.XML_ELEMENT_CURVE_CENTER_TAG]))
            return str_error
        if len(self.point_center) != 2:
            str_error = (
                'Attribute: {} must be a list of two float: {}'.
                format(dlx.XML_ELEMENT_CURVE_CENTER_TAG, element[dlx.XML_ELEMENT_CURVE_CENTER_TAG]))
            return str_error
        if dlx.XML_FIRST_COORDINATE_IS_NORTH:
            fc = self.point_center[1]
            sc = self.point_center[0]
            self.point_center = [fc, sc]
        if not dlx.XML_ELEMENT_CURVE_END_TAG in element:
            str_error = ('Not exists attribute: {}'.format(dlx.XML_ELEMENT_CURVE_END_TAG))
            return str_error
        value_list = element[dlx.XML_ELEMENT_CURVE_END_TAG].split(' ')
        try:
            self.point_end = [float(char) for char in value_list]
        except ValueError:
            str_error = (
                'Attribute: {} must be a list of two float: {}'.
                format(dlx.XML_ELEMENT_CURVE_END_TAG, element[dlx.XML_ELEMENT_CURVE_END_TAG]))
            return str_error
        if len(self.point_end) != 2:
            str_error = (
                'Attribute: {} must be a list of two float: {}'.
                format(dlx.XML_ELEMENT_CURVE_END_TAG, element[dlx.XML_ELEMENT_CURVE_END_TAG]))
            return str_error
        if dlx.XML_FIRST_COORDINATE_IS_NORTH:
            fc = self.point_end[1]
            sc = self.point_end[0]
            self.point_end = [fc, sc]
        if dlx.XML_ELEMENT_CURVE_ATTRIBUTE_CRV_TYPE_TAG in element:
            value = element[dlx.XML_ELEMENT_CURVE_ATTRIBUTE_CRV_TYPE_TAG]
            if not value in dlx.crv_type_types:
                str_error = ('Invalid attribute value: {}\nmust be in: {}'.format(value, dlx.crv_type_types))
                return str_error
            self.curve_type = value
        if dlx.XML_ELEMENT_CURVE_ATTRIBUTE_RADIUS_TAG in element:
            value = element[dlx.XML_ELEMENT_CURVE_ATTRIBUTE_RADIUS_TAG]
            try:
                self.radius = float(value)
            except ValueError:
                str_error = (
                    'Attribute: {} must be a float: {}'.
                    format(dlx.XML_ELEMENT_CURVE_ATTRIBUTE_RADIUS_TAG, value))
                return str_error
        if dlx.XML_ELEMENT_CURVE_ATTRIBUTE_LENGTH_TAG in element:
            value = element[dlx.XML_ELEMENT_CURVE_ATTRIBUTE_LENGTH_TAG]
            try:
                self.length = float(value)
            except ValueError:
                str_error = (
                    'Attribute: {} must be a float: {}'.
                    format(dlx.XML_ELEMENT_CURVE_ATTRIBUTE_LENGTH_TAG, value))
                return str_error
        if dlx.XML_ELEMENT_CURVE_ATTRIBUTE_DIR_START_TAG in element:
            value = element[dlx.XML_ELEMENT_CURVE_ATTRIBUTE_DIR_START_TAG]
            try:
                self.direction_start = float(value)
            except ValueError:
                str_error = (
                    'Attribute: {} must be a float: {}'.
                    format(dlx.XML_ELEMENT_CURVE_ATTRIBUTE_DIR_START_TAG, value))
                return str_error
        if dlx.XML_ELEMENT_CURVE_ATTRIBUTE_DIR_END_TAG in element:
            value = element[dlx.XML_ELEMENT_CURVE_ATTRIBUTE_DIR_END_TAG]
            try:
                self.direction_end = float(value)
            except ValueError:
                str_error = (
                    'Attribute: {} must be a float: {}'.
                    format(dlx.XML_ELEMENT_CURVE_ATTRIBUTE_DIR_END_TAG, value))
                return str_error
        return str_error
