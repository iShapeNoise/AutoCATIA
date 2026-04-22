from pycatia.exception_handling import CATIAApplicationException
from pycatia.product_structure_interfaces.product import Product
from werkzeug.datastructures import ImmutableMultiDict
from win32.lib.pywintypes import com_error

from application.pycatia_scripts.settings import product_template

# Default property list
default_property_list = [
    'part_number',
    'revision',
    'nomenclature',
    'definition',
    'source',
    'description'
]

def get_properties(product: Product | None, type_: str):
    """
    :param product:
    :param type_: Must be either default or user
    :return:
    """
    property_list = []
    if type_ == 'default':
        property_list = default_property_list
    elif type_ == 'user':
        # Get user properties from settings
        user_props = product_template.get('user_ref_properties', {})
        property_list = list(user_props.keys())

    properties = {}

    # Always include all properties in the list, even if product is None
    for property in property_list:
        properties[property] = ''  # Default to empty string

        if product:
            try:
                if type_ == 'default':
                    properties[property] = getattr(product, property)
                elif type_ == 'user':
                    user_ref_properties = product.user_ref_properties
                    if user_ref_properties:
                        cad_property = user_ref_properties.item(property)
                        properties[property] = cad_property.value
            except (AttributeError, CATIAApplicationException):
                properties[property] = ''
                if type_ == 'user':
                    properties[property] = product_template['user_ref_properties'].get(property, '')

    return properties


def update_properties(product: Product, form: ImmutableMultiDict):
    """
    Update product properties with proper UDA creation
    """

    # Get user defined properties from settings
    user_props = product_template.get('user_ref_properties', {})
    user_defined_property_list = list(user_props.keys())

    # Add common UDAs that should be created
    additional_udas = ['number', 'title', 'material', 'created_by', 'approved_by']
    all_user_properties = user_defined_property_list + additional_udas

    print(f"=== DEBUG: User defined property list: {all_user_properties} ===")

    for key in form.keys():
        # Handle default properties
        if key in default_property_list:
            if key == 'part_number':
                try:
                    product.part_number = form.get(key)
                    print(f"=== DEBUG: Set part_number to: {form.get(key)} ===")
                except Exception as e:
                    print(f"=== DEBUG: Error setting part_number: {e} ===")
            elif key == 'source':
                # Handle source with enum mapping
                source_value = form.get(key)
                if source_value not in ['Unknown', '']:
                    source_mapping = {'Built': 1, 'Bought': 2}
                    if source_value in source_mapping:
                        try:
                            product.source = source_mapping[source_value]
                            print(f"=== DEBUG: Set source to enum: {source_mapping[source_value]} ===")
                        except Exception as e:
                            print(f"=== DEBUG: Error setting source: {e} ===")
            else:
                try:
                    setattr(product, key, form.get(key))
                    print(f"=== DEBUG: Set {key} to: {form.get(key)} ===")
                except Exception as e:
                    print(f"=== DEBUG: Error setting {key}: {e} ===")

        # Handle user defined properties - CREATE THEM IF THEY DON'T EXIST
        if key in all_user_properties:
            user_ref_properties = product.user_ref_properties
            try:
                # Try to get existing property
                user_ref_property = user_ref_properties.item(key)
                user_ref_property.value = form.get(key)
                print(f"=== DEBUG: Updated existing UDA {key}: {form.get(key)} ===")
            except (CATIAApplicationException, com_error):
                # Create new property if it doesn't exist
                try:
                    user_ref_properties.create_string(key, form.get(key))
                    print(f"=== DEBUG: Created new UDA {key}: {form.get(key)} ===")
                except Exception as e:
                    print(f"=== DEBUG: Failed to create UDA {key}: {e} ===")
