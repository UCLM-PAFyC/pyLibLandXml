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

class Curve:
    def __init__(self, aligment):
        self.aligment = aligment
        self.sta_start = None
        self.rot = None
        self.crv_type = None
        self.radius = None
        self.length = None
        self.dir_start = None
        self.dir_end = None
        self.start = None  # point
        self.center = None  # point
        self.end = None  # point

    def set_from_landxml_element(self,
                                 element):
        str_error = ''
        if not dlx.XML_ELEMENT_CURVE_ATTRIBUTE_STA_START_TAG in element:
            str_error = ('Not exists attribute: {}'.format(dlx.XML_ELEMENT_CURVE_ATTRIBUTE_STA_START_TAG))
            return str_error
        value = element[dlx.XML_ELEMENT_CURVE_ATTRIBUTE_STA_START_TAG]
        try:
            self.sta_start = float(value)
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
        self.rot = value
        if not dlx.XML_ELEMENT_CURVE_START_TAG in element:
            str_error = ('Not exists attribute: {}'.format(dlx.XML_ELEMENT_CURVE_START_TAG))
            return str_error
        value_list = element[dlx.XML_ELEMENT_CURVE_START_TAG].split(' ')
        try:
            self.start = [float(char) for char in value_list]
        except ValueError:
            str_error = (
                'Attribute: {} must be a list of two float: {}'.
                format(dlx.XML_ELEMENT_CURVE_START_TAG, element[dlx.XML_ELEMENT_CURVE_START_TAG]))
            return str_error
        if len(self.start) != 2:
            str_error = (
                'Attribute: {} must be a list of two float: {}'.
                format(dlx.XML_ELEMENT_CURVE_ATTRIBUTE_STA_START_TAG, element[dlx.XML_ELEMENT_CURVE_START_TAG]))
            return str_error
        if not dlx.XML_ELEMENT_CURVE_CENTER_TAG in element:
            str_error = ('Not exists attribute: {}'.format(dlx.XML_ELEMENT_CURVE_CENTER_TAG))
            return str_error
        value_list = element[dlx.XML_ELEMENT_CURVE_CENTER_TAG].split(' ')
        try:
            self.center = [float(char) for char in value_list]
        except ValueError:
            str_error = (
                'Attribute: {} must be a list of two float: {}'.
                format(dlx.XML_ELEMENT_CURVE_CENTER_TAG, element[dlx.XML_ELEMENT_CURVE_CENTER_TAG]))
            return str_error
        if len(self.center) != 2:
            str_error = (
                'Attribute: {} must be a list of two float: {}'.
                format(dlx.XML_ELEMENT_CURVE_CENTER_TAG, element[dlx.XML_ELEMENT_CURVE_CENTER_TAG]))
            return str_error
        if not dlx.XML_ELEMENT_CURVE_END_TAG in element:
            str_error = ('Not exists attribute: {}'.format(dlx.XML_ELEMENT_CURVE_END_TAG))
            return str_error
        value_list = element[dlx.XML_ELEMENT_CURVE_END_TAG].split(' ')
        try:
            self.end = [float(char) for char in value_list]
        except ValueError:
            str_error = (
                'Attribute: {} must be a list of two float: {}'.
                format(dlx.XML_ELEMENT_CURVE_END_TAG, element[dlx.XML_ELEMENT_CURVE_END_TAG]))
            return str_error
        if len(self.end) != 2:
            str_error = (
                'Attribute: {} must be a list of two float: {}'.
                format(dlx.XML_ELEMENT_CURVE_END_TAG, element[dlx.XML_ELEMENT_CURVE_END_TAG]))
            return str_error
        if dlx.XML_ELEMENT_CURVE_ATTRIBUTE_CRV_TYPE_TAG in element:
            value = element[dlx.XML_ELEMENT_CURVE_ATTRIBUTE_CRV_TYPE_TAG]
            if not value in dlx.crv_type_types:
                str_error = ('Invalid attribute value: {}\nmust be in: {}'.format(value, dlx.crv_type_types))
                return str_error
            self.crv_type = value
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
                self.dir_start = float(value)
            except ValueError:
                str_error = (
                    'Attribute: {} must be a float: {}'.
                    format(dlx.XML_ELEMENT_CURVE_ATTRIBUTE_DIR_START_TAG, value))
                return str_error
        if dlx.XML_ELEMENT_CURVE_ATTRIBUTE_DIR_END_TAG in element:
            value = element[dlx.XML_ELEMENT_CURVE_ATTRIBUTE_DIR_END_TAG]
            try:
                self.dir_end = float(value)
            except ValueError:
                str_error = (
                    'Attribute: {} must be a float: {}'.
                    format(dlx.XML_ELEMENT_CURVE_ATTRIBUTE_DIR_END_TAG, value))
                return str_error
        return str_error
