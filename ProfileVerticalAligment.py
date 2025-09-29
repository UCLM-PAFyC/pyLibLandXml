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
from ParabolicVerticalCurve import ParabolicVerticalCurve

# http://www.landxml.org/schema/landxml-1.2/documentation/LandXML-1.2Doc_ProfAlign.html
class ProfileVerticalAligment:
    def __init__(self, aligment):
        self.aligment = aligment
        self.name = None
        self.points_vertical_intersection_by_cumulative_distance_mm = None # [cumulative distance, elevation] ¿puede estar vacio? de momento supongo que no, al menos origen y fin
        self.parabolic_vertical_curve_by_cumulative_distance_mm = None # ¿puede estar vacio? de momento supongo que no, al menos uno, ¿recta?
        self.start_cumulative_distance = None # min acumulative distance

    def set_from_landxml_element(self,
                                 element):
        str_error = ''
        if not dlx.XML_ELEMENT_PROFILE_PROF_ALIGN_ATTRIBUTE_NAME_TAG in element:
            str_error = ('Not exists attribute: {}'.format(dlx.XML_ELEMENT_PROFILE_PROF_ALIGN_ATTRIBUTE_NAME_TAG))
            return str_error
        self.name = element[dlx.XML_ELEMENT_PROFILE_PROF_ALIGN_ATTRIBUTE_NAME_TAG]
        if not dlx.XML_ELEMENT_PROFILE_PROF_ALIGN_PVI_TAG in element:
            str_error = ('Not exists attribute: {}'.format(dlx.XML_ELEMENT_PROFILE_PROF_ALIGN_PVI_TAG))
            return str_error
        # if dlx.XML_ELEMENT_PROFILE_PROF_ALIGN_PVI_TAG in element:
        element_pvi = element[dlx.XML_ELEMENT_PROFILE_PROF_ALIGN_PVI_TAG]
        if not isinstance(element_pvi, list):
            str_error = ('Attribute: {} must be a list'.format(dlx.XML_ELEMENT_PROFILE_PROF_ALIGN_PVI_TAG))
            return str_error
        points_vertical_intersection = {}
        for i in range(len(element_pvi)):
            value_list = element_pvi[i].split(' ')
            try:
                pvi = [float(char) for char in value_list]
            except ValueError:
                str_error = (
                    'Attribute: {} in position: {} must be a list of two float: {}'.
                    format(dlx.XML_ELEMENT_CURVE_CENTER_TAG, str(i + 1),
                           element[dlx.XML_ELEMENT_CURVE_CENTER_TAG]))
                return str_error
            if len(pvi) != 2:
                str_error = (
                    'Attribute: {} in position: {} must be a list of two float: {}'.
                    format(dlx.XML_ELEMENT_CURVE_CENTER_TAG, str(i + 1),
                           element[dlx.XML_ELEMENT_CURVE_CENTER_TAG]))
                return str_error
            cumulative_distance_mm_int = int(pvi[0] * 1000.0)
            points_vertical_intersection[cumulative_distance_mm_int] = pvi
        if len(points_vertical_intersection) < 2:
            str_error = (
                'Attribute: {} must be a list of two or more points'.format(dlx.XML_ELEMENT_PROFILE_PROF_ALIGN_PVI_TAG))
            return str_error
        self.points_vertical_intersection_by_cumulative_distance_mm = dict(sorted(points_vertical_intersection.items()))
        self.start_cumulative_distance = next(iter(self.points_vertical_intersection_by_cumulative_distance_mm))
        self.start_cumulative_distance = self.start_cumulative_distance / 1000.0
        if not dlx.XML_ELEMENT_PROFILE_PROF_ALIGN_PARA_CURVE_TAG in element:
            str_error = ('Not exists attribute: {}'.format(dlx.XML_ELEMENT_PROFILE_PROF_ALIGN_PARA_CURVE_TAG))
            return str_error
        element_para_curve = element[dlx.XML_ELEMENT_PROFILE_PROF_ALIGN_PARA_CURVE_TAG]
        para_curve_list = []
        if isinstance(element_para_curve, list):
            para_curve_list = element_para_curve
        else:
            para_curve_list.append(element_para_curve)
        parabolic_vertical_curve_by_cumulative_distance = {}
        for i in range(len(para_curve_list)):
            para_curve_element = para_curve_list[i]
            if not isinstance(para_curve_element, dict):
                str_error = ('In position: {} attribute: {} must be a dictionary'
                             .format(str(i + 1), dlx.XML_ELEMENT_PROFILE_PROF_ALIGN_PARA_CURVE_TAG))
                return str_error
            if not dlx.XML_ELEMENT_PROFILE_PROF_ALIGN_PARA_CURVE_ATTRIBUTE_LENGTH_TAG in para_curve_element:
                str_error = ('Not exists attribute: {} in position: {} attribute: {}'
                             .format(dlx.XML_ELEMENT_PROFILE_PROF_ALIGN_PARA_CURVE_ATTRIBUTE_LENGTH_TAG,
                                     str(i + 1), dlx.XML_ELEMENT_PROFILE_PROF_ALIGN_PARA_CURVE_TAG))
                return str_error
            value = para_curve_element[dlx.XML_ELEMENT_PROFILE_PROF_ALIGN_PARA_CURVE_ATTRIBUTE_LENGTH_TAG]
            length = None
            try:
                length = float(value)
            except ValueError:
                str_error = ('Attribute: {} in position: {} in attribute: {} must be a float'
                             .format(dlx.XML_ELEMENT_PROFILE_PROF_ALIGN_PARA_CURVE_ATTRIBUTE_LENGTH_TAG,
                                     str(i + 1), dlx.XML_ELEMENT_PROFILE_PROF_ALIGN_PARA_CURVE_TAG))
                return str_error
            desc = ''
            if dlx.XML_ELEMENT_PROFILE_PROF_ALIGN_PARA_CURVE_ATTRIBUTE_DESC_TAG in para_curve_element:
                value = para_curve_element[dlx.XML_ELEMENT_PROFILE_PROF_ALIGN_PARA_CURVE_ATTRIBUTE_DESC_TAG]
                desc = value
                # desc = None
                # try:
                #     desc = float(value)
                # except ValueError:
                #     str_error = ('Attribute: {} in position: {} in attribute: {} must be a float'
                #                  .format(dlx.XML_ELEMENT_PROFILE_PROF_ALIGN_PARA_CURVE_ATTRIBUTE_DESC_TAG,
                #                          str(i + 1), dlx.XML_ELEMENT_PROFILE_PROF_ALIGN_PARA_CURVE_TAG))
                #     return str_error
            if not dlx.XML_ELEMENT_PROFILE_PROF_ALIGN_PARA_CURVE_TEXT_TAG in para_curve_element:
                str_error = ('Not exists element: {} in position: {} attribute: {}'
                             .format(dlx.XML_ELEMENT_PROFILE_PROF_ALIGN_PARA_CURVE_TEXT_TAG,
                                     str(i + 1), dlx.XML_ELEMENT_PROFILE_PROF_ALIGN_PARA_CURVE_TAG))
                return str_error
            value = para_curve_element[dlx.XML_ELEMENT_PROFILE_PROF_ALIGN_PARA_CURVE_TEXT_TAG]
            value_list = value.split(' ')
            text_values = None
            try:
                text_values = [float(char) for char in value_list]
            except ValueError:
                str_error = ('Attribute: {} in position: {} in attribute: {} must be a list of two float'
                             .format(dlx.XML_ELEMENT_PROFILE_PROF_ALIGN_PARA_CURVE_TEXT_TAG,
                                     str(i + 1), dlx.XML_ELEMENT_PROFILE_PROF_ALIGN_PARA_CURVE_TAG))
                return str_error
            if len(text_values) != 2:
                str_error = ('Attribute: {} in position: {} in attribute: {} must be a list of two float'
                             .format(dlx.XML_ELEMENT_PROFILE_PROF_ALIGN_PARA_CURVE_TEXT_TAG,
                                     str(i + 1), dlx.XML_ELEMENT_PROFILE_PROF_ALIGN_PARA_CURVE_TAG))
                return str_error
            cumulative_distance = text_values[0]
            elevation = text_values[1]
            parabolic_vertical_curve = ParabolicVerticalCurve(self, length, desc, cumulative_distance, elevation)
            cumulative_distance_mm_int = int(cumulative_distance * 1000.)
            parabolic_vertical_curve_by_cumulative_distance[cumulative_distance_mm_int] = parabolic_vertical_curve
        self.parabolic_vertical_curve_by_cumulative_distance_mm \
            = dict(sorted(parabolic_vertical_curve_by_cumulative_distance.items()))
        return str_error






