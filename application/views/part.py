from flask import render_template
from application.support.properties import get_properties
from application import app
from application.views.view_wrappers import catia_v5_required


@app.route('/part')
@catia_v5_required
def part():
    return render_template(
        'part.html',
    )


@app.route('/part/new')
@catia_v5_required
def part_new():
    from application.pycatia_scripts.settings import load_settings
    settings_data = load_settings()

    return render_template(
        'part_new.html',
        default_attributes=settings_data.get('default_attributes', {}),
        user_attributes=settings_data.get('user_attributes', {})
    )


@app.route('/part/edit')
@catia_v5_required
def part_edit():
    from application.pycatia_scripts.part.edit_part import check_open_parts
    from application.support.properties import get_properties
    from application.pycatia_scripts.settings import load_settings

    # Get all open parts
    open_parts = check_open_parts()

    # Select part automatically if only one, or empty if multiple
    selected_part = open_parts[0] if len(open_parts) == 1 else ''

    # Initialize attributes
    default_attributes = {}
    user_attributes = {}

    # Load settings for fallback
    settings_data = load_settings()

    if selected_part:
        try:
            from application.support.documents import get_part_document
            pt_part_document, errors = get_part_document(part_only=False)
            if not errors:
                part = pt_part_document.product  # Part has product interface for properties
                default_attributes = get_properties(part, 'default')
                user_attributes = get_properties(part, 'user')
        except:
            # Fallback to settings if CATIA access fails
            default_attributes = settings_data.get('default_attributes', {})
            user_attributes = settings_data.get('user_attributes', {})
    else:
        # Use settings defaults when no part selected
        default_attributes = settings_data.get('default_attributes', {})
        user_attributes = settings_data.get('user_attributes', {})

    return render_template(
        'part_edit.html',
        open_parts=open_parts,
        selected_part=selected_part,
        default_attributes=default_attributes,
        user_attributes=user_attributes
    )


@app.route('/part/points')
@catia_v5_required
def part_points():
    return render_template(
        'part_points.html',
    )


@app.route('/part/bounding_box')
@catia_v5_required
def part_bounding_box():
    return render_template(
        'part_bounding_box.html',
    )
