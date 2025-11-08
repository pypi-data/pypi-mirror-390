from .config import _CONFIG
from pathlib import Path
import xml.etree.ElementTree as ET

# taking inspiration from Emily's Repo: https://github.com/emilyhunt/hr_selection_function/tree/main


def read_xml():
    """
    Reads an XML file and returns a dictionary containing the text content of each element.

    Args:
        file_path (str): The path to the XML file.

    Returns:
        dict: A dictionary where the keys are the element tags and the values are the text content of each element.
    """
    tree = ET.parse(_CONFIG["CONFIG_XML_FILE_PATH"])
    root = tree.getroot()

    element_texts = {}

    for element in root.iter():
        if element != root:
            element_texts[element.tag] = element.text

    return element_texts

# Default XML content
DEFAULT_XML_CONTENT = """<?xml version="1.0" encoding="UTF-8"?>
<SpectraRequest>
  <list_of_default_lines>Halpha</list_of_default_lines>
  <list_of_line_wavelengths>450,573.5</list_of_line_wavelengths>
  <provide_all_extrema>true</provide_all_extrema>
  <provide_equivalent_widths>true</provide_equivalent_widths>
  <output_format>csv</output_format>
  <number_of_cores>6</number_of_cores>
  <data_release>DR3</data_release>
</SpectraRequest>
"""

def create_default_config(config_xml_path):
    """Create the default XML config file if it doesn't exist."""

    # if config_xml_path is str, convert to Path
    if isinstance(config_xml_path, str):
        try:
            config_xml_path = Path(config_xml_path)
        except Exception as e:
            raise ValueError(f"Invalid config_xml_path: {config_xml_path}") from e
    if not isinstance(config_xml_path, Path):
        raise TypeError(f"config_xml_path must be a str or pathlib.Path, got {type(config_xml_path)}")
    if not config_xml_path.exists():
        config_xml_path.write_text(DEFAULT_XML_CONTENT, encoding="utf-8")
        print(f"Default config created at {config_xml_path}")


    _CONFIG["CONFIG_XML_FILE_PATH"] = config_xml_path


def create_data_dir(data_dir):
    """Create the data directory if it doesn't exist."""

    # if data_dir is str, convert to Path
    if isinstance(data_dir, str):
        try:
            data_dir = Path(data_dir)
        except Exception as e:
            raise ValueError(f"Invalid data_dir path: {data_dir}") from e
    
    if not isinstance(data_dir, Path):
        raise TypeError(f"data_dir must be a str or pathlib.Path, got {type(data_dir)}")

    if not data_dir.exists():
        data_dir.mkdir(parents=True, exist_ok=True)
        print(f"Data directory created at: {data_dir}. Henceforth, all results will be stored here.")

    _CONFIG["DATA_DIR"] = data_dir