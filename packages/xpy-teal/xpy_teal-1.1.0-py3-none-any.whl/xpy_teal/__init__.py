# src/xpy_teal/__init__.py

# Import modules from Codes
from .Codes import (
    dataIO,
    config,
    math_tools,
    download_xp_spectra,
    spectrum_tools,
    line_analysis,
    xpy_teal_pipeline,
)

# Import constants from config
from .Codes.config import _DEFAULT_DATA_DIR, _XML_FILE_PATH
from .Codes.dataIO import create_data_dir, create_default_config

# Set up default data directory and configuration file
create_data_dir(_DEFAULT_DATA_DIR)
create_default_config(_XML_FILE_PATH)


__all__ = [
    "spectrum_tools",
    "math_tools",
    "dataIO",
    "config",
    "line_analysis",
    "xpy_teal_pipeline",
    "download_xp_spectra",
    "_DEFAULT_DATA_DIR",
    "_XML_FILE_PATH",
    "create_data_dir",
    "create_default_config",
    "read_config_xml",
]