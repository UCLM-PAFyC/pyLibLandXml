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

class Line:
    def __init__(self, aligment):
        self.aligment = aligment
        self.sta_start = None
        self.length = None
        self.dir = None
        self.start = None  # point
        self.end = None  # point

    def set_from_landxml_element(self,
                                 element):
        str_error = ''
        if not dlx.XML_ELEMENT_LINE_ATTRIBUTE_STA_START_TAG in element:
            str_error = ('Not exists attribute: {}'.format(dlx.XML_ELEMENT_LINE_ATTRIBUTE_STA_START_TAG))
            return str_error
        value = element[dlx.XML_ELEMENT_LINE_ATTRIBUTE_STA_START_TAG]
        try:
            self.sta_start = float(value)
        except ValueError:
            str_error = (
                'Attribute: {} must be a float: {}'.
                format(dlx.XML_ELEMENT_LINE_ATTRIBUTE_STA_START_TAG, value))
            return str_error
        if not dlx.XML_ELEMENT_LINE_START_TAG in element:
            str_error = ('Not exists attribute: {}'.format(dlx.XML_ELEMENT_LINE_START_TAG))
            return str_error
        value_list = element[dlx.XML_ELEMENT_LINE_START_TAG].split(' ')
        try:
            self.start = [float(char) for char in value_list]
        except ValueError:
            str_error = (
                'Attribute: {} must be a list of two float: {}'.
                format(dlx.XML_ELEMENT_LINE_START_TAG, element[dlx.XML_ELEMENT_LINE_START_TAG]))
            return str_error
        if len(self.start) != 2:
            str_error = (
                'Attribute: {} must be a list of two float: {}'.
                format(dlx.XML_ELEMENT_LINE_ATTRIBUTE_STA_START_TAG, element[dlx.XML_ELEMENT_LINE_START_TAG]))
            return str_error
        if not dlx.XML_ELEMENT_LINE_END_TAG in element:
            str_error = ('Not exists attribute: {}'.format(dlx.XML_ELEMENT_LINE_END_TAG))
            return str_error
        value_list = element[dlx.XML_ELEMENT_LINE_END_TAG].split(' ')
        try:
            self.end = [float(char) for char in value_list]
        except ValueError:
            str_error = (
                'Attribute: {} must be a list of two float: {}'.
                format(dlx.XML_ELEMENT_LINE_END_TAG, element[dlx.XML_ELEMENT_LINE_END_TAG]))
            return str_error
        if len(self.end) != 2:
            str_error = (
                'Attribute: {} must be a list of two float: {}'.
                format(dlx.XML_ELEMENT_LINE_END_TAG, element[dlx.XML_ELEMENT_LINE_END_TAG]))
            return str_error
        if dlx.XML_ELEMENT_LINE_ATTRIBUTE_LENGTH_TAG in element:
            value = element[dlx.XML_ELEMENT_LINE_ATTRIBUTE_LENGTH_TAG]
            try:
                self.length = float(value)
            except ValueError:
                str_error = (
                    'Attribute: {} must be a float: {}'.
                    format(dlx.XML_ELEMENT_LINE_ATTRIBUTE_LENGTH_TAG, value))
                return str_error
        if dlx.XML_ELEMENT_LINE_ATTRIBUTE_DIR_TAG in element:
            value = element[dlx.XML_ELEMENT_LINE_ATTRIBUTE_DIR_TAG]
            try:
                self.dir = float(value)
            except ValueError:
                str_error = (
                    'Attribute: {} must be a float: {}'.
                    format(dlx.XML_ELEMENT_LINE_ATTRIBUTE_DIR_TAG, value))
                return str_error
        return str_error