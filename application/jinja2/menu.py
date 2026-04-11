from flask import url_for, render_template
from application import app
from application.pycatia_scripts.language import lang_manager

with app.app_context():
    # Part menu
    m_dict_part = {
        'title': 'menu.part',
        'url': url_for('part'),
        'menu_items': [
            {
                'url': url_for('part_new'),
                'title': 'pages.part.new_part'
            },
            {
                'url': url_for('part_points'),
                'title': 'pages.part.points'
            },
            {
                'url': url_for('part_bounding_box'),
                'title': 'pages.part.bounding_box'
            },
        ]
    }

    # Product menu
    m_dict_product = {
        'title': 'menu.product',
        'url': url_for('product'),
        'menu_items': [
            {
                'url': url_for('product_new'),
                'title': 'pages.product.new_product'
            },
            {
                'url': url_for('product_reorder'),
                'title': 'pages.product.reorder_product_tree'
            },
            {
                'url': url_for('product_renumber_instances'),
                'title': 'pages.product.renumber_instances'
            },
            {
                'url': url_for('product_properties'),
                'title': 'pages.product.edit_product_properties'
            },
        ]
    }

    # Drawing menu
    m_dict_drawing = {
        'title': 'menu.drawing',
        'url': url_for('drawing'),
        'menu_items': [
            {
                'url': url_for('drawing_new'),
                'title': 'pages.drawing.new_drawing'
            },
            {
                'url': url_for('drawing_add_page'),
                'title': 'pages.drawing.add_page'
            },
            {
                'url': url_for('drawing_views'),
                'title': 'pages.drawing.views'
            },
            {
                'url': url_for('drawing_save_as'),
                'title': 'pages.drawing.save_as'
            },
        ]
    }

    # Home menu
    m_dict_home = {
        'title': 'menu.home',
        'url': url_for('home'),
    }

    # Documents menu
    m_dict_documents = {
        'title': 'menu.documents',
        'url': url_for('documents'),
    }

    # Settings menu
    m_dict_settings = {
        'title': 'menu.settings',
        'url': url_for('settings'),
    }

    m_list = [
        m_dict_home,
        m_dict_documents,
        m_dict_part,
        m_dict_product,
        m_dict_drawing,
    ]


def render_menu_header():
    from application.pycatia_scripts.language import lang_manager

    # Apply translations to main menu items
    translated_m_list = []
    for menu_item in m_list:
        translated_item = menu_item.copy()
        if 'title' in translated_item:
            translated_item['title'] = lang_manager.t(translated_item['title'], translated_item['title'])
        translated_m_list.append(translated_item)

    return render_template('partials.menu_header.html', m_list=translated_m_list)


def render_menu(option: str):
    from application.pycatia_scripts.language import lang_manager

    m_dict = None

    if option == 'menu':
        m_dict = m_dict_menu
    if option == 'part':
        m_dict = m_dict_part
    if option == 'product':
        m_dict = m_dict_product
    if option == 'drawing':
        m_dict = m_dict_drawing

    if m_dict:
        # Apply translations to the entire menu structure
        translated_menu = {
            'title': lang_manager.t(m_dict['title'], m_dict['title']),
            'url': m_dict['url'],
            'menu_items': []
        }

        for item in m_dict['menu_items']:
            translated_item = {
                'url': item['url'],
                'title': lang_manager.t(item['title'], item['title'])
            }
            translated_menu['menu_items'].append(translated_item)

        m_dict = translated_menu

    return render_template('partials.menu.html', m_dict=m_dict)
