# authors:
# David Hernandez Lopez, david.hernandez@uclm.es

import numpy as np

import defs_landxml as dlx
from ParabolicVerticalCurve import ParabolicVerticalCurve
from LineVerticalCurve import LineVerticalCurve

# http://www.landxml.org/schema/landxml-1.2/documentation/LandXML-1.2Doc_ProfAlign.html
class ProfileVerticalAligment:
    def __init__(self, aligment):
        self.aligment = aligment
        self.name = None
        self.points_vertical_intersection_by_cumulative_distance_mm = None # [cumulative distance, elevation] ¿puede estar vacio? de momento supongo que no, al menos origen y fin
        self.parabolic_vertical_curve_by_cumulative_distance_mm = None # ¿puede estar vacio? de momento supongo que no, al menos uno, ¿recta?
        self.start_cumulative_distance = None # min acumulative distance
        self.computed_parameters = False
        self.computed_cumulative_distance_end = None
        self.vertical_aligment_by_start_cumulative_distance_mm = None

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
        vertical_component_count = 0
        for vertical_aligment_cumulative_distance_mm in self.vertical_aligment_by_start_cumulative_distance_mm:
            vertical_aligment_component = self.vertical_aligment_by_start_cumulative_distance_mm[
                vertical_aligment_cumulative_distance_mm]
            if (cumulative_distance >= vertical_aligment_component.start_cumulative_distance
                    and cumulative_distance <= vertical_aligment_component.computed_cumulative_distance_end):
                str_error, elevation = vertical_aligment_component.compute_elevation_from_cumulative_distance(cumulative_distance)
                break
            vertical_component_count = vertical_component_count + 1
        return str_error, elevation

    def compute_parameters(self):
        str_error = ''
        if self.computed_parameters:
            return str_error
        vertical_aligment_by_start_cumulative_distance_mm = {}
        parabolic_count = 0
        # first vertical aligment: type parabola
        for cumulative_distance_mm in self.parabolic_vertical_curve_by_cumulative_distance_mm:
            parabolic_vertical_curve = self.parabolic_vertical_curve_by_cumulative_distance_mm[cumulative_distance_mm]
            ip_cumulative_distance = parabolic_vertical_curve.cumulative_distance
            ip_elevation = parabolic_vertical_curve.elevation
            length = parabolic_vertical_curve.length
            # search point before (type PVI or PI)
            before_cumulative_distance = None
            before_elevation = None
            after_cumulative_distance = None
            after_elevation = None
            for aux_ad_mm in self.points_vertical_intersection_by_cumulative_distance_mm:
                aux_acumulative_distance = self.points_vertical_intersection_by_cumulative_distance_mm[aux_ad_mm][0]
                aux_elevation = self.points_vertical_intersection_by_cumulative_distance_mm[aux_ad_mm][1]
                if aux_acumulative_distance < ip_cumulative_distance:
                    if before_cumulative_distance is None:
                        before_cumulative_distance = aux_acumulative_distance
                        before_elevation = aux_elevation
                    else:
                        if (np.abs(aux_acumulative_distance - ip_cumulative_distance)
                                < np.abs(before_cumulative_distance - ip_cumulative_distance)):
                            before_cumulative_distance = aux_acumulative_distance
                            before_elevation = aux_elevation
                if aux_acumulative_distance > ip_cumulative_distance:
                    if after_cumulative_distance is None:
                        after_cumulative_distance = aux_acumulative_distance
                        after_elevation = aux_elevation
                    else:
                        if (np.abs(aux_acumulative_distance - ip_cumulative_distance)
                                < np.abs(after_cumulative_distance - ip_cumulative_distance)):
                            after_cumulative_distance = aux_acumulative_distance
                            after_elevation = aux_elevation
            for aux_ad_mm in self.parabolic_vertical_curve_by_cumulative_distance_mm:
                if aux_ad_mm == cumulative_distance_mm:
                    continue
                aux_parabolic_vertical_curve = self.parabolic_vertical_curve_by_cumulative_distance_mm[
                    aux_ad_mm]
                aux_acumulative_distance = aux_parabolic_vertical_curve.cumulative_distance
                aux_elevation = aux_parabolic_vertical_curve.elevation
                if aux_acumulative_distance < ip_cumulative_distance:
                    if before_cumulative_distance is None:
                        before_cumulative_distance = aux_acumulative_distance
                        before_elevation = aux_elevation
                    else:
                        if (np.abs(aux_acumulative_distance - ip_cumulative_distance)
                                < np.abs(before_cumulative_distance - ip_cumulative_distance)):
                            before_cumulative_distance = aux_acumulative_distance
                            before_elevation = aux_elevation
                if aux_acumulative_distance > ip_cumulative_distance:
                    if after_cumulative_distance is None:
                        after_cumulative_distance = aux_acumulative_distance
                        after_elevation = aux_elevation
                    else:
                        if (np.abs(aux_acumulative_distance - ip_cumulative_distance)
                                < np.abs(after_cumulative_distance - ip_cumulative_distance)):
                            after_cumulative_distance = aux_acumulative_distance
                            after_elevation = aux_elevation
            if before_cumulative_distance is None:
                str_error = ('Not found before point for parabola position: {}'.format(str(parabolic_count + 1)))
                return str_error
            if after_cumulative_distance is None:
                str_error = ('Not found after point for parabola position: {}'.format(str(parabolic_count + 1)))
                return str_error
            parabolic_vertical_curve.before_inclination_pu = ((ip_elevation - before_elevation)
                                     / (ip_cumulative_distance - before_cumulative_distance))
            parabolic_vertical_curve.after_inclination_pu = ((after_elevation - ip_elevation)
                                     / (after_cumulative_distance - ip_cumulative_distance))
            # parabolic_vertical_curve.inclination_difference = (parabolic_vertical_curve.before_inclination_pu
            #                                                    - parabolic_vertical_curve.after_inclination_pu)
            parabolic_vertical_curve.inclination_difference = (parabolic_vertical_curve.after_inclination_pu
                                                               - parabolic_vertical_curve.before_inclination_pu)
            parabolic_vertical_curve.kv = length / parabolic_vertical_curve.inclination_difference
            parabolic_vertical_curve.start_cumulative_distance = parabolic_vertical_curve.cumulative_distance - length / 2.
            parabolic_vertical_curve.computed_cumulative_distance_end = parabolic_vertical_curve.cumulative_distance + length / 2.
            parabolic_vertical_curve.elevation_start = (before_elevation
                                                        + parabolic_vertical_curve.before_inclination_pu
                                                        * (parabolic_vertical_curve.start_cumulative_distance
                                                           - before_cumulative_distance))
            parabolic_vertical_curve.elevation_end = (after_elevation
                                                        - parabolic_vertical_curve.after_inclination_pu
                                                        * (after_cumulative_distance
                                                           - parabolic_vertical_curve.computed_cumulative_distance_end))
            parabolic_vertical_curve.computed_parameters = True
            start_cumulative_distance_mm = int(parabolic_vertical_curve.start_cumulative_distance * 1000.)
            vertical_aligment_by_start_cumulative_distance_mm[start_cumulative_distance_mm] = parabolic_vertical_curve
            parabolic_count = parabolic_count + 1
        # second vertical aligment: type line, two secuential points are PVI
        pvi_count = 0
        number_of_pvis = len(self.points_vertical_intersection_by_cumulative_distance_mm)
        last_cumulative_distance_mm = list(self.points_vertical_intersection_by_cumulative_distance_mm.keys())[-1]
        for cumulative_distance_mm in self.points_vertical_intersection_by_cumulative_distance_mm:
            # if cumulative_distance_mm == last_cumulative_distance_mm:
            #     break
            pvi_cumulative_distance = self.points_vertical_intersection_by_cumulative_distance_mm[cumulative_distance_mm][0]
            pvi_elevation = self.points_vertical_intersection_by_cumulative_distance_mm[cumulative_distance_mm][1]
            after_cumulative_distance = None
            after_elevation = None
            after_elevation_point_type_is_pvi = False
            before_cumulative_distance = None
            before_elevation = None
            before_elevation_point_type_is_pvi = False
            for aux_ad_mm in self.points_vertical_intersection_by_cumulative_distance_mm:
                aux_acumulative_distance = self.points_vertical_intersection_by_cumulative_distance_mm[aux_ad_mm][0]
                aux_elevation = self.points_vertical_intersection_by_cumulative_distance_mm[aux_ad_mm][1]
                if pvi_count < (number_of_pvis - 1):
                    if aux_acumulative_distance <= pvi_cumulative_distance:
                        continue
                    if after_cumulative_distance is None:
                        after_cumulative_distance = aux_acumulative_distance
                        after_elevation = aux_elevation
                        after_elevation_point_type_is_pvi = True
                    else:
                        if (np.abs(aux_acumulative_distance - pvi_cumulative_distance)
                                    < np.abs(after_cumulative_distance - pvi_cumulative_distance)):
                            after_cumulative_distance = aux_acumulative_distance
                            after_elevation = aux_elevation
                            after_elevation_point_type_is_pvi = True
                if pvi_count > 0:
                    if aux_acumulative_distance >= pvi_cumulative_distance:
                        continue
                    if before_cumulative_distance is None:
                        before_cumulative_distance = aux_acumulative_distance
                        before_elevation = aux_elevation
                        before_elevation_point_type_is_pvi = True
                    else:
                        if (np.abs(aux_acumulative_distance - pvi_cumulative_distance)
                                    < np.abs(before_cumulative_distance - pvi_cumulative_distance)):
                            before_cumulative_distance = aux_acumulative_distance
                            before_elevation = aux_elevation
                            before_elevation_point_type_is_pvi = True
            for aux_ad_mm in self.parabolic_vertical_curve_by_cumulative_distance_mm:
                aux_parabolic_vertical_curve = self.parabolic_vertical_curve_by_cumulative_distance_mm[
                    aux_ad_mm]
                if pvi_count < (number_of_pvis - 1):
                    aux_acumulative_distance = aux_parabolic_vertical_curve.start_cumulative_distance
                    aux_elevation = aux_parabolic_vertical_curve.elevation_start
                    if aux_acumulative_distance <= pvi_cumulative_distance:
                        continue
                    if after_cumulative_distance is None:
                        after_cumulative_distance = aux_acumulative_distance
                        after_elevation = aux_elevation
                    else:
                        if (np.abs(aux_acumulative_distance - pvi_cumulative_distance)
                                    < np.abs(after_cumulative_distance - pvi_cumulative_distance)):
                            after_cumulative_distance = aux_acumulative_distance
                            after_elevation = aux_elevation
                            after_elevation_point_type_is_pvi = False
                if pvi_count > 0:
                    aux_acumulative_distance = aux_parabolic_vertical_curve.computed_cumulative_distance_end
                    aux_elevation = aux_parabolic_vertical_curve.elevation_end
                    if aux_acumulative_distance >= pvi_cumulative_distance:
                        continue
                    if before_cumulative_distance is None:
                        before_cumulative_distance = aux_acumulative_distance
                        before_elevation = aux_elevation
                    else:
                        if (np.abs(aux_acumulative_distance - pvi_cumulative_distance)
                                    < np.abs(before_cumulative_distance - pvi_cumulative_distance)):
                            before_cumulative_distance = aux_acumulative_distance
                            before_elevation = aux_elevation
                            before_elevation_point_type_is_pvi = False
            if pvi_count < (number_of_pvis - 1):
                if after_cumulative_distance is None:
                    str_error = ('Not found after point for point vertical intersection position: {}'.format(str(parabolic_count + 1)))
                    return str_error
                # if not after_elevation_point_type_is_pvi:
                #     continue
                slope = (after_elevation - pvi_elevation) / (after_cumulative_distance - pvi_cumulative_distance)
                line_vertical_curve = LineVerticalCurve(self)
                line_vertical_curve.start_cumulative_distance = pvi_cumulative_distance
                line_vertical_curve.computed_cumulative_distance_end = after_cumulative_distance
                line_vertical_curve.elevation_start = pvi_elevation
                line_vertical_curve.elevation_end = after_elevation
                line_vertical_curve.slope = slope
                line_vertical_curve.computed_parameters = True
                start_cumulative_distance_mm = int(pvi_cumulative_distance * 1000.)
                vertical_aligment_by_start_cumulative_distance_mm[start_cumulative_distance_mm] = line_vertical_curve
            if pvi_count > 0:
                if before_cumulative_distance is None:
                    str_error = ('Not found before point for point vertical intersection position: {}'.format(str(parabolic_count + 1)))
                    return str_error
                # if not before_elevation_point_type_is_pvi:
                #     continue
                slope = (pvi_elevation - before_elevation) / (pvi_cumulative_distance - before_cumulative_distance)
                line_vertical_curve = LineVerticalCurve(self)
                line_vertical_curve.start_cumulative_distance = before_cumulative_distance
                line_vertical_curve.computed_cumulative_distance_end = pvi_cumulative_distance
                line_vertical_curve.elevation_start = before_elevation
                line_vertical_curve.elevation_end = pvi_elevation
                line_vertical_curve.slope = slope
                line_vertical_curve.computed_parameters = True
                start_cumulative_distance_mm = int(before_cumulative_distance * 1000.)
                vertical_aligment_by_start_cumulative_distance_mm[start_cumulative_distance_mm] = line_vertical_curve
            pvi_count = pvi_count + 1
        # compute lines between parabolas
        sorted_vertical_aligment_by_start_cumulative_distance_mm \
            = dict(sorted(vertical_aligment_by_start_cumulative_distance_mm.items()))
        cumulative_distances_mm = list(sorted_vertical_aligment_by_start_cumulative_distance_mm.keys())
        vertical_aligment_by_start_cumulative_distance_mm = {}
        for i in range(len(cumulative_distances_mm) - 1):
            first_cumulative_distance = cumulative_distances_mm[i]
            fva = sorted_vertical_aligment_by_start_cumulative_distance_mm[first_cumulative_distance]
            second_cumulative_distance = cumulative_distances_mm[i + 1]
            sva = sorted_vertical_aligment_by_start_cumulative_distance_mm[second_cumulative_distance]
            if np.abs(sva.start_cumulative_distance - fva.computed_cumulative_distance_end) > 0.001:
                slope = (sva.elevation_start - fva.elevation_end) / (sva.start_cumulative_distance - fva.computed_cumulative_distance_end)
                line_vertical_curve = LineVerticalCurve(self)
                line_vertical_curve.start_cumulative_distance = fva.computed_cumulative_distance_end
                line_vertical_curve.computed_cumulative_distance_end = sva.start_cumulative_distance
                line_vertical_curve.elevation_start = fva.elevation_end
                line_vertical_curve.elevation_end = sva.elevation_start
                line_vertical_curve.slope = slope
                line_vertical_curve.computed_parameters = True
                start_cumulative_distance_mm = int(fva.computed_cumulative_distance_end * 1000.)
                vertical_aligment_by_start_cumulative_distance_mm[start_cumulative_distance_mm] = line_vertical_curve
        sorted_vertical_aligment_by_start_cumulative_distance_mm.update(vertical_aligment_by_start_cumulative_distance_mm)
        self.vertical_aligment_by_start_cumulative_distance_mm \
            = dict(sorted(sorted_vertical_aligment_by_start_cumulative_distance_mm.items()))
        last_cumulative_distance_mm = list(self.vertical_aligment_by_start_cumulative_distance_mm.keys())[-1]
        last_vertical_aligment = self.vertical_aligment_by_start_cumulative_distance_mm[last_cumulative_distance_mm]
        self.computed_cumulative_distance_end = last_vertical_aligment.computed_cumulative_distance_end
        self.computed_parameters = True
        return str_error

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
        str_error = self.compute_parameters()
        return str_error






