@app.route('/drawing-format', methods=['GET', 'POST'])
def drawing_format():
    formats = {
        "A4 Portrait": (210, 297),
        "A4 Landscape": (297, 210),
        "A3 Landscape": (420, 297),
    }
    if request.method == 'POST':
        selected = request.form['format']
        width, height = formats[selected]
        # Use pycatia to create drawing
        from pycatia import catia
        app_catia = catia()
        drawing = app_catia.documents.add("Drawing")
        sheet = drawing.sheets.active_sheet
        sheet.set_size(width, height)
        return f"<p>Drawing created: {selected} ({width}x{height} mm)</p>"

    return render_template('drawing_format.html', formats=formats.keys())
