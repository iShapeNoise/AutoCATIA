from pycatia.exception_handling import CATIAApplicationException
from pycatia.product_structure_interfaces.product import Product
from werkzeug.datastructures import ImmutableMultiDict
from win32.lib.pywintypes import com_error

from application.pycatia_scripts.settings import product_template, drawing_template
from application.pycatia_scripts.settings import load_settings, settings_data

# Define property lists at module level 
default_property_list = list(settings_data.get('default_attributes', {}).keys())
user_defined_property_list = list(settings_data.get('user_attributes', {}).keys())

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
        property_list = user_defined_property_list

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
                        try:
                            # German COM interface workaround
                            cad_property = user_ref_properties.item(property)
                            properties[property] = cad_property.value
                        except (CATIAApplicationException, com_error):
                            # If item() fails, try to create and get the property
                            try:
                                user_ref_properties.create_string(property, '')
                                cad_property = user_ref_properties.item(property)
                                properties[property] = cad_property.value
                            except (CATIAApplicationException, com_error):
                                # Final fallback - use empty string
                                properties[property] = ''
            except (AttributeError, CATIAApplicationException):
                properties[property] = ''
                if type_ == 'user':
                    properties[property] = settings_data.get('user_attributes', {}).get(property, '')

    return properties


def update_properties_enum(product: Product, form: ImmutableMultiDict):
    """
    Update both Default and User Defined properties using enum-based approach
    """

    # Update Default Attributes
    update_default_properties(product, form)

    # Update User Defined Attributes
    update_user_defined_properties(product, form)


def update_default_properties(product: Product, form: ImmutableMultiDict):
    """
    Update Default Attributes with German interface workaround for description
    """

    for key in form.keys():
        if key in default_property_list:
            value = form.get(key)
            # Special handling for part_number - use direct assignment
            if key == 'part_number':
                try:
                    setattr(product, key, value)
                except Exception as e:
                    print(f"=== DEBUG: Error setting {key}: {e} ===")
            # Special handling for source - use enum for language independence
            elif key == 'source':
                try:
                    source_value = form.get(key)
                    if source_value not in ['Unknown', '']:
                        # Map English values to enum indices
                        source_mapping = {
                            'Unknown': 0,
                            'Built': 1,
                            'Bought': 2
                        }
                        enum_value = source_mapping.get(source_value, 0)
                        # Use enum-based approach for language independence
                        product.source = enum_value
                except Exception as e:
                    print(f"=== DEBUG: Error setting source: {e} ===")
            # Special handling for description - German interface workaround
            elif key == 'description':
                try:
                    # Try standard approach first
                    setattr(product, key, value)
                    # Retry with German interface if needed
                    if value and value.strip():
                        try:
                            # Alternative approach for German interface
                            product.Description = value
                        except:
                            pass
                except Exception as e:
                    # Try alternative approach for German interface
                    try:
                        if value and value.strip():
                            product.Description = value
                    except:
                        pass
            # Handle other default properties
            else:
                try:
                    setattr(product, key, value)
                except Exception as e:
                    print(f"=== DEBUG: Error setting {key}: {e} ===")


def update_user_defined_properties(product: Product, form: ImmutableMultiDict):
    """
    Update User Defined Attributes with automatic date generation for new parts
    """

    from datetime import datetime

    print("=== DEBUG: Starting User Defined Attributes update ===")

    # Get user attributes from settings
    user_attrs = settings_data.get('user_attributes', {})

    if not user_attrs:
        return


    user_ref_properties = product.user_ref_properties

    for attr_name in user_attrs.keys():
        # Special handling for date field - auto-generate for new parts
        if attr_name == 'date':
            # Check if this is a new part (form has date field but it's empty)
            form_date = form.get('date', '')
            if not form_date:  # Empty means new part, generate date
                date_value = datetime.now().strftime("%d/%m/%Y")
            else:  # Has value means editing existing part
                date_value = form_date

            # Create/update the date field using the original name
            try:
                existing_prop = user_ref_properties.item('date')
                existing_prop.value = date_value
            except CATIAApplicationException:
                # Create new date field
                user_ref_properties.create_string('date', date_value)
            except com_error:
                # Alternative creation method
                user_ref_properties.create_string('date', date_value)
            continue

        # Handle other user attributes normally
        value = form.get(attr_name, '')

        try:
            existing_prop = user_ref_properties.item(attr_name)
            existing_prop.value = value
        except CATIAApplicationException:
            user_ref_properties.create_string(attr_name, value)
        except com_error as e:
            # Try alternative creation method
            try:
                user_ref_properties.create_string(attr_name, value)
            except Exception as e2:
                print(f"=== DEBUG: Failed to create UDA '{attr_name}': {e2} ===")


def update_properties(product: Product, form: ImmutableMultiDict):
    """
    Update both Default and User Defined properties
    """
    # Update Default Attributes
    update_default_properties(product, form)

    # Update User Defined Attributes - NOW ENABLED
    update_user_defined_properties(product, form)


def get_form_title(form_type: str) -> str:
    """
    Get the appropriate title based on form type
    """
    if form_type == 'product':
        return 'Product'
    else:
        return 'Part'


def get_properties_with_titles(product: Product | None, type_: str, form_type: str = 'part'):
    """
    Enhanced get_properties that includes conditional form type handling
    :param product: CATIA Product object
    :param type_: 'default' or 'user'
    :param form_type: 'part' or 'product'
    :return: Properties dictionary with form type metadata
    """
    properties = get_properties(product, type_)


    return properties
