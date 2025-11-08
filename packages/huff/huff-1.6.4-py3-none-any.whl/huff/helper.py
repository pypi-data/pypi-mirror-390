#-----------------------------------------------------------------------
# Name:        helper (huff package)
# Purpose:     Huff Model helper functions and definitions
# Author:      Thomas Wieland 
#              ORCID: 0000-0001-5168-9846
#              mail: geowieland@googlemail.com              
# Version:     1.1.6
# Last update: 2025-11-07 16:51
# Copyright (c) 2025 Thomas Wieland
#-----------------------------------------------------------------------


import pandas as pd
import numpy as np
from math import pi


# Basic config:
FLOAT_ROUND = 3

# Permitted location types:
PERMITTED_LOCATION_TYPES = [
    "origins",
    "destinations"
]


# Market area models config:

# Default column names:
DEFAULT_COLNAME_ATTRAC = "A_j"
DEFAULT_COLNAME_TC = "t_ij"
DEFAULT_COLNAME_UTILITY = "U_ij"
DEFAULT_COLNAME_UTILITY_SUM = "U_i"
DEFAULT_COLNAME_MARKETSIZE = "C_i"
DEFAULT_COLNAME_PROBABILITY = "p_ij"
DEFAULT_COLNAME_FLOWS = "E_ij"
DEFAULT_COLNAME_CUSTOMER_ORIGINS = "i"
DEFAULT_COLNAME_SUPPLY_LOCATIONS = "j"
DEFAULT_COLNAME_INTERACTION = "ij"
DEFAULT_COLNAME_TOTAL_MARKETAREA = "T_j"

# Default column name suffixes:
DEFAULT_LCT_SUFFIX = "__LCT"
DEFAULT_WEIGHTED_SUFFIX = "_weighted"
DEFAULT_OBSERVED_SUFFIX = "_emp"

DEFAULT_OBSERVED_COL = "observed"
DEFAULT_EXPECTED_COL = "expected"

DEFAULT_COLNAME_ATTRAC_WEIGHTED = f"{DEFAULT_COLNAME_ATTRAC}{DEFAULT_WEIGHTED_SUFFIX}"
DEFAULT_COLNAME_TC_WEIGHTED = f"{DEFAULT_COLNAME_TC}{DEFAULT_WEIGHTED_SUFFIX}"

DEFAULT_COLNAME_PROBABILITY_OBSERVED = f"{DEFAULT_COLNAME_PROBABILITY}{DEFAULT_OBSERVED_SUFFIX}"
DEFAULT_COLNAME_FLOWS_OBSERVED = f"{DEFAULT_COLNAME_FLOWS}{DEFAULT_OBSERVED_SUFFIX}"
DEFAULT_COLNAME_TOTAL_MARKETAREA_OBSERVED = f"{DEFAULT_COLNAME_TOTAL_MARKETAREA}{DEFAULT_OBSERVED_SUFFIX}"

# Default descriptions:
DEFAULT_NAME_ATTRAC = "Attraction"
DEFAULT_NAME_TC = "Transport costs"
DEFAULT_NAME_MARKETSIZE = "Market size"
DEFAULT_NAME_CUSTOMER_ORIGINS = "Customer origins"
DEFAULT_NAME_SUPPLY_LOCATIONS = "Supply locations"

# Default weighting functions:
PERMITTED_WEIGHTING_FUNCTIONS = {
    "power": {
        "description": "Power function",
        "function": "a*(values**b)",
        "no_params": 1
        },
    "exponential": {
        "description": "Exponential function",
        "function": "a*np.exp(b*values)",
        "no_params": 1
        },
    "logistic": {
        "description": "Logistic function",
        "function": "1+np.exp(b+c*values)",
        "no_params": 2
        },
    "linear": {
        "description": "Linear function",
        "function": "a+(b*values)",
        "no_params": 1
        }
    }
PERMITTED_WEIGHTING_FUNCTIONS_LIST = list(PERMITTED_WEIGHTING_FUNCTIONS.keys())

MCI_TRANSFORMATIONS = {
    "LCT": "Log-centering transformation",
    "ILCT": "Inverse log-centering transformation"
}
MCI_TRANSFORMATIONS_LIST = list(MCI_TRANSFORMATIONS.keys())
DEFAULT_MCI_TRANSFORMATION = MCI_TRANSFORMATIONS_LIST[0]


APE_PREFIX = "APE"
APE_MIN = 1
APE_MAX = 100

GOODNESS_OF_FIT = {
    "Sum of squared residuals": "SQR",
    #"Sum of absolute residuals": "SAR",
    "R-squared": "Rsq",
    "Mean squared error": "MSE",
    "Root mean squared error": "RMSE",
    "Mean absolute error": "MAE",
    "Mean absolute percentage error": "MAPE",
    "Symmetric MAPE": "sMAPE",
    #"Negative log-likelihood": "LL",
    "Deviations <  5 %": f"{APE_PREFIX}5",
    "Deviations < 10 %": f"{APE_PREFIX}10",
    #"Deviations < 15 %": f"{APE_PREFIX}15",
    #"Deviations < 20 %": f"{APE_PREFIX}20",
    #"Deviations < 25 %": f"{APE_PREFIX}25",
    #"Deviations < 30 %": f"{APE_PREFIX}30",
    #"Deviations < 35 %": f"{APE_PREFIX}35",
    #"Deviations < 40 %": f"{APE_PREFIX}40",
    #"Deviations < 45 %": f"{APE_PREFIX}45",
    #"Deviations < 50 %": f"{APE_PREFIX}50",
}



# ORS config:

ORS_SERVER = "https://api.openrouteservice.org/v2/"
ORS_URL_RESTRICTIONS = "https://openrouteservice.org/restrictions/"

ORS_HEADERS = {
    "Content-Type": "application/json; charset=utf-8",
    "Accept": "application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8",    
}

ORS_AUTH = "5b3ce3597851110001cf62480a15aafdb5a64f4d91805929f8af6abd"
# for TESTING

ORS_ENDPOINTS = {
    "Isochrones": {
        "endpoint": "isochrones/",
        "Restrictions": {
            "Locations": 5,
            "Intervals": 10,
            "Range distance": 120,
            "Range time (Foot profiles)": 20,
            "Range time (Cycling profiles)": 5,
            "Range time (Driving profiles)": 1
        },
        "Parameters": {
            "unit": {
                "param": "range_type",
                "type": str,
                "options": {
                    "time": {
                        "description": "Time [minutes]",
                        "param": "time"
                    },
                    "distance": {
                        "description": "Distance [meters]",
                        "param": "distance"
                    }
                },
            },
        }
    },
    "Matrix": {
        "endpoint": "matrix/",
        "Restrictions": {
            "Locations (origin x destination)": 3500            
        },
        "Parameters": {
            "unit": {
                "param": "metrics",
                "type": str,
                "options": {
                    "time": {
                        "description": "Time [minutes]",
                        "param": "duration"
                    },
                    "distance": {
                        "description": "Distance [meters]",
                        "param": "distance"
                    }
                },
            },
        },
    }
}

ORS_PROFILES = {
    "Driving car": "driving-car",
    "Driving heavy goods vehicle": "driving-hgv",
    "Walking by foot": "foot-walking",
}
ORS_PROFILES_LIST = ORS_PROFILES.keys()
ORS_PROFILES_LIST_API = list(ORS_PROFILES.values())

ORS_RANGE_TYPES = {
    "Time [minutes]": "time",
    "Distance [meters]": "distance"
    }
ORS_RANGE_TYPES_LIST = ORS_RANGE_TYPES.keys()
ORS_RANGE_TYPES_LIST_API = list(ORS_RANGE_TYPES.values())

ORS_SEGMENT_COL = "segment"


# OSM config:

OSM_TILES_SERVER = "http://a.tile.openstreetmap.org/"

DEFAULT_FILENAME_ORS_TMP = "osm_map.png"


# GIS constants and defaults:

MATRIX_OD_SEPARATOR = "_"

MATRIX_COL_SOURCE = "source"
MATRIX_COL_DESTINATION = "destination"


WGS84_EPSG = 4326
WGS84_CRS = f"EPSG:{WGS84_EPSG}"
PSEUDO_MERCATOR_EPSG = 3857
PSEUDO_MERCATOR_CRS = f"EPSG:{PSEUDO_MERCATOR_EPSG}"

DISTANCE_TYPES = {
    "Euclidean distance": "euclidean",
    "Manhattan distance": "manhattan"
}
DISTANCE_TYPES_LIST = list(DISTANCE_TYPES.keys())
DISTANCE_TYPES_LIST_FUNC = list(DISTANCE_TYPES.values())

DEFAULT_SEGMENTS_COL = ORS_SEGMENT_COL

DEFAULT_LAYER_ALPHA = 0.6
DEFAULT_LAYER_LABEL = "Layer"
DEFAULT_LEGEND_LOC = "lower right"
DEFAULT_LEGEND_FONTSIZE = "small"


# Helper functions:

def weighting(
    values: pd.Series,
    func: str,
    b: float,
    c: float = None,
    a: float = 1.0
    ):
    
    if func not in PERMITTED_WEIGHTING_FUNCTIONS_LIST:
        raise ValueError (f"Parameter 'func' must be one of {', '.join(PERMITTED_WEIGHTING_FUNCTIONS_LIST)}")
    
    if not check_numeric_series(values):
        raise TypeError("Vector given by parameter 'series' is not numeric")    
    
    result = None
    
    calc_formula = PERMITTED_WEIGHTING_FUNCTIONS[func]["function"]
    
    calc_dict = {"a": a, "b": b, "values": values, "np": np}
    
    if "c" in calc_formula:
        if c is None:
            raise ValueError("Parameter 'c' must be provided for this function")
        calc_dict["c"] = c
        
    result = eval(calc_formula, {}, calc_dict)
    
    return result


def log_centering_transformation(
    df: pd.DataFrame,
    ref_col: str,
    cols: list,
    suffix: str = DEFAULT_LCT_SUFFIX
    ):
   
    check_vars(
        df = df,
        cols = cols
        )
    
    if ref_col not in df.columns:
        raise KeyError(f"Error in log-centering transformation: Column '{ref_col}' not in dataframe.")

    def lct (x):

        x_geom = np.exp(np.log(x).mean())
        x_lct = np.log(x/x_geom)

        return x_lct
    
    for var in cols:
        
        unique_values = df[var].unique()
        if set(unique_values).issubset({0, 1}):
            df[var+suffix] = df[var]
            print (f"Column {var} is a dummy variable and requires/allows no log-centering transformation")
            continue

        if (df[var] <= 0).any():
            df[var+suffix] = float("nan")
            print (f"Column {var} contains values <= 0. No log-centering transformation possible.")
            continue

        var_t = df.groupby(ref_col)[var].apply(lct)
        var_t = var_t.reset_index()
        df[var+suffix] = var_t[var]

    return df


def check_vars(
    df: pd.DataFrame,
    cols: list,
    check_numeric: bool = True,
    check_zero: bool = True
    ):

    for col in cols:
        if col not in df.columns:
            raise KeyError(f"Column '{col}' not in dataframe.")
    
    if check_numeric:
        for col in cols:
            if not check_numeric_series(df[col]):
                raise TypeError(f"Column '{col}' is not numeric. All stated columns must be numeric.")
    
    if check_zero:
        for col in cols:
            if (df[col] <= 0).any():
                raise ValueError(f"Column '{col}' includes values <= 0. All values must be numeric and positive.")


def lonlat_transform(
    source: list,
    destination: list,
    transform: bool = True
    ):

    lon1 = source[0]
    lat1 = source[1]
    lon2 = destination[0]
    lat2 = destination[1]

    if transform:
        lat1_r = lat1*pi/180
        lon1_r = lon1*pi/180
        lat2_r = lat2*pi/180
        lon2_r = lon2*pi/180

        return lat1_r, lat2_r, lon1_r, lon2_r
    
    else:

        return lat1, lat2, lon1, lon2


def check_numeric_series(
    values: pd.Series
    ):
    
    if not pd.api.types.is_numeric_dtype(values):
        return False
    else:
        return True