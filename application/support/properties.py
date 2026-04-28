from pycatia.exception_handling import CATIAApplicationException
from pycatia.product_structure_interfaces.product import Product
from werkzeug.datastructures import ImmutableMultiDict
from win32.lib.pywintypes import com_error

from application.pycatia_scripts.settings import product_template, drawing_template
from application.pycatia_scripts.settings import load_settings, settings_data

# Define property lists at module level
default_property_list = list(settings_data.get('default_attributes', {}).keys())
user_defined_property_list = list(settings_data.get('user_attributes', {}).keys())
#user_defined_property_list = list(product_template.get('user_ref_properties', {}).keys())


def get_properties(product: Product | None, type_: str):
    """
    :param product:
    :param type_: Must be either default or user
    :return:
    """
    from application.pycatia_scripts.settings import settings_data

    property_list = []
    if type_ == 'default':
        property_list = default_property_list
    elif type_ == 'user':
        property_list = user_defined_property_list

    properties = {}

    # Always include all properties in the list, even if product is None
    for property in property_list:
        properties[property] = ''

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
                    properties[property] = product_template.get('user_ref_properties', {}).get(property, '')

    # Special handling for new forms (product is None) - construct part_number
    if product is None and type_ == 'default':
        # Get values from settings for new forms
        drawing_params = settings_data.get('drawing_template', {}).get('parameters', {})
        user_ref_props = settings_data.get('product_template', {}).get('user_ref_properties', {})

        # Get the three components
        number = user_ref_props.get('NUMBER', '001')  # From user defined
        title = user_ref_props.get('TITLE', 'Product')  # From user defined
        revision = drawing_params.get('REVISION', 'P01')  # From default attributes

        # Construct part_number
        properties['part_number'] = f"{number}_{title}_{revision}"

        # Also set individual values for form display
        properties['source'] = drawing_params.get('SOURCE', '0')
        properties['revision'] = revision

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
            # Special handling for source - use numeric values for language independence
            elif key == 'source':
                try:
                    source_value = form.get(key)
                    # Convert string to integer for CATIA enum
                    if source_value and source_value.isdigit():
                        enum_value = int(source_value)
                        # Validate enum range (0=Unknown, 1=Built, 2=Bought)
                        if 0 <= enum_value <= 2:
                            product.source = enum_value
                            print(f"=== DEBUG: Set source to {enum_value} ===")
                        else:
                            print(f"=== DEBUG: Invalid source value {enum_value}, using 0 ===")
                            product.source = 0
                    else:
                        # Fallback for empty or invalid values
                        product.source = 0
                except Exception as e:
                    print(f"=== DEBUG: Error setting source: {e} ===")
            # Special handling for description - German interface workaround
            elif key == 'description':
                try:
                    # Try standard approach first
                    setattr(product, key, value)
                except (AttributeError, TypeError):
                    # Fall back to German interface (capitalized property name)
                    try:
                        product.description = value
                    except AttributeError:
                        # If both approaches fail, log the error but don't crash
                        print(f"Warning: Could not set description property on product")
            # Handle other default properties
            else:
                try:
                    setattr(product, key, value)
                except Exception as e:
                    print(f"=== DEBUG: Error setting {key}: {e} ===")


def update_user_defined_properties(product, form):
    """
    Update User Defined Attributes for both Part and Product objects
    """
    print("=== DEBUG: Starting User Defined Attributes update ===")

    # Get user attributes from settings
    user_attrs = settings_data.get('user_attributes', {})

    for key in form.keys():
        if key in user_attrs:
            value = form.get(key)
            # Handle date field - set current date if empty
            if key.lower() == 'date':
                if not value or value == '[ dd / mm / yyyy ]':
                    from datetime import datetime
                    date_value = datetime.now().strftime("%d/%m/%Y")
            else:
                date_value = form.get(key)

            # Get the correct product interface for user properties
            if hasattr(product, 'part'):
                # This is a Part object, use its product interface
                user_ref_properties = product.product.user_ref_properties
            else:
                # This is a Product object, use directly
                user_ref_properties = product.user_ref_properties

            try:
                user_ref_property = user_ref_properties.item(key)
                user_ref_property.value = date_value
                print(f"=== DEBUG: Updated {key} = {date_value} ===")
            except CATIAApplicationException:
                user_ref_properties.create_string(key, date_value)
                print(f"=== DEBUG: Created {key} = {date_value} ===")
            except com_error:
                user_ref_properties.create_string(key, date_value)
                print(f"=== DEBUG: Created {key} = {date_value} (com_error) ===")

    print("=== DEBUG: User Defined Attributes update complete ===")


def update_properties(product: Product, form: ImmutableMultiDict):
    """
    Update properties for both Part and Product objects
    """
    print("=== DEBUG: Starting properties update ===")

    # Update default properties with error handling
    for key in form.keys():
        if key in default_property_list:
            try:
                setattr(product, key, form.get(key))
                print(f"=== DEBUG: Successfully set {key} = {form.get(key)} ===")
            except CATIAApplicationException as e:
                print(f"=== DEBUG: Could not set {key}: {e} ===")
                # Skip this property or use alternative method
                continue

    # Update user-defined properties with automatic date handling
    for key in form.keys():
        if key in user_defined_property_list:
            # Handle automatic date setting
            if key.lower() == 'date' and (not form.get(key) or form.get(key) == '[ dd / mm / yyyy ]'):
                from datetime import datetime
                date_value = datetime.now().strftime("%d/%m/%Y")
            else:
                date_value = form.get(key)

            try:
                user_ref_properties = product.user_ref_properties
                user_ref_property = user_ref_properties.item(key)
                user_ref_property.value = date_value
            except CATIAApplicationException:
                user_ref_properties.create_string(key, date_value)
            except com_error:
                user_ref_properties.create_string(key, date_value)

    print("=== DEBUG: Properties update complete ===")


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
