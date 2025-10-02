import os, sys
current_path = os.path.dirname(__file__)
sys.path.append(os.path.join(current_path, '../../..'))

# lib_path = 'E:/dev/python/lib'
# sys.path.append('E:/dev/python/lib')

from pyLibLandXml.LandXml import LandXml

def main():
    input_file_path = current_path + "/data/LAV_Tafalla_eje+rasante+subbalasto.xml"
    input_file_path = os.path.normpath(input_file_path)
    landXml = LandXml()
    str_error = landXml.set_from_file(input_file_path)
    if str_error:
        print(f"Error:\n\t{str_error}")
        return
    points_distance = 10.0
    str_error = landXml.set_axis_points(points_distance)
    if str_error:
        print(f"Error:\n\t{str_error}")
        return
    str_error, wkt_linestring = landXml.get_axis_points_as_wktlinestring()
    if str_error:
        print(f"Error:\n\t{str_error}")
        return
    # output_json_file_path = current_path + "/data/LAV_Tafalla_eje+rasante+subbalasto.json"
    # output_json_file_path = os.path.normpath(output_json_file_path)
    # str_error = landXml.write_to_json_file(output_json_file_path)
    # if str_error:
    #     print(f"Error:\n\t{str_error}")
    #     return


if __name__ == '__main__':
    main()
