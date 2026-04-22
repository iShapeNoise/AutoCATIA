from flask import request, render_template

from application import app
from application.pycatia_scripts.part.new_part import create_new_part
from application.support.documents import get_product_document
from application.views.url_prefixes import htmx
from application.support.properties import get_properties


@app.route(f'{htmx}/part/create_new', methods=['POST'])
def htmx_create_new_part():
    # DEBUG: Log request arrival
    print("=== DEBUG: HTMX endpoint htmx_create_new_part called ===")

    # DEBUG: Print all form data received
    print("=== DEBUG: Form data received at HTMX endpoint ===")
    for key, value in request.form.items():
        print(f"{key}: {value}")
    print("================================")

    output = create_new_part(request.form)
    data = output['data']
    errors = output['errors']

    # Only get properties if part creation was successful
    default_attributes = {}
    user_attributes = {}

    if not errors:
        try:
            pt_product_document, doc_errors = get_product_document(product_only=False)
            if not doc_errors:
                product = pt_product_document.product
                default_attributes = get_properties(product, 'default')
                user_attributes = get_properties(product, 'user')
        except Exception as e:
            print(f"=== DEBUG: Error getting properties: {e} ===")

    print(f"=== DEBUG: Data: {data}, Errors: {errors} ===")

    return render_template(
        'partials/form_attributes.html',
        default_attributes=default_attributes,
        user_attributes=user_attributes,
        data=data,
        errors=errors
    )


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
