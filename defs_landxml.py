# authors:
# David Hernandez Lopez, david.hernandez@uclm.es

XML_DOCUMENT_TAG = "LandXML"
XML_DOCUMENT_ATTRIBUTE_VERSION_TAG = "@version"
valid_versions = ["1.2"] # ["1.0", "1.1"]
XML_DOCUMENT_PROJECT_TAG = "Project"
XML_ELEMENT_PROJECT_ATTRIBUTE_NAME_TAG = "@name"
XML_DOCUMENT_UNITS_TAG = "Units"
XML_ELEMENT_UNITS_METRIC_TAG = "Metric"
XML_ELEMENT_UNITS_METRIC_ATTRIBUTE_LINEAR_UNIT_TAG = "@linearUnit"
XML_ELEMENT_UNITS_METRIC_ATTRIBUTE_ANGULAR_UNIT_TAG = "@angularUnit"
LINEAR_UNIT_METER = 'meter'
valid_linear_units = [LINEAR_UNIT_METER]
ANGULAR_UNIT_DEG = 'decimal degrees'
ANGULAR_UNIT_GRAD ='grads'
valid_angular_units = [ANGULAR_UNIT_DEG, ANGULAR_UNIT_GRAD]


XML_DOCUMENT_CRS_TAG = "CoordinateSystem"
XML_ELEMENT_CRS_ATTRIBUTE_WKT_TAG = "@ogcWktCode"
XML_DOCUMENT_ALIGMENTS_TAG = "Alignments"
XML_ELEMENT_ALIGMENTS_ATTRIBUTE_NAME_TAG = "@name"
XML_ELEMENT_ALIGMENTS_ALIGMENT_TAG = "Alignment"
XML_ELEMENT_ALIGMENTS_ALIGMENT_ATTRIBUTE_NAME_TAG = "@name"
XML_ELEMENT_ALIGMENTS_ALIGMENT_ATTRIBUTE_STASTART_TAG = "@staStart"
# Distance to the location on the basis of the control point(the cumulative distance station
# of the start point in the following figure)
XML_ELEMENT_ALIGMENTS_ALIGMENT_ATTRIBUTE_LENGTH_TAG = "@length"

