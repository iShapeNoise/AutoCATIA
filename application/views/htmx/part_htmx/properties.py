from flask import request, render_template

from application import app
from application.support.documents import get_part_document
from application.support.properties import update_properties, get_properties
from application.views.url_prefixes import htmx


@app.route(f'{htmx}/part/properties', methods=['POST'])
def htmx_part_properties():
    pt_part_document, errors = get_part_document(part_only=False)
    part = pt_part_document.product  # Part has product interface for properties

    update_properties(part, request.form)

    default_attributes = get_properties(part, 'default')
    user_attributes = get_properties(part, 'user')

    return render_template(
        'partials/form_attributes.html',
        default_attributes=default_attributes,
        user_attributes=user_attributes
    )
