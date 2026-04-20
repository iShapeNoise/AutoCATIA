from pycatia.exception_handling import CATIAApplicationException
from pycatia.product_structure_interfaces.product import Product
from werkzeug.datastructures import ImmutableMultiDict
from win32.lib.pywintypes import com_error

from application.pycatia_scripts.settings import product_template

default_property_list = [
    'part_number',
    'revision',
    'nomenclature',
    'definition',
    'source',
    'description'
]

user_defined_property_list = [key for key in product_template['user_ref_properties']]


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
                        cad_property = user_ref_properties.item(property)
                        properties[property] = cad_property.value
            except (AttributeError, CATIAApplicationException):
                properties[property] = ''
                if type_ == 'user':
                    properties[property] = product_template['user_ref_properties'].get(property, '')

    return properties


def update_properties(product: Product, form: ImmutableMultiDict):
    """

    :param product:
    :param form:
    :return:
    """

    for key in form.keys():
        if key in default_property_list:
            setattr(product, key, form.get(key))
        if key in user_defined_property_list:
            user_ref_properties = product.user_ref_properties
            try:
                user_ref_property = user_ref_properties.item(key)
                user_ref_property.value = form.get(key)
            except CATIAApplicationException:
                user_ref_properties.create_string(key, form.get(key))
            except com_error:
                user_ref_properties.create_string(key, form.get(key))
