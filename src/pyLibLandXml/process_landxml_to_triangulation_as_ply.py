# authors:
# David Hernandez Lopez, david.hernandez@uclm.es
import argparse
import sys
import os

from .LandXml import LandXml

def process(input_file_path,
            points_distance_in_axis,
            triangulation_argument):
    str_error = ''
    input_file_path = os.path.normpath(input_file_path)
    landXml = LandXml()
    str_error = landXml.set_from_file(input_file_path)
    if str_error:
        return str_error
    points_distance = 10.0
    str_error = landXml.set_axis_points(points_distance)
    if str_error:
        return str_error
    str_error, wkt_linestring, wkt_profile_linestring = landXml.get_axis_points_as_wktlinestring()
    if str_error:
        return str_error
    grading_axis = False
    cross_sections = True
    ply_file_path = landXml.file_path
    ply_file_path = ply_file_path.lower()
    ply_file_path = ply_file_path.replace(".xml", ".ply")
    ply_file_path = os.path.normpath(ply_file_path)
    str_error = landXml.compute_triangulation(grading_axis,
                                              cross_sections,
                                              ply_file_path)
    if str_error:
        return str_error
    return str_error

def main():
    # ==================
    # parse command line
    # ==================
    parser = argparse.ArgumentParser()
    parser.add_argument("--land_xml_file_path", dest="land_xml_file_path", action="store", type=str,
                      help="Land XML file path", default=None)
    parser.add_argument("--points_distance_in_axis", dest="points_distance_in_axis", action="store", type=float,
                      help="Points distance in axis, in meters", default=None)
    parser.add_argument("--triangulation_argument", dest="triangulation_argument", action="store", type=str,
                      help="Triangulation argument", default=None)
    args = parser.parse_args()
    if not args.land_xml_file_path:
        parser.print_help()
        return
    land_xml_file_path = args.land_xml_file_path
    if not os.path.exists(land_xml_file_path):
        sys.stderr.write("Error:\nNot exists Land XML file path:\n%s" % land_xml_file_path)
        sys.stderr.flush()
        return
    if not args.points_distance_in_axis:
        parser.print_help()
        return
    points_distance_in_axis = args.points_distance_in_axis
    if not args.triangulation_argument:
        parser.print_help()
        return
    triangulation_argument = args.triangulation_argument
    str_error = process(land_xml_file_path, points_distance_in_axis, triangulation_argument)
    if str_error:
        sys.stderr.write("Error:\n{}".format(str_error))
        sys.stderr.flush()
        return
    # sys.stdout.write("... Process finished")
    # sys.stdout.flush()

if __name__ == '__main__':
    main()
