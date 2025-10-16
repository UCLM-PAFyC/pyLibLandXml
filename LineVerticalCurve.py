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

# http://www.landxml.org/schema/landxml-1.2/documentation/LandXML-1.2Doc_ParaCurve.html
class LineVerticalCurve:
    def __init__(self,
                 profile_aligment):
        self.profile_aligment = profile_aligment
        self.start_cumulative_distance = None
        self.computed_cumulative_distance_end = None
        self.elevation_start = None
        self.elevation_end = None
        self.slope = None
        self.computed_parameters = False

    def compute_elevation_from_cumulative_distance(self,
                                                   cumulative_distance):
        str_error = ''
        elevation = None
        if not self.computed_parameters:
            str_error = ('LineVerticalCurve object is not initialized.')
            if str_error:
                return str_error, elevation
        if cumulative_distance < self.start_cumulative_distance:
            str_error = ('Input cumulative distance: {}\nis less than start cumulative distance: {}.'.
                         format(cumulative_distance, self.start_cumulative_distance))
            return str_error, elevation
        if cumulative_distance > self.computed_cumulative_distance_end:
            str_error = ('Input cumulative distance: {}\nis less than computed cumulative end: {}.'.
                         format(cumulative_distance, self.computed_cumulative_distance_end))
            return str_error, elevation
        elevation = self.elevation_start + self.slope * (cumulative_distance - self.start_cumulative_distance)
        return str_error, elevation
