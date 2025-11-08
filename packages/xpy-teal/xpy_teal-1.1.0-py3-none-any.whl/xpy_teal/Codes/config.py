from pathlib import Path
import os

# taking inspiration from Emily's Repo: https://github.com/emilyhunt/hr_selection_function/tree/main


_CONFIG = dict()

# the Configuration directory cannot be changed by the user
_CONFIG["CONFIG_DIR"] = Path(__file__).resolve().parent.parent / "Configuration_Data"

# the Data directory can be changed by the user via an environment variable
_DEFAULT_DATA_DIR = os.getenv("XPy_TEAL_DATA_DIR", None)
if _DEFAULT_DATA_DIR is None:
    _DEFAULT_DATA_DIR = Path.cwd() / "XPy_TEAL_Results"

# convert to Path if it's a str
if isinstance(_DEFAULT_DATA_DIR, str):
    try:
        _DEFAULT_DATA_DIR = Path(_DEFAULT_DATA_DIR)
    except Exception as e:
        raise ValueError(f"Invalid _DEFAULT_DATA_DIR: {_DEFAULT_DATA_DIR}") from e
if not isinstance(_DEFAULT_DATA_DIR, Path):
    raise TypeError(f"_DEFAULT_DATA_DIR must be a str or pathlib.Path, got {type(_DEFAULT_DATA_DIR)}")


# Default Configuration XML (can be overridden by environment variable)

_XML_FILE_PATH = os.getenv("XPy_TEAL_CONFIG_XML", None)
if _XML_FILE_PATH is None:
    _XML_FILE_PATH = Path.cwd() / "XPy_TEAL_config.xml"

# convert to Path if it's a str
if isinstance(_XML_FILE_PATH, str):
    try:
        _XML_FILE_PATH = Path(_XML_FILE_PATH)
    except Exception as e:
        raise ValueError(f"Invalid _XML_FILE_PATH: {_XML_FILE_PATH}") from e
if not isinstance(_XML_FILE_PATH, Path):
    raise TypeError(f"_XML_FILE_PATH must be a str or pathlib.Path, got {type(_XML_FILE_PATH)}")


