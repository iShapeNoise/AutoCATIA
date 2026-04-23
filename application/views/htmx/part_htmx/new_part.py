from flask import request, render_template

from application import app
from application.pycatia_scripts.part.new_part import create_new_part
from application.support.documents import get_product_document
from application.views.url_prefixes import htmx
from application.support.properties import get_properties
from application.pycatia_scripts.settings import load_settings


@app.route(f'{htmx}/part/create_new', methods=['POST'])
def htmx_create_new_part():
    output = create_new_part(request.form)
    data = output['data']
    errors = output['errors']

    if errors:
        # Return JSON for error popup
        return {
            'success': False,
            'message': 'Error creating part: ' + '; '.join(errors),
            'data': None
        }

    # Get the newly created part's properties for form update
    pt_product_document, get_errors = get_product_document(product_only=False)
    product = pt_product_document.product

    # Get both default and user properties from the new part
    default_properties = get_properties(product, 'default')
    user_defined_properties = get_properties(product, 'user')

    # Render form HTML for UI update
    form_html = render_template(
        'partials/form_product_properties.html',
        default_properties=default_properties,
        user_defined_properties=user_defined_properties,
        form_type='part',
        data=None,  # Don't show success message in form
        errors=[]   # Don't show errors in form
    )

    # Return JSON for success popup and form update
    return {
        'success': True,
        'message': data,
        'form_html': form_html
    }


@app.route(f'{htmx}/check_file_exists', methods=['GET'])
def htmx_check_file_exists():
    from pathlib import Path
    import os

    file_name = request.args.get('file', '')
    if not file_name:
        return {'exists': False}

    # Check in current directory and common project directories
    current_dir = os.getcwd()
    project_path = request.args.get('path', current_dir)

    full_path = Path(project_path) / file_name
    exists = full_path.exists()

    return {'exists': exists}
