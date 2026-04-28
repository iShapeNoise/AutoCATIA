from flask import render_template
from application.support.properties import get_properties
from application import app
from application.views.view_wrappers import catia_v5_required
from application.support.properties import get_properties_with_titles


@app.route('/part')
@catia_v5_required
def part():
    return render_template(
        'part.html',
    )


@app.route('/part/new')
@catia_v5_required
def part_new():
    from application.support.properties import get_properties

    default_properties = get_properties(None, 'default')
    user_defined_properties = get_properties(None, 'user')

    return render_template(
        'part_new.html',
        default_properties=default_properties,
        user_defined_properties=user_defined_properties
    )


@app.route('/part/edit')
@catia_v5_required
def part_edit():
    from application.pycatia_scripts.part.edit_part import check_open_parts
    from application.support.properties import get_properties

    # Get all open parts
    open_parts = check_open_parts()

    # Select part automatically if only one, or empty if multiple
    selected_part = open_parts[0] if len(open_parts) == 1 else ''

    # Always start with empty properties for stable layout
    default_properties = get_properties(None, 'default')
    user_defined_properties = get_properties(None, 'user')

    return render_template(
        'part_edit.html',
        open_parts=open_parts,
        selected_part=selected_part,
        default_properties=default_properties,
        user_defined_properties=user_defined_properties
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
