"""
CATIA Default Attributes Enum Mappings for Language Independence
These mappings use CATIA's internal enum indices instead of string names
"""

# CATIA Product Default Attributes Enums
PRODUCT_DEFAULT_ATTRIBUTES = {
    'part_number': 1001,      # Internal CATIA enum for PartNumber
    'revision': 1002,         # Internal CATIA enum for Revision
    'nomenclature': 1003,     # Internal CATIA enum for Nomenclature
    'definition': 1004,       # Internal CATIA enum for Definition
    'source': 1005,           # Internal CATIA enum for Source
    'description': 1006,      # Internal CATIA enum for Description
}

# CATIA Source Enum Values (for dropdown)
SOURCE_ENUM_VALUES = {
    'Unknown': 0,     # catSourceUnknown
    'Built': 1,       # catSourceBuilt
    'Bought': 2,      # catSourceBought
}

def get_property_enum_index(property_name: str) -> int:
    """Get the enum index for a CATIA Default Attribute"""
    return PRODUCT_DEFAULT_ATTRIBUTES.get(property_name, 0)

def get_source_enum_value(source_text: str) -> int:
    """Get the enum value for Source dropdown"""
    return SOURCE_ENUM_VALUES.get(source_text, 0)
