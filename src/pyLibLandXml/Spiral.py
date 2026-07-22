# authors:
# David Hernandez Lopez, david.hernandez@uclm.es

import numpy as np
from pyclothoids import Clothoid

from . import defs_landxml as dlx

# http://www.landxml.org/schema/landxml-1.2/documentation/LandXML-1.2Doc_Spiral.html
class Spiral:
    def __init__(self, aligment):
        self.aligment = aligment
        self.start_cumulative_distance = None
        self.description = None
        self.rotation = None
        self.spiral_type = None
        self.constant = None
        self.length = None
        self.direction_start = None
        self.direction_end = None
        self.radius_start = None
        self.radius_end = None
        self.point_start = None  # point
        self.point_intersection = None  # point
        self.point_end = None  # point
        self.tx = None
        self.ty = None
        self.xpi = None
        self.ypi = None
        self.x0 = None
        self.y0 = None
        self.x1 = None
        self.y1 = None
        self.azi_0_pi = None
        self.t0 = None
        self.azi_1_pi = None
        self.t1 = None
        self.t1 = None
        self.clothoid = None
        self.computed_parameters = False
        self.computed_cumulative_distance_end = None

    def compute_parameters(self):
        str_error = None
        if self.computed_parameters:
            return str_error
        if self.point_start is None:
            str_error = "Object Spiral is not initialized"
            return str_error
        xpi = self.point_intersection[0]
        ypi = self.point_intersection[1]
        x0 = self.point_start[0]
        y0 = self.point_start[1]
        x1 = self.point_end[0]
        y1 = self.point_end[1]
        tx = x0
        if x1 < tx:
            tx = x1
        if xpi < tx:
            tx = xpi
        ty = y0
        if y1 < ty:
            ty = y1
        if ypi < ty:
            ty = ypi
        self.tx = tx
        self.ty = ty
        self.xpi = xpi - tx
        self.ypi = ypi - ty
        self.x0 = x0 - tx
        self.y0 = y0 - ty
        self.x1 = x1 - tx
        self.y1 = y1 - ty
        self.azi_0_pi = np.arctan2(xpi - x0, ypi - y0)
        self.t0 = np.pi / 2. - self.azi_0_pi
        self.azi_1_pi = np.arctan2(xpi - x1, ypi - y1)
        self.t1 = np.pi / 2. - self.azi_1_pi
        self.t1 = self.t1 + np.pi
        self.clothoid = Clothoid.G1Hermite(self.x0, self.y0, self.t0, self.x1, self.y1, self.t1)
        self.computed_cumulative_distance_end = self.start_cumulative_distance + self.length
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
        s = cumulative_distance - self.start_cumulative_distance
        fc = self.clothoid.X(s)
        sc = self.clothoid.Y(s)
        fc = fc + self.tx
        sc = sc + self.ty
        point = [fc, sc]
        return str_error, point

    def set_from_landxml_element(self,
                                 element):
        str_error = ''
        if not dlx.XML_ELEMENT_SPIRAL_ATTRIBUTE_STA_START_TAG in element:
            str_error = ('Not exists attribute: {}'.format(dlx.XML_ELEMENT_SPIRAL_ATTRIBUTE_STA_START_TAG))
            return str_error
        value = element[dlx.XML_ELEMENT_SPIRAL_ATTRIBUTE_STA_START_TAG]
        try:
            self.start_cumulative_distance = float(value)
        except ValueError:
            str_error = (
                'Attribute: {} must be a float: {}'.
                format(dlx.XML_ELEMENT_SPIRAL_ATTRIBUTE_STA_START_TAG, value))
            return str_error
        if not dlx.XML_ELEMENT_SPIRAL_ATTRIBUTE_LENGTH_TAG in element:
            str_error = ('Not exists attribute: {}'.format(dlx.XML_ELEMENT_SPIRAL_ATTRIBUTE_LENGTH_TAG))
            return str_error
        value = element[dlx.XML_ELEMENT_SPIRAL_ATTRIBUTE_LENGTH_TAG]
        try:
            self.length = float(value)
        except ValueError:
            str_error = (
                'Attribute: {} must be a float: {}'.
                format(dlx.XML_ELEMENT_SPIRAL_ATTRIBUTE_LENGTH_TAG, value))
            return str_error
        if dlx.XML_ELEMENT_SPIRAL_ATTRIBUTE_DESC_TAG in element:
            self.description = element[dlx.XML_ELEMENT_SPIRAL_ATTRIBUTE_DESC_TAG]
        if not dlx.XML_ELEMENT_SPIRAL_ATTRIBUTE_ROT_TAG in element:
            str_error = ('Not exists attribute: {}'.format(dlx.XML_ELEMENT_SPIRAL_ATTRIBUTE_ROT_TAG))
            return str_error
        value = element[dlx.XML_ELEMENT_SPIRAL_ATTRIBUTE_ROT_TAG]
        if not value in dlx.rotation_types:
            str_error = ('Invalid attribute value: {}\nmust be in: {}'.format(value, dlx.rotation_types))
            return str_error
        self.rotation = value
        if not dlx.XML_ELEMENT_SPIRAL_START_TAG in element:
            str_error = ('Not exists attribute: {}'.format(dlx.XML_ELEMENT_SPIRAL_START_TAG))
            return str_error
        value_list = element[dlx.XML_ELEMENT_SPIRAL_START_TAG].split(' ')
        try:
            self.point_start = [float(char) for char in value_list]
        except ValueError:
            str_error = (
                'Attribute: {} must be a list of two float: {}'.
                format(dlx.XML_ELEMENT_SPIRAL_START_TAG, element[dlx.XML_ELEMENT_SPIRAL_START_TAG]))
            return str_error
        if len(self.point_start) != 2:
            str_error = (
                'Attribute: {} must be a list of two float: {}'.
                format(dlx.XML_ELEMENT_SPIRAL_ATTRIBUTE_STA_START_TAG, element[dlx.XML_ELEMENT_SPIRAL_START_TAG]))
            return str_error
        if dlx.XML_FIRST_COORDINATE_IS_NORTH:
            fc = self.point_start[1]
            sc = self.point_start[0]
            self.point_start = [fc, sc]
        if not dlx.XML_ELEMENT_SPIRAL_PI_TAG in element:
            str_error = ('Not exists attribute: {}'.format(dlx.XML_ELEMENT_SPIRAL_PI_TAG))
            return str_error
        value_list = element[dlx.XML_ELEMENT_SPIRAL_PI_TAG].split(' ')
        try:
            self.point_intersection = [float(char) for char in value_list]
        except ValueError:
            str_error = (
                'Attribute: {} must be a list of two float: {}'.
                format(dlx.XML_ELEMENT_SPIRAL_PI_TAG, element[dlx.XML_ELEMENT_SPIRAL_PI_TAG]))
            return str_error
        if len(self.point_intersection) != 2:
            str_error = (
                'Attribute: {} must be a list of two float: {}'.
                format(dlx.XML_ELEMENT_SPIRAL_PI_TAG, element[dlx.XML_ELEMENT_SPIRAL_PI_TAG]))
            return str_error
        if dlx.XML_FIRST_COORDINATE_IS_NORTH:
            fc = self.point_intersection[1]
            sc = self.point_intersection[0]
            self.point_intersection = [fc, sc]
        if not dlx.XML_ELEMENT_SPIRAL_END_TAG in element:
            str_error = ('Not exists attribute: {}'.format(dlx.XML_ELEMENT_SPIRAL_END_TAG))
            return str_error
        value_list = element[dlx.XML_ELEMENT_SPIRAL_END_TAG].split(' ')
        try:
            self.point_end = [float(char) for char in value_list]
        except ValueError:
            str_error = (
                'Attribute: {} must be a list of two float: {}'.
                format(dlx.XML_ELEMENT_SPIRAL_END_TAG, element[dlx.XML_ELEMENT_SPIRAL_END_TAG]))
            return str_error
        if len(self.point_end) != 2:
            str_error = (
                'Attribute: {} must be a list of two float: {}'.
                format(dlx.XML_ELEMENT_SPIRAL_END_TAG, element[dlx.XML_ELEMENT_SPIRAL_END_TAG]))
            return str_error
        if dlx.XML_FIRST_COORDINATE_IS_NORTH:
            fc = self.point_end[1]
            sc = self.point_end[0]
            self.point_end = [fc, sc]
        if not dlx.XML_ELEMENT_SPIRAL_ATTRIBUTE_SPI_TYPE_TAG in element:
            str_error = ('Not exists attribute: {}'.format(dlx.XML_ELEMENT_SPIRAL_ATTRIBUTE_SPI_TYPE_TAG))
            return str_error
        value = element[dlx.XML_ELEMENT_SPIRAL_ATTRIBUTE_SPI_TYPE_TAG]
        if not value in dlx.spi_type_types:
            str_error = ('Invalid attribute value: {}\nmust be in: {}'.format(value, dlx.spi_type_types))
            return str_error
        self.spiral_type = value
        if not dlx.XML_ELEMENT_SPIRAL_ATTRIBUTE_RADIUS_START_TAG in element:
            str_error = ('Not exists attribute: {}'.format(dlx.XML_ELEMENT_SPIRAL_ATTRIBUTE_RADIUS_START_TAG))
            return str_error
        value = element[dlx.XML_ELEMENT_SPIRAL_ATTRIBUTE_RADIUS_START_TAG]
        try:
            self.radius_start = float(value)
        except ValueError:
            str_error = (
                'Attribute: {} must be a float: {}'.
                format(dlx.XML_ELEMENT_SPIRAL_ATTRIBUTE_RADIUS_START_TAG, value))
            return str_error
        if not dlx.XML_ELEMENT_SPIRAL_ATTRIBUTE_RADIUS_END_TAG in element:
            str_error = ('Not exists attribute: {}'.format(dlx.XML_ELEMENT_SPIRAL_ATTRIBUTE_RADIUS_END_TAG))
            return str_error
        value = element[dlx.XML_ELEMENT_SPIRAL_ATTRIBUTE_RADIUS_END_TAG]
        try:
            self.radius_end = float(value)
        except ValueError:
            str_error = (
                'Attribute: {} must be a float: {}'.
                format(dlx.XML_ELEMENT_SPIRAL_ATTRIBUTE_RADIUS_END_TAG, value))
            return str_error
        if dlx.XML_ELEMENT_SPIRAL_ATTRIBUTE_DIR_START_TAG in element:
            value = element[dlx.XML_ELEMENT_SPIRAL_ATTRIBUTE_DIR_START_TAG]
            try:
                self.direction_start = float(value)
            except ValueError:
                str_error = (
                    'Attribute: {} must be a float: {}'.
                    format(dlx.XML_ELEMENT_SPIRAL_ATTRIBUTE_DIR_START_TAG, value))
                return str_error
        if dlx.XML_ELEMENT_SPIRAL_ATTRIBUTE_DIR_END_TAG in element:
            value = element[dlx.XML_ELEMENT_SPIRAL_ATTRIBUTE_DIR_END_TAG]
            try:
                self.direction_end = float(value)
            except ValueError:
                str_error = (
                    'Attribute: {} must be a float: {}'.
                    format(dlx.XML_ELEMENT_SPIRAL_ATTRIBUTE_DIR_END_TAG, value))
                return str_error
        return str_error


