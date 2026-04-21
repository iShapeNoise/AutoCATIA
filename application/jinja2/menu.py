from flask import url_for, render_template
from application import app
from application.pycatia_scripts.language import lang_manager

with app.app_context():
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
                'url': url_for('part_edit'),
                'title': 'pages.part.edit_part'
            }
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
                'url': url_for('product_edit'),
                'title': 'pages.product.edit_product'
            }
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
                'url': url_for('drawing_edit_page'),
                'title': 'pages.drawing.edit_page'
            },
            {
                'url': url_for('drawing_views'),
                'title': 'pages.drawing.views'
            },
            {
                'url': url_for('drawing_bom'),
                'title': 'pages.drawing.bom'
            },
            {
                'url': url_for('drawing_save_as'),
                'title': 'pages.drawing.save_as'
            },
        ]
    }

    # Tools menu
    m_dict_tools = {
        'title': 'menu.tools',
        'url': url_for('tools'),
        'menu_items': [
            {
                'url': url_for('tools_symbol_from_image'),
                'title': 'pages.tools.symbol_from_image'
            },
        ]
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
        m_dict_tools,
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


def render_menu(option: str, current_route: str = None):
    from application.pycatia_scripts.language import lang_manager
    from flask import request

    if current_route is None:
        current_route = request.endpoint

    # For main menu, use existing logic
    if option == 'menu':
        return render_menu_header()

    # For submenus, use URL-based matching
    m_dict = None
    if option == 'part':
        m_dict = m_dict_part
    if option == 'product':
        m_dict = m_dict_product
    if option == 'drawing':
        m_dict = m_dict_drawing
    if option == 'tools':
        m_dict = m_dict_tools

    if m_dict:
        # Apply translations
        translated_menu = {
            'title': lang_manager.t(m_dict['title'], m_dict['title']),
            'url': m_dict['url'],
            'menu_items': []
        }

        for item in m_dict['menu_items']:
            translated_item = {
                'url': item['url'],
                'title': lang_manager.t(item['title'], item['title']),
                # Use URL-based matching instead of endpoint matching
                'active': item['url'] in request.url
            }
            translated_menu['menu_items'].append(translated_item)

        m_dict = translated_menu

    return render_template('partials.menu.html', m_dict=m_dict)
