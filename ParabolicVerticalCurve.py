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

# http://www.landxml.org/schema/landxml-1.2/documentation/LandXML-1.2Doc_ParaCurve.html
class ParabolicVerticalCurve:
    def __init__(self,
                 profile_aligment,
                 length,
                 desc,
                 cumulative_distance,
                 elevation):
        self.profile_aligment = profile_aligment
        self.length = None
        self.description = None
        self.cumulative_distance = None
        self.elevation = None
