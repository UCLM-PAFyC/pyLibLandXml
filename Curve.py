# authors:
# David Hernandez Lopez, david.hernandez@uclm.es

import os, sys
import math
import pathlib
import datetime
import json
import xmltodict
import numpy as np

current_path = os.path.dirname(os.path.realpath(__file__))
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
        self.computed_radius = None
        self.computed_azimuth_start = None
        self.computed_azimuth_end = None
        self.computed_curve_angle = None
        self.computed_cumulative_distance_end = None
        # self.computed_cumulative_distance_start = None
        self.computed_parameters = False

    def compute_parameters(self):
        str_error = ''
        if self.computed_parameters:
            return str_error
        if self.point_start is None:
            str_error = 'Object curve is not initialized'
            return str_error
        self.computed_radius = np.sqrt((self.point_start[0] - self.point_center[0]) ** 2.
                                       + (self.point_start[1] - self.point_center[1]) ** 2.)
        self.computed_azimuth_start = np.arctan2(self.point_start[0] - self.point_center[0],
                                                 self.point_start[1] - self.point_center[1])
        if self.computed_azimuth_start < 0:
            self.computed_azimuth_start += 2 * math.pi
        self.computed_azimuth_end = np.arctan2(self.point_end[0] - self.point_center[0],
                                               self.point_end[1] - self.point_center[1])
        if self.computed_azimuth_end < 0:
            self.computed_azimuth_end += 2 * math.pi
        self.computed_curve_angle = np.abs(self.computed_azimuth_end - self.computed_azimuth_start)
        self.computed_cumulative_distance_end = (self.start_cumulative_distance
                                                 + self.computed_curve_angle * self.computed_radius)
        self.computed_parameters = True
        return str_error

    def compute_point_from_cumulative_distance(self,
                                               cumulative_distance):
        str_error = ''
        point = None
        if not self.computed_parameters:
            str_error = self.compute_parameters()
            if str_error:
                return str_error, point
        if cumulative_distance < self.start_cumulative_distance:
            str_error = ('Input cumulative distance: {}\nis less than start cumulative distance: {}.'.
                         format(cumulative_distance, self.start_cumulative_distance))
            return str_error, point
        if cumulative_distance > self.computed_cumulative_distance_end:
            str_error = ('Input cumulative distance: {}\nis less than computed cumulative end: {}.'.
                         format(cumulative_distance, self.computed_cumulative_distance_end))
            return str_error, point
        angle_pto = (cumulative_distance - self.start_cumulative_distance) / self.computed_radius
        azi_pto = self.computed_azimuth_start + angle_pto
        if self.rotation.casefold() == dlx.rotation_type_ccw.casefold():
            azi_pto = self.computed_azimuth_start - angle_pto
        fc = self.point_center[0] + self.computed_radius * np.sin(azi_pto)
        sc = self.point_center[1] + self.computed_radius * np.cos(azi_pto)
        point = [fc, sc]
        return str_error, point

    # def set_axis_points(self,
    #                     cumulative_distance,
    #                     points_distance):
    #     str_error = ''
    #     axis_points_by_cumulative_distance_mm = {}
    #     if (cumulative_distance - self.start_cumulative_distance) < dlx.CUMULATIVE_DISTANCE_IGNORE_FIRST_POINT_TOLERANCE:
    #         cumulative_distance = cumulative_distance + points_distance
    #     if not self.computed_parameters:
    #         str_error = self.compute_parameters()
    #         if str_error:
    #             return str_error, axis_points_by_cumulative_distance_mm
    #     while cumulative_distance < self.computed_cumulative_distance_end:
    #         if ((self.computed_cumulative_distance_end - cumulative_distance)
    #                 < dlx.CUMULATIVE_DISTANCE_IGNORE_FIRST_POINT_TOLERANCE):
    #             break
    #         str_error, point = self.compute_point_from_cumulative_distance(cumulative_distance)
    #         axis_points_by_cumulative_distance_mm[int(cumulative_distance * 1000.)] = point
    #         cumulative_distance = cumulative_distance + points_distance
    #     axis_points_by_cumulative_distance_mm[int(self.computed_cumulative_distance_end * 1000.)] = self.point_end
    #     return str_error, axis_points_by_cumulative_distance_mm, cumulative_distance

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
