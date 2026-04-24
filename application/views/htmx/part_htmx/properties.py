from flask import request, render_template
from application import app
from application.support.documents import get_part_document
from application.support.properties import update_properties, get_properties
from application.views.url_prefixes import htmx

@app.route(f'{htmx}/part/properties', methods=['POST'])
def htmx_part_properties():
    pt_part_document, errors = get_part_document()

    if errors:
        return render_template(
            'partials/form_product_properties.html',
            default_properties={},
            user_defined_properties={},
            errors=errors,
            form_type='part'
        )

    part = pt_part_document.part

    # Update properties with form data
    update_properties(part, request.form)

    # Reload properties to get updated values
    default_properties = get_properties(part.product, 'default')
    user_defined_properties = get_properties(part.product, 'user')

    return render_template(
        'partials/form_product_properties.html',
        default_properties=default_properties,
        user_defined_properties=user_defined_properties,
        data='Part properties updated successfully',
        form_type='part'
    )
