# authors:
# David Hernandez Lopez, david.hernandez@uclm.es

import numpy as np

from . import defs_landxml as dlx

# http://www.landxml.org/schema/landxml-1.2/documentation/LandXML-1.2Doc_CrossSectSurf.html#Link07F1F4F0
class CrossSectionSurface:
    def __init__(self, cross_section):
        self.cross_section = cross_section
        self.name = None
        self.description = None
        self.state = None
        self.feature_code = None
        self.feature_text = None
        self.point_center = None
        self.point_left = None
        self.point_right = None
        self.values_by_distance_to_center_mm = None # [dis_to_axis, elevation], negative left, 0 center
        self.points_by_distance_to_center_mm = None # [fc, sc, elevation]
        self.computed_parameters = False
        self.as_linestring = None

    def compute_parameters(self):
        str_error = ''
        if self.computed_parameters:
            return str_error
        if self.values_by_distance_to_center_mm is None:
            str_error = ('Points object in CrossSection is not initialized.')
            return str_error
        left_clossest_distance_mm = -100000
        right_clossest_distance_mm = 100000
        tolerance_to_axis = 0.01
        find_center = False
        distance_center_mm = None
        for distance_mm in self.values_by_distance_to_center_mm:
            if np.abs(distance_mm) < tolerance_to_axis:
                find_center = True
                distance_center_mm = distance_mm
            elif distance_mm < 0:
                if np.abs(distance_mm) < np.abs(left_clossest_distance_mm):
                    left_clossest_distance_mm = distance_mm
            else:
                if distance_mm < right_clossest_distance_mm:
                    right_clossest_distance_mm = distance_mm
        if not find_center:
            dl = self.values_by_distance_to_center_mm[left_clossest_distance_mm][0]
            el = self.values_by_distance_to_center_mm[right_clossest_distance_mm][1]
            dr = self.values_by_distance_to_center_mm[right_clossest_distance_mm][0]
            er = self.values_by_distance_to_center_mm[right_clossest_distance_mm][1]
            slope = (er - el) / (dr - dl)
            ec = el - slope * dl # minus because dl is negative
            self.values_by_distance_to_center_mm[0] = [0.0, ec]
            distance_center_mm = 0
        points_by_distance_to_center_mm = {}
        [point_axis_fc, point_axis_sc, point_axis_elevation] = self.cross_section.point_axis
        for distance_mm in self.values_by_distance_to_center_mm:
            point = None
            if distance_mm == distance_center_mm:
                point = [point_axis_fc, point_axis_sc, 0.0]
                point[2] = self.values_by_distance_to_center_mm[distance_mm][1]
                self.point_center = point
            else:
                distance = self.values_by_distance_to_center_mm[distance_mm][0]
                azimuth = azimuth = self.cross_section.azimuth + np.pi / 2
                if distance_mm < 0:
                    azimuth = azimuth - np.pi
                    distance = -1. * distance
                fc = point_axis_fc + distance * np.sin(azimuth)
                sc = point_axis_sc + distance * np.cos(azimuth)
                elevation = self.values_by_distance_to_center_mm[distance_mm][1]
                point = [fc, sc, elevation]
            points_by_distance_to_center_mm[distance_mm] = point
        self.points_by_distance_to_center_mm = dict(sorted(points_by_distance_to_center_mm.items()))
        keys_as_list = list(self.points_by_distance_to_center_mm)
        self.point_left = self.points_by_distance_to_center_mm[keys_as_list[0]]
        self.point_right = self.points_by_distance_to_center_mm[keys_as_list[len(keys_as_list) - 1]]
        self.as_linestring = 'LINESTRING('
        for i in range(len(keys_as_list)):
            if i > 0:
                self.as_linestring += ','
            pto = self.points_by_distance_to_center_mm[keys_as_list[i]]
            self.as_linestring += ('{:4f} {:4f} {:4f}'.format(pto[0], pto[1], pto[2]))
        self.as_linestring += ')'
        self.computed_parameters = True
        return str_error

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
        values_by_distance_to_center_mm = {}
        nop = int(len(values) / 2)
        for i in range(nop):
            distance_to_center_mm = int(values[i*2] * 1000.)
            values_by_distance_to_center_mm[distance_to_center_mm] = [values[i * 2], values[i * 2 + 1]]
        self.values_by_distance_to_center_mm = dict(
            sorted(values_by_distance_to_center_mm.items()))
        return str_error






