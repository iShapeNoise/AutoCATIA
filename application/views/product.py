from flask import render_template
from application.support.properties import get_properties_with_titles
from application import app
from application.support.properties import get_properties
from application.support.documents import get_product_document
from application.views.view_wrappers import catia_v5_required


@app.route('/product')
@catia_v5_required
def product():
    return render_template(
        'product.html',
    )

@app.route('/product/new')
@catia_v5_required
def product_new():
    default_properties = get_properties_with_titles(None, 'default', 'product')
    user_defined_properties = get_properties_with_titles(None, 'user', 'product')

    return render_template(
        'product_new.html',
        default_properties=default_properties,
        user_defined_properties=user_defined_properties
    )

@app.route('/product/edit')
@catia_v5_required
def product_edit():
    from application.support.load_properties import get_open_products, load_product_properties

    # Get open products
    open_products = get_open_products()

    # Select product automatically if only one, or empty if multiple
    selected_product = open_products[0] if len(open_products) == 1 else ''

    # Load properties for selected product
    default_properties = {}
    user_defined_properties = {}
    errors = []

    if selected_product:
        default_properties, user_defined_properties, errors = load_product_properties(selected_product)

    return render_template(
        'product_edit.html',
        open_products=open_products,
        selected_product=selected_product,
        default_properties=default_properties,
        user_defined_properties=user_defined_properties,
        errors=errors
    )


@app.route('/product/reorder')
@catia_v5_required
def product_reorder():
    return render_template(
        'product_reorder.html',
    )


@app.route('/product/renumber_instances')
@catia_v5_required
def product_renumber_instances():
    return render_template(
        'product_renumber_instances.html',
    )


@app.route('/product/properties')
@catia_v5_required
def product_properties():
    from application.support.documents import get_product_document

    pt_product_document, errors = get_product_document(product_only=False)

    if errors:
        return render_template('partials/errors.html', errors=errors)

    product = pt_product_document.product

    default_properties = get_properties(product, 'default')
    user_defined_properties = get_properties(product, 'user')

    return render_template(
        'product_properties.html',
        default_properties=default_properties,
        user_defined_properties=user_defined_properties,
    )
