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
from Aligment import Aligment
from pyLibCRSs import CRSsDefines as defs_crs
from pyLibCRSs.CRSsTools import CRSsTools

class LandXml:
    def __init__(self):
        self.file_path = None
        self.as_dict = None
        self.project_name = None
        self.crs_tools = CRSsTools()
        self.crs_id = None
        self.crs_epsg_code = None
        self.crs_vertical_epsg_code = None
        self.alignment_by_cumulative_distance_mm = None
        self.axis_points_by_cumulative_distance_mm = None
        self.start_cumulative_distance = None
        self.computed_cumulative_distance_end = None
        self.computed_parameters = False

    def clear(self):
        self.file_path = None
        self.alignment_by_cumulative_distance_mm.clear()

    def compute_point_from_cumulative_distance(self,
                                               cumulative_distance):
        str_error = ''
        point = None
        if not self.computed_parameters:
            str_error = ('LandXml object is not initialized.')
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
        for cumulative_distance_mm in self.alignment_by_cumulative_distance_mm:
            aligment = self.alignment_by_cumulative_distance_mm[cumulative_distance_mm]
            if (cumulative_distance >= aligment.start_cumulative_distance
                    and cumulative_distance <= aligment.computed_cumulative_distance_end):
                str_error, point = aligment.compute_point_from_cumulative_distance(cumulative_distance)
                break
        return str_error, point

    def get_axis_points_as_wktlinestring(self):
        str_error = ''
        if self.alignment_by_cumulative_distance_mm is None:
            str_error = ('Axis points object is not initialized')
            return str_error
        wkt_linestring = "LINESTRING("
        wkt_profile_linestring = "LINESTRING("
        start_cumulative_distance = None
        np = 0
        for cumulative_distance_mm in self.axis_points_by_cumulative_distance_mm:
            cumulative_distance = self.axis_points_by_cumulative_distance_mm[cumulative_distance_mm]
            if np == 0:
                start_cumulative_distance = cumulative_distance
            if np > 0:
                wkt_linestring += ","
            pto = self.axis_points_by_cumulative_distance_mm[cumulative_distance_mm]
            wkt_linestring += ('{:.4f} {:.4f} {:.4f}'.format(pto[0], pto[1], pto[2]))
            wkt_profile_linestring += ('{:.4f} {:.4f}'.format(cumulative_distance - start_cumulative_distance, pto[2]))
            np = np + 1
        wkt_linestring += ")"
        wkt_profile_linestring += ")"
        return str_error, wkt_linestring

    def set_axis_points(self,
                        points_distance):
        str_error = ''
        if self.alignment_by_cumulative_distance_mm is None:
            str_error = ('LandXml object is not initialized')
            return str_error
        cumulative_distance = res = next(iter(self.alignment_by_cumulative_distance_mm)) / 1000.
        axis_points_by_cumulative_distance_mm = {}
        for cumulative_distance_mm in self.alignment_by_cumulative_distance_mm:
            aligment = self.alignment_by_cumulative_distance_mm[cumulative_distance_mm]
            str_error, aapcd_mm, cumulative_distance = aligment.set_axis_points(cumulative_distance,
                                                                                points_distance)
            if str_error:
                str_error = ('Setting axis points for aligment: {}\nError:\n{}'.format(aligment.name, str_error))
                return str_error
            axis_points_by_cumulative_distance_mm.update(aapcd_mm)
            yo = 1
        self.axis_points_by_cumulative_distance_mm = dict(sorted(axis_points_by_cumulative_distance_mm.items()))

        return str_error

    def set_from_file(self,
                      file_path):
        str_error = ''
        if self.file_path:
            self.clear()
        if not os.path.exists(file_path):
            str_error = ('Not exists LandXml file: {}'.format(file_path))
            return str_error
        value_as_dict = None
        with open(file_path, 'r', encoding='utf-8') as file:
            value_as_xml = file.read()
        try:
            self.as_dict = xmltodict.parse(value_as_xml)
        except xmltodict.expat.ExpatError as e:
            str_error = ('Parsing LandXml file: {}\nError:\n{}'.format(file_path, str(e)))
            return str_error
        if not dlx.XML_DOCUMENT_TAG in self.as_dict:
            str_error = ('Not exists tag: {} in LandXml file:\n{}'.
                         format(dlx.XML_DOCUMENT_TAG, file_path))
            return str_error
        root = self.as_dict[dlx.XML_DOCUMENT_TAG]
        if not dlx.XML_DOCUMENT_ATTRIBUTE_VERSION_TAG in root:
            str_error = ('Not exists attribute: {} in LandXml file:\n{}'.
                         format(dlx.XML_DOCUMENT_ATTRIBUTE_VERSION_TAG, file_path))
            return str_error
        version = root[dlx.XML_DOCUMENT_ATTRIBUTE_VERSION_TAG]
        if not version in dlx.valid_versions:
            str_error = ('Version: {} in LandXml file:\n{}\nis not in supported versions: {}'.
                         format(version, file_path, dlx.valid_versions))
            return str_error
        if not dlx.XML_DOCUMENT_PROJECT_TAG in root:
            str_error = ('Not exists element: {} in LandXml file:\n{}'.
                         format(dlx.XML_DOCUMENT_PROJECT_TAG, file_path))
            return str_error
        element_project = root[dlx.XML_DOCUMENT_PROJECT_TAG]
        if not dlx.XML_ELEMENT_PROJECT_ATTRIBUTE_NAME_TAG in element_project:
            str_error = ('Not exists attribute: {} in element: {} in LandXml file:\n{}'.
                         format(dlx.XML_ELEMENT_PROJECT_ATTRIBUTE_NAME_TAG,
                                dlx.XML_DOCUMENT_PROJECT_TAG, file_path))
            return str_error
        self.project_name = element_project[dlx.XML_ELEMENT_PROJECT_ATTRIBUTE_NAME_TAG]
        if not dlx.XML_DOCUMENT_UNITS_TAG in root:
            str_error = ('Not exists element: {} in LandXml file:\n{}'.
                         format(dlx.XML_DOCUMENT_UNITS_TAG, file_path))
            return str_error
        element_units = root[dlx.XML_DOCUMENT_UNITS_TAG]
        if not dlx.XML_ELEMENT_UNITS_METRIC_TAG in element_units:
            str_error = ('Not exists element: {} in element: {} in LandXml file:\n{}'.
                         format(dlx.XML_ELEMENT_UNITS_METRIC_TAG,
                                dlx.XML_DOCUMENT_UNITS_TAG, file_path))
            return str_error
        element_units_metric = element_units[dlx.XML_ELEMENT_UNITS_METRIC_TAG]
        if not dlx.XML_ELEMENT_UNITS_METRIC_ATTRIBUTE_LINEAR_UNIT_TAG in element_units_metric:
            str_error = ('Not exists attribute: {} in element: {} in element: {} in LandXml file:\n{}'.
                         format(dlx.XML_ELEMENT_UNITS_METRIC_ATTRIBUTE_LINEAR_UNIT_TAG,
                                dlx.XML_ELEMENT_UNITS_METRIC_TAG, dlx.XML_DOCUMENT_UNITS_TAG, file_path))
            return str_error
        self.linear_unit = element_units_metric[dlx.XML_ELEMENT_UNITS_METRIC_ATTRIBUTE_LINEAR_UNIT_TAG]
        if not self.linear_unit in dlx.valid_linear_units:
            str_error = ('Not valid value: {} in attribute: {} in element: {} in element: {} in LandXml file:\n{}'.
                         format(self.linear_unit, dlx.XML_ELEMENT_UNITS_METRIC_ATTRIBUTE_LINEAR_UNIT_TAG,
                                dlx.XML_ELEMENT_UNITS_METRIC_TAG, dlx.XML_DOCUMENT_UNITS_TAG, file_path))
            return str_error
        if not dlx.XML_ELEMENT_UNITS_METRIC_ATTRIBUTE_ANGULAR_UNIT_TAG in element_units_metric:
            str_error = ('Not exists attribute: {} in element: {} in element: {} in LandXml file:\n{}'.
                         format(dlx.XML_ELEMENT_UNITS_METRIC_ATTRIBUTE_ANGULAR_UNIT_TAG,
                                dlx.XML_ELEMENT_UNITS_METRIC_TAG, dlx.XML_DOCUMENT_UNITS_TAG, file_path))
            return str_error
        self.angular_unit = element_units_metric[dlx.XML_ELEMENT_UNITS_METRIC_ATTRIBUTE_ANGULAR_UNIT_TAG]
        if not self.angular_unit in dlx.valid_angular_units:
            str_error = ('Not valid value: {} in attribute: {} in element: {} in element: {} in LandXml file:\n{}'.
                         format(self.angular_unit, dlx.XML_ELEMENT_UNITS_METRIC_ATTRIBUTE_LINEAR_UNIT_TAG,
                                dlx.XML_ELEMENT_UNITS_METRIC_TAG, dlx.XML_DOCUMENT_UNITS_TAG, file_path))
            return str_error
        if not dlx.XML_DOCUMENT_CRS_TAG in root:
            str_error = ('Not exists element: {} in LandXml file:\n{}'.
                         format(dlx.XML_DOCUMENT_CRS_TAG, file_path))
            return str_error
        element_crs = root[dlx.XML_DOCUMENT_CRS_TAG]
        if not dlx.XML_ELEMENT_CRS_ATTRIBUTE_WKT_TAG in element_crs:
            str_error = ('Not exists attribute: {} in element: {} in LandXml file:\n{}'.
                         format(dlx.XML_ELEMENT_CRS_ATTRIBUTE_WKT_TAG,
                                dlx.XML_DOCUMENT_CRS_TAG, file_path))
            return str_error
        crs_wkt = element_crs[dlx.XML_ELEMENT_CRS_ATTRIBUTE_WKT_TAG]
        str_error, self.crs_id, self.crs_epsg_code, self.vertical_crs_epsg_code = self.crs_tools.get_crs_from_wkt(crs_wkt)
        # reference_wkt_cmp = "COMPD_CS[\"ETRS89 / UTM zone 30N + Alicante height\",PROJCS[\"ETRS89 / UTM zone 30N\",GEOGCS[\"ETRS89\",DATUM[\"European Terrestrial Reference System 1989 ensemble\",SPHEROID[\"GRS 1980\",6378137,298.257222101,AUTHORITY[\"EPSG\",\"7019\"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY[\"EPSG\",\"6258\"]],PRIMEM[\"Greenwich\",0,AUTHORITY[\"EPSG\",\"8901\"]],UNIT[\"degree\",0.01745329251994328,AUTHORITY[\"EPSG\",\"9102\"]],AUTHORITY[\"EPSG\",\"4258\"]],PROJECTION[\"Transverse_Mercator\",AUTHORITY[\"EPSG\",\"9807\"]],PARAMETER[\"latitude_of_origin\",0],PARAMETER[\"central_meridian\",-3],PARAMETER[\"scale_factor\",0.9996],PARAMETER[\"false_easting\",500000],PARAMETER[\"false_northing\",0],UNIT[\"metre\",1,AUTHORITY[\"EPSG\",\"9001\"]],AUTHORITY[\"EPSG\",\"25830\"]],VERT_CS[\"Alicante height\",VERT_DATUM[\"Alicante\",2005,AUTHORITY[\"EPSG\",\"5180\"]],UNIT[\"metre\",1,AUTHORITY[\"EPSG\",\"9001\"]],AUTHORITY[\"EPSG\",\"5782\"]]]"
        # reference_wkt_bad = "COMPD_KK[\"ETRS89 / UTM zone 30N + Alicante height\",PROJCS[\"ETRS89 / UTM zone 30N\",GEOGCS[\"ETRS89\",DATUM[\"European Terrestrial Reference System 1989 ensemble\",SPHEROID[\"GRS 1980\",6378137,298.257222101,AUTHORITY[\"EPSG\",\"7019\"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY[\"EPSG\",\"6258\"]],PRIMEM[\"Greenwich\",0,AUTHORITY[\"EPSG\",\"8901\"]],UNIT[\"degree\",0.01745329251994328,AUTHORITY[\"EPSG\",\"9102\"]],AUTHORITY[\"EPSG\",\"4258\"]],PROJECTION[\"Transverse_Mercator\",AUTHORITY[\"EPSG\",\"9807\"]],PARAMETER[\"latitude_of_origin\",0],PARAMETER[\"central_meridian\",-3],PARAMETER[\"scale_factor\",0.9996],PARAMETER[\"false_easting\",500000],PARAMETER[\"false_northing\",0],UNIT[\"metre\",1,AUTHORITY[\"EPSG\",\"9001\"]],AUTHORITY[\"EPSG\",\"25830\"]],VERT_CS[\"Alicante height\",VERT_DATUM[\"Alicante\",2005,AUTHORITY[\"EPSG\",\"5180\"]],UNIT[\"metre\",1,AUTHORITY[\"EPSG\",\"9001\"]],AUTHORITY[\"EPSG\",\"5782\"]]]"
        # str_error, crs_id_cmp, crs_epsg_code_cmp, vertical_crs_epsg_code_cmp = self.project.crs_tools.get_crs_from_wkt(reference_wkt_cmp)
        # str_error, crs_id_bad, crs_epsg_code_bad, vertical_crs_epsg_code_bad = self.project.crs_tools.get_crs_from_wkt(reference_wkt_bad)
        if str_error:
            str_error = ('Processing attribute: {} in element: {} in LandXml file:\n{}'.
                         format(dlx.XML_ELEMENT_CRS_ATTRIBUTE_WKT_TAG,
                                dlx.XML_DOCUMENT_CRS_TAG, file_path))
            return str_error
        if not self.crs_id:
            str_error = ('Processing attribute: {} in element: {} in LandXml file:\n{}\nCRS is not valid:\n{}'.
                         format(dlx.XML_ELEMENT_CRS_ATTRIBUTE_WKT_TAG,
                                dlx.XML_DOCUMENT_CRS_TAG, file_path, crs_wkt))
            return str_error
        # crs_geo2d_id = self.crs_tools.get_crs_geo2d_for_crs(crs_id)
        # if not crs_geo2d_id:
        #     str_error = (
        #         'Getting CRS geographic 2D from element: {} in chunk in metashape markers XML file:\n{}\nCRS is not valid'.
        #         format(defs_msm.METASHAPE_MARKERS_XML_REFERENCE_TAG, self.file_path))
        if not dlx.XML_DOCUMENT_ALIGMENTS_TAG in root:
            str_error = ('Not exists element: {} in LandXml file:\n{}'.
                         format(dlx.XML_DOCUMENT_ALIGMENTS_TAG, file_path))
            return str_error
        element_aligments = root[dlx.XML_DOCUMENT_ALIGMENTS_TAG]
        if not dlx.XML_ELEMENT_ALIGMENTS_ATTRIBUTE_NAME_TAG in element_aligments:
            str_error = ('Not exists attribute: {} in element: {} in LandXml file:\n{}'.
                         format(dlx.XML_ELEMENT_ALIGMENTS_ATTRIBUTE_NAME_TAG,
                                dlx.XML_DOCUMENT_ALIGMENTS_TAG, file_path))
            return str_error
        self.aligments_name = element_aligments[dlx.XML_ELEMENT_ALIGMENTS_ATTRIBUTE_NAME_TAG]
        if not dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_TAG in element_aligments:
            str_error = ('Not exists element: {} in element: {} in LandXml file:\n{}'.
                         format(dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_TAG,
                                dlx.XML_DOCUMENT_ALIGMENTS_TAG, file_path))
            return str_error
        element_aligment_content = element_aligments[dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_TAG]
        aligment_list = []
        if isinstance(element_aligment_content, dict):
            aligment_list.append(element_aligment_content)
        else:
            aligment_list = element_aligment_content
        is_multi_band = False
        alignment_by_cumulative_distance = {}
        for i in range(len(aligment_list)):
            aligment_element = aligment_list[i]
            aligment = Aligment(self)
            str_error = aligment.set_from_landxml_element(aligment_element, i, file_path)
            if str_error:
                str_error = ('Setting element: {} in position: {} in element: {} in LandXml file:\n{}'.
                             format(dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_TAG,
                                    str(i+1), dlx.XML_DOCUMENT_ALIGMENTS_TAG, file_path))
                return str_error
            cumulative_distance_mm_int = int(aligment.start_cumulative_distance * 1000.)
            alignment_by_cumulative_distance[cumulative_distance_mm_int] = aligment
        self.alignment_by_cumulative_distance_mm = dict(sorted(alignment_by_cumulative_distance.items()))
        cont_aligment = 0
        for cumulative_distance_mm in self.alignment_by_cumulative_distance_mm:
            aligment = self.alignment_by_cumulative_distance_mm[cumulative_distance_mm]
            str_error = aligment.compute_parameters()
            if str_error:
                str_error = ('Computing parameters for aligment: {}\nError:\n{}'.format(aligment.name, str_error))
                return str_error
            if cont_aligment == 0:
                self.start_cumulative_distance = aligment.start_cumulative_distance
            cont_aligment = cont_aligment + 1
            if cont_aligment == len(self.alignment_by_cumulative_distance_mm):
                self.computed_cumulative_distance_end = aligment.computed_cumulative_distance_end
        self.computed_parameters = True
        return str_error

    def write_to_json_file(self,
                           output_file_path):
        str_error = ''
        if not self.as_dict:
            str_error = ('LandXml is not loaded')
            return str_error
        try:
            with open(output_file_path, 'w') as fout:
                json_dumps_str = json.dumps(self.as_dict, indent=4)
                print(json_dumps_str, file=fout)
        except Exception as e:
            str_error = ('Writing LandXml file: {}\nError:\n{}'.format(output_file_path, e))
            return  str_error
        return str_error
