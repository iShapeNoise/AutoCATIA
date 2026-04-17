from flask import render_template

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
    default_properties = get_properties(None, 'default')
    user_defined_properties = get_properties(None, 'user')

    return render_template(
        'product_new.html',
        default_properties=default_properties,
        user_defined_properties=user_defined_properties
    )

@app.route('/product/edit')
@catia_v5_required
def product_edit():
    from application.pycatia_scripts.product.edit_product import check_open_products
    from application.support.documents import get_product_document
    from application.support.properties import get_properties

    # Get open products
    open_products = check_open_products()

    # Set selected product
    selected_product = ''
    if len(open_products) == 1:
        selected_product = open_products[0]

    # Get properties for the selected product if available
    default_properties = {}
    user_defined_properties = {}

    if selected_product:
        try:
            pt_product_document, errors = get_product_document(product_only=False)
            if not errors:
                product = pt_product_document.product
                default_properties = get_properties(product, 'default')
                user_defined_properties = get_properties(product, 'user')
        except:
            pass

    return render_template(
        'product_edit.html',
        open_products=open_products,
        selected_product=selected_product,
        default_properties=default_properties,
        user_defined_properties=user_defined_properties
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
