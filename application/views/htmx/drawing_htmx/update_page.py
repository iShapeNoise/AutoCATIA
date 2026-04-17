from flask import request, render_template
from application import app
from application.views.url_prefixes import htmx
from application.pycatia_scripts.drawing.update_page import update_page_scale

@app.route(f'{htmx}/drawing/update_page', methods=['POST'])
def htmx_update_page():
    sheet_name = request.form.get('sheet_name')
    drawing_name = request.form.get('drawing_name')  # Add this line

    if not sheet_name:
        return render_template('partials/errors.html',
                             errors=['No sheet name provided'])

    from application.pycatia_scripts.drawing.update_page import update_page_scale
    result = update_page_scale(sheet_name, drawing_name)  # Pass drawing_name

    if result.get('success'):
        return render_template('partials/success.html',
                             data=result.get('message'))
    else:
        return render_template('partials/errors.html',
                             errors=[result.get('error')])
