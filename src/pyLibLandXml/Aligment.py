# authors:
# David Hernandez Lopez, david.hernandez@uclm.es

from . import defs_landxml as dlx
from . import Curve
from . import Line
from . import Spiral
from . import ProfileVerticalAligment
from . import CrossSection

# http://www.landxml.org/schema/landxml-1.2/documentation/landxml-1.2doc_alignment.html
class Aligment:
    def __init__(self, land_xml):
        self.land_xml = land_xml
        self.position = None # from 0
        self.name = None
        self.length = None
        self.description = None
        self.start_cumulative_distance = None
        self.horizontal_aligment_by_cumulative_distance_mm = None
        self.profile_aligment_by_cumulative_distance_mm = None
        self.cross_section_by_cumulative_distance_mm = None
        self.computed_cumulative_distance_end = None
        self.computed_parameters = False

    def compute_parameters(self):
        str_error = ''
        component_count = 0
        for aligment_cumulative_distance_mm in self.horizontal_aligment_by_cumulative_distance_mm:
            aligment_component = self.horizontal_aligment_by_cumulative_distance_mm[
                aligment_cumulative_distance_mm]
            str_error = aligment_component.compute_parameters()
            if str_error:
                str_error = ('Computing paramerers for horizontal component position: {}\nError:\n{}'
                             .format(str(component_count + 1), str_error))
                return str_error
            component_count = component_count + 1
            if component_count == len(self.horizontal_aligment_by_cumulative_distance_mm):
                self.computed_cumulative_distance_end = aligment_component.computed_cumulative_distance_end
        component_count = 0
        for profile_aligment_cumulative_distance_mm in self.profile_aligment_by_cumulative_distance_mm:
            profile_aligment_component = self.profile_aligment_by_cumulative_distance_mm[
                profile_aligment_cumulative_distance_mm]
            str_error = profile_aligment_component.compute_parameters()
            if str_error:
                str_error = ('Computing paramerers for vertial component position: {}\nError:\n{}'
                             .format(str(component_count + 1), str_error))
                return str_error
            component_count = component_count + 1
            # if component_count == len(self.horizontal_aligment_by_cumulative_distance_mm):
            #     self.computed_cumulative_distance_end = aligment_component.computed_cumulative_distance_end
        component_count = 0
        self.computed_parameters = True
        for cross_section_cumulative_distance in self.cross_section_by_cumulative_distance_mm:
            cross_section_component = self.cross_section_by_cumulative_distance_mm[cross_section_cumulative_distance]
            str_error = cross_section_component.compute_parameters()
            if str_error:
                str_error = ('Computing paramerers for cross section component position: {}\nError:\n{}'
                             .format(str(component_count + 1), str_error))
                self.computed_parameters = False
                return str_error
            component_count = component_count + 1
        return str_error

    def compute_elevation_from_cumulative_distance(self,
                                                   cumulative_distance):
        str_error = ''
        elevation = None
        if not self.computed_parameters:
            str_error = self.compute_parameters()
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
        profile_component_count = 0
        for profile_aligment_cumulative_distance_mm in self.profile_aligment_by_cumulative_distance_mm:
            profile_aligment_component = self.profile_aligment_by_cumulative_distance_mm[
                profile_aligment_cumulative_distance_mm]
            if (cumulative_distance >= profile_aligment_component.start_cumulative_distance
                    and cumulative_distance <= profile_aligment_component.computed_cumulative_distance_end):
                str_error, elevation = profile_aligment_component.compute_elevation_from_cumulative_distance(cumulative_distance)
                break
            profile_component_count = profile_component_count + 1
        return str_error, elevation

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
        component_count = 0
        for aligment_cumulative_distance_mm in self.horizontal_aligment_by_cumulative_distance_mm:
            aligment_component = self.horizontal_aligment_by_cumulative_distance_mm[
                aligment_cumulative_distance_mm]
            if (cumulative_distance >= aligment_component.start_cumulative_distance
                    and cumulative_distance <= aligment_component.computed_cumulative_distance_end):
                str_error, point = aligment_component.compute_point_from_cumulative_distance(cumulative_distance)
                break
            component_count = component_count + 1
        str_error, elevation = self.compute_elevation_from_cumulative_distance(cumulative_distance)
        if str_error:
            return str_error, elevation
        point.append(elevation)
        return str_error, point

    def set_axis_points(self,
                        cumulative_distance,
                        points_distance):
        str_error = ''
        axis_points_by_cumulative_distance_mm = {}
        component_count = 0
        for aligment_cumulative_distance_mm in self.horizontal_aligment_by_cumulative_distance_mm:
            aligment_component = self.horizontal_aligment_by_cumulative_distance_mm[
                aligment_cumulative_distance_mm]
            points_by_cumulative_distance_mm = {}
            start_point = aligment_component.point_start
            str_error, elevation = self.compute_elevation_from_cumulative_distance(aligment_component.start_cumulative_distance)
            if str_error:
                return str_error, axis_points_by_cumulative_distance_mm, cumulative_distance
            start_point.append(elevation)
            points_by_cumulative_distance_mm[int(aligment_component.start_cumulative_distance * 1000.)] = start_point
            if ((cumulative_distance - aligment_component.start_cumulative_distance)
                    < dlx.CUMULATIVE_DISTANCE_IGNORE_FIRST_POINT_TOLERANCE):
                cumulative_distance = cumulative_distance + points_distance
            if not aligment_component.computed_parameters:
                str_error = aligment_component.compute_parameters()
                if str_error:
                    str_error = ('Computing paramerers for curve in component position: {}\nError:\n{}'
                                 .format(str(component_count + 1), str_error))
                    return str_error, axis_points_by_cumulative_distance_mm, cumulative_distance
            while cumulative_distance < aligment_component.computed_cumulative_distance_end:
                if ((aligment_component.computed_cumulative_distance_end - cumulative_distance)
                        < dlx.CUMULATIVE_DISTANCE_IGNORE_FIRST_POINT_TOLERANCE):
                    break
                str_error, point = aligment_component.compute_point_from_cumulative_distance(cumulative_distance)
                if str_error:
                    return str_error, axis_points_by_cumulative_distance_mm, cumulative_distance
                str_error, elevation = self.compute_elevation_from_cumulative_distance(cumulative_distance)
                if str_error:
                    return str_error, axis_points_by_cumulative_distance_mm, cumulative_distance
                point.append(elevation)
                points_by_cumulative_distance_mm[int(cumulative_distance * 1000.)] = point
                cumulative_distance = cumulative_distance + points_distance
            end_point = aligment_component.point_end
            str_error, elevation = self.compute_elevation_from_cumulative_distance(aligment_component.computed_cumulative_distance_end)
            if str_error:
                return str_error, axis_points_by_cumulative_distance_mm, cumulative_distance
            end_point.append(elevation)
            points_by_cumulative_distance_mm[int(aligment_component.computed_cumulative_distance_end * 1000.)] = end_point
            axis_points_by_cumulative_distance_mm.update(points_by_cumulative_distance_mm)
            component_count = component_count + 1
            # if component_count > 1:
            #     break
        return str_error, axis_points_by_cumulative_distance_mm, cumulative_distance

    def set_from_landxml_element(self,
                                 element,
                                 position,
                                 file_path):
        str_error = ''
        self.position = position
        if not dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_ATTRIBUTE_NAME_TAG in element:
            str_error = ('Not exists attribute: {} in element: {} in position in element: {} in LandXml file:\n{}'.
                         format(dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_ATTRIBUTE_NAME_TAG,
                                dlx.XML_ELEMENT_ALIGMENTS_ATTRIBUTE_NAME_TAG,
                                str(position + 1), dlx.XML_DOCUMENT_ALIGMENTS_TAG, file_path))
            return str_error
        self.name = element[dlx.XML_ELEMENT_ALIGMENTS_ATTRIBUTE_NAME_TAG]
        if not dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_ATTRIBUTE_STASTART_TAG in element:
            str_error = ('Not exists attribute: {} in element: {} in position in element: {} in LandXml file:\n{}'.
                         format(dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_ATTRIBUTE_NAME_TAG,
                                dlx.XML_ELEMENT_ALIGMENTS_ATTRIBUTE_NAME_TAG,
                                str(position + 1), dlx.XML_DOCUMENT_ALIGMENTS_TAG, file_path))
            return str_error
        value = element[dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_ATTRIBUTE_STASTART_TAG]
        try:
            self.start_cumulative_distance = float(value)
        except ValueError:
            str_error = ('Attribute: {} in element: {} in position in element: {} in LandXml file:\n{}\nmust be a float: {}'.
                         format(dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_ATTRIBUTE_NAME_TAG,
                                dlx.XML_ELEMENT_ALIGMENTS_ATTRIBUTE_NAME_TAG,
                                str(position + 1), dlx.XML_DOCUMENT_ALIGMENTS_TAG, file_path, value))
            return str_error
        if not dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_ATTRIBUTE_LENGTH_TAG in element:
            str_error = ('Not exists attribute: {} in element: {} in position in element: {} in LandXml file:\n{}'.
                         format(dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_ATTRIBUTE_LENGTH_TAG,
                                dlx.XML_ELEMENT_ALIGMENTS_ATTRIBUTE_NAME_TAG,
                                str(position + 1), dlx.XML_DOCUMENT_ALIGMENTS_TAG, file_path))
            return str_error
        value = element[dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_ATTRIBUTE_LENGTH_TAG]
        try:
            self.length = float(value)
        except ValueError:
            str_error = ('Attribute: {} in element: {} in position in element: {} in LandXml file:\n{}\nmust be a float: {}'.
                         format(dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_ATTRIBUTE_LENGTH_TAG,
                                dlx.XML_ELEMENT_ALIGMENTS_ATTRIBUTE_NAME_TAG,
                                str(position + 1), dlx.XML_DOCUMENT_ALIGMENTS_TAG, file_path, value))
            return str_error
        if dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_ATTRIBUTE_DESCRIPTION_TAG in element:
            self.description = element[dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_ATTRIBUTE_DESCRIPTION_TAG]
        if not dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_COORD_GEOM_TAG in element:
            str_error = ('Not exists element: {} in element: {} in position in element: {} in LandXml file:\n{}'.
                         format(dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_COORD_GEOM_TAG,
                                dlx.XML_ELEMENT_ALIGMENTS_ATTRIBUTE_NAME_TAG,
                                str(position + 1), dlx.XML_DOCUMENT_ALIGMENTS_TAG, file_path))
            return str_error
        element_coord_geom_content = element[dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_COORD_GEOM_TAG]
        if not isinstance(element_coord_geom_content, dict):
            str_error = ('Element: {} in element: {} in position in element: {} in LandXml file:\n{}\nmust be a dict'.
                         format(dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_COORD_GEOM_TAG,
                                dlx.XML_ELEMENT_ALIGMENTS_ATTRIBUTE_NAME_TAG,
                                str(position + 1), dlx.XML_DOCUMENT_ALIGMENTS_TAG, file_path))
            return str_error
        cont = 0
        coord_geom_by_distance = {}
        for element_geometry_tag in element_coord_geom_content:
            cont = cont + 1
            if not element_geometry_tag.lower() in [s.lower() for s in dlx.coord_geom_types]:
                str_error = (
                    'Invalid value: {} in component position: {} in element: {}\nin element: {} in position in element: {} in LandXml file:\n{}'.
                    format(element_geometry_tag, str(cont), dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_COORD_GEOM_TAG,
                           dlx.XML_ELEMENT_ALIGMENTS_ATTRIBUTE_NAME_TAG,
                           str(position + 1), dlx.XML_DOCUMENT_ALIGMENTS_TAG, file_path))
                return str_error
            element_geometry = element_coord_geom_content[element_geometry_tag]
            element_list = []
            if isinstance(element_geometry, list):
                element_list = element_geometry
            else:
                element_list.append(element_geometry)
            for i in range(len(element_list)):
                element_coord_geom = element_list[i]
                coord_geom = None
                if element_geometry_tag.casefold() == dlx.XML_ELEMENT_CURVE_TAG.casefold():
                    coord_geom = Curve(self)
                elif element_geometry_tag.casefold() == dlx.XML_ELEMENT_LINE_TAG.casefold():
                    coord_geom = Line(self)
                elif element_geometry_tag.casefold() == dlx.XML_ELEMENT_SPIRAL_TAG.casefold():
                    coord_geom = Spiral(self)
                else:
                    str_error = (
                        'Invalid value: {} in component position: {} in element: {}\nin element: {} in position in element: {} in LandXml file:\n{}'.
                        format(element_geometry_tag, str(cont), dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_COORD_GEOM_TAG,
                               dlx.XML_ELEMENT_ALIGMENTS_ATTRIBUTE_NAME_TAG,
                               str(position + 1), dlx.XML_DOCUMENT_ALIGMENTS_TAG, file_path))
                    return str_error
                str_error = coord_geom.set_from_landxml_element(element_coord_geom)
                if str_error:
                    str_error = (
                        'Setting element: {} in position: {} in component position: {} in element: {}'
                        '\nin element: {} in position in element: {} in LandXml file:\n{}'.
                        format(element_geometry_tag, str(i + 1), element_geometry_tag,
                               str(cont), dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_COORD_GEOM_TAG,
                               dlx.XML_ELEMENT_ALIGMENTS_ATTRIBUTE_NAME_TAG,
                               str(position + 1), dlx.XML_DOCUMENT_ALIGMENTS_TAG, file_path))
                    return str_error
                sta_start_mm_int = int(coord_geom.start_cumulative_distance * 1000.)
                coord_geom_by_distance[sta_start_mm_int] = coord_geom
        self.horizontal_aligment_by_cumulative_distance_mm = dict(sorted(coord_geom_by_distance.items()))
        if not dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_PROFILE_TAG in element:
            str_error = ('Not exists element: {} in element: {} in position in element: {} in LandXml file:\n{}'.
                         format(dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_PROFILE_TAG,
                                dlx.XML_ELEMENT_ALIGMENTS_ATTRIBUTE_NAME_TAG,
                                str(position + 1), dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_PROFILE_TAG, file_path))
            return str_error
        element_profile = element[dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_PROFILE_TAG]
        profile_list = []
        if isinstance(element_profile, list):
            profile_list = element_profile
        else:
            profile_list.append(element_profile)
        profile_vertical_aligment_by_cumulative_distance = {}
        for i in range(len(profile_list)):
            element_profile_content = profile_list[i]
            if not isinstance(element_profile_content, dict):
                str_error = ('Element: {} in position: {} in element: {} in position in element: {} in LandXml file:\n{}\nmust be a dict'.
                             format(dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_PROFILE_TAG, str(i + 1),
                                    dlx.XML_ELEMENT_ALIGMENTS_ATTRIBUTE_NAME_TAG,
                                    str(position + 1), dlx.XML_DOCUMENT_ALIGMENTS_TAG, file_path))
                return str_error
            if not dlx.XML_ELEMENT_PROFILE_PROF_ALIGN_TAG in element_profile_content:
                str_error = ('Not exists element: {} in element: {}\nin element: {} in position in element: {} in LandXml file:\n{}'.
                         format(dlx.XML_ELEMENT_PROFILE_PROF_ALIGN_TAG,
                                dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_PROFILE_TAG,
                                dlx.XML_ELEMENT_ALIGMENTS_ATTRIBUTE_NAME_TAG,
                                str(position + 1), dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_PROFILE_TAG, file_path))
                return str_error
            element_profile_prof_aling_content = element_profile_content[dlx.XML_ELEMENT_PROFILE_PROF_ALIGN_TAG]
            profile_vertical_aligment = ProfileVerticalAligment(self)
            str_error = profile_vertical_aligment.set_from_landxml_element(element_profile_prof_aling_content)
            if str_error:
                str_error = (
                    'Setting element: {} in position: {} in component position: {} in element: {}'
                    '\nin element: {} in position in element: {} in LandXml file:\n{}'.
                    format(dlx.XML_ELEMENT_PROFILE_PROF_ALIGN_TAG, str(i + 1),
                           str(cont), dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_PROFILE_TAG,
                           dlx.XML_ELEMENT_ALIGMENTS_ATTRIBUTE_NAME_TAG,
                           str(position + 1), dlx.XML_DOCUMENT_ALIGMENTS_TAG, file_path))
                return str_error
            cumulative_distance_mm_int = int(profile_vertical_aligment.start_cumulative_distance * 1000.)
            profile_vertical_aligment_by_cumulative_distance[cumulative_distance_mm_int] = profile_vertical_aligment
        self.profile_aligment_by_cumulative_distance_mm = dict(sorted(profile_vertical_aligment_by_cumulative_distance.items()))
        if not dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_CROSS_SECTS_GEOM_TAG in element:
            str_error = ('Not exists element: {} in element: {} in position in element: {} in LandXml file:\n{}'.
                         format(dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_CROSS_SECTS_GEOM_TAG,
                                dlx.XML_ELEMENT_ALIGMENTS_ATTRIBUTE_NAME_TAG,
                                str(position + 1), dlx.XML_DOCUMENT_ALIGMENTS_TAG, file_path))
            return str_error
        element_cross_sections_content = element[dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_CROSS_SECTS_GEOM_TAG]
        if not isinstance(element_cross_sections_content, dict):
            str_error = ('Element: {} in element: {} in position in element: {} in LandXml file:\n{}\nmust be a dict'.
                         format(dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_CROSS_SECTS_GEOM_TAG,
                                dlx.XML_ELEMENT_ALIGMENTS_ATTRIBUTE_NAME_TAG,
                                str(position + 1), dlx.XML_DOCUMENT_ALIGMENTS_TAG, file_path))
            return str_error
        if not dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_CROSS_SECT_GEOM_TAG in element_cross_sections_content:
            str_error = ('Not exists element: {} in element: {}  in element: {}\n in position in element: {} in LandXml file:\n{}'.
                         format(dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_CROSS_SECT_GEOM_TAG,
                                dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_CROSS_SECTS_GEOM_TAG,
                                dlx.XML_ELEMENT_ALIGMENTS_ATTRIBUTE_NAME_TAG,
                                str(position + 1), dlx.XML_DOCUMENT_ALIGMENTS_TAG, file_path))
            return str_error
        element_cross_section_content = element_cross_sections_content[dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_CROSS_SECT_GEOM_TAG]
        cross_sect_list = []
        if isinstance(element_cross_section_content, dict):
            cross_sect_list.append(element_cross_section_content)
        else:
            cross_sect_list = element_cross_section_content
        cross_section_by_distance = {}
        for i in range(len(cross_sect_list)):
            element_cross_section = cross_sect_list[i]
            cross_section = CrossSection(self)
            str_error = cross_section.set_from_landxml_element(element_cross_section)
            if str_error:
                str_error = (
                    'Setting element: {} in position: {} in element: {}  in element: {}\n in position in element: {} in LandXml file:\n{}'.
                    format(dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_CROSS_SECT_GEOM_TAG, str(i + 1),
                           dlx.XML_ELEMENT_ALIGMENTS_ALIGMENT_CROSS_SECTS_GEOM_TAG,
                           dlx.XML_ELEMENT_ALIGMENTS_ATTRIBUTE_NAME_TAG,
                           str(position + 1), dlx.XML_DOCUMENT_ALIGMENTS_TAG, file_path))
                return str_error
            acumulative_distance_mm_int = int(cross_section.start_cumulative_distance * 1000.)
            cross_section_by_distance[acumulative_distance_mm_int] = cross_section
        self.cross_section_by_cumulative_distance_mm = dict(sorted(cross_section_by_distance.items()))
        return str_error
