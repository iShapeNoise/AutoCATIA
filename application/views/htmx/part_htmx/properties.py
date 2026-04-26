from flask import request, render_template
from application import app
from application.support.documents import get_part_document
from application.support.properties import update_properties, get_properties
from application.views.url_prefixes import htmx


@app.route(f'{htmx}/part/properties', methods=['POST'])
def htmx_part_properties():
    print("=== DEBUG: HTMX part properties endpoint called ===")

    pt_part_document, errors = get_part_document()

    if errors:
        return render_template(
            'partials/form_product_properties.html',
            default_properties={},
            user_defined_properties={},
            errors=errors
        )

    # CRITICAL: Save document FIRST before any property operations
    try:
        print("=== DEBUG: Saving document before property updates ===")
        pt_part_document.part_document.save()
        print("=== DEBUG: Document saved successfully ===")
    except Exception as e:
        print(f"=== DEBUG: Error saving document: {e} ===")

    # Update properties with document reference
    update_properties(pt_part_document.product, request.form)

    # Force CATIA to update
    try:
        pt_part_document.part.update()
        print("=== DEBUG: Part updated ===")
    except Exception as e:
        print(f"=== DEBUG: Error updating part: {e} ===")

    # Save again after property updates
    try:
        print("=== DEBUG: Saving document after property updates ===")
        pt_part_document.part_document.save()
        print("=== DEBUG: Final save completed ===")
    except Exception as e:
        print(f"=== DEBUG: Error in final save: {e} ===")

    # Now reload properties
    default_properties = get_properties(pt_part_document.product, 'default')
    user_defined_properties = get_properties(pt_part_document.product, 'user')

    print("=== DEBUG: Properties reloaded for display ===")

    return render_template(
        'partials/form_product_properties.html',
        default_properties=default_properties,
        user_defined_properties=user_defined_properties
    )
