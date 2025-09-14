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
        self.alignments = []

    def clear(self):
        self.file_path = None
        self.alignments.clear()

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
        for i in range(len(aligment_list)):
            aligment_element = aligment_list[i]
            aligment = Aligment(self)
            str_error = aligment.set_from_landxml_element(aligment_element, i, file_path)
            if str_error:
                str_error = ('Setting element: {} in position: {} in element: {} in LandXml file:\n{}'.
                             format(dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_TAG,
                                    str(i+1), dlx.XML_DOCUMENT_ALIGMENTS_TAG, file_path))
                return str_error
            self.alignments.append(aligment)
            yo = 1

        yo = 1
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
