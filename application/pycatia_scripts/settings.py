from pathlib import Path
import os
import json


def read_json(f: Path):
    """Reads the contents of the json file `f` and returns the data."""
    data = None
    try:
        with open(f, encoding='utf-8') as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading {f}: {e}")
    return data


def create_default_settings(userdata_path: Path):
    """Create default settings in userdata/ folder"""
    default_settings = {
        # New attribute sections
        'default_attributes': {
            'part_number': '',
            'revision': '',
            'nomenclature': '',
            'definition': '',
            'source': 'Unknown',
            'description': ''
        },
        'user_attributes': {
            'number': '',
            'title': '',
            'extra_title': '',
            'created_by': '',
            'approved_by': '',
            'material': '',
            'blank': '',
            'date': '[ dd / mm / yyyy ]'
        },
        'drawing_template': {
            'border_offset': 10,
            'company_details': {
                'name': 'AutoCATIA',
                'address': [
                    'github',
                    'url: https://github.com/iShapeNoise/AutoCATIA',
                    'email: yenz4xyz@gmail.com'
                ]
            },
            # Keep only automatic parameters
            'parameters': {
                'scale': '1:1',
                'document_type': '',
                'format': '',
                'page': '1/1'
            },
            'logo': '',
            'projection_method': 'PM_EU.jpg',
            'template_name': 'DT-001 A',
            'tolerances': {
                ',X': '±1,5',
                ',XX': '±,75',
                ',XXX': '±,25'
            },
            'units': ['METRIC', 'MILLIMETRES']
        },
        # Keep other existing sections
        'part_template': {
            'geometric_sets': ['ReferenceGeometry', 'MasterGeometry', 'ConstructionGeometry'],
            'parameters': {
                'Thickness': {'type': 'length', 'value': 2},
                'InternalBendRadius': {'type': 'length', 'value': 2}
            }
        },
        'notifications': {
            'enabled': True,
            'visibility_seconds': 2
        },
        # Add new checkbox defaults at root level
        'text_field_enabled': True,
        'gdt_enabled': False,
        'gdt_general_abc': False,
        'gdt_general_ab': False,
        'gdt_welded_structure': False,
        'gdt_of_rz_63': False,
        'gdt_ofz_general': False,
        'gdt_ofz_wxy': False,
        'gdt_ofz_main_specs': False,
        'gdt_ofz_main_raw': False,
        'gdt_ofz_main': False,
        'gdt_edges_iso': False,
        'gdt_thermally_cut': False,
        'bom': {
            'columns': {
                'title': True,
                'created_by': True,
                'subject': False,
                'description': True,
                'keywords': False,
                'category': False,
                'status': False,
                'material': True,
                'mass': True,
                'part_number': True,
                'rev': True,
                'project': False,
                'custom': False,
                'date': True,
                'last_saved_by': False,
                'last_modified_time': False,
                'checked_by': True,
                'manager': False,
                'company': False,
                'hyperlink_base': False,
                'pos': True,
                'part_number_2': False,
                'quantity': True,
                'object_quantity': False,
                'base_unit': False,
                'base_quantity': False,
                'bom_structure': False,
                'comment': True
            },
        },
    }

    settings_file = Path(userdata_path, 'settings')
    with open(settings_file, 'w', encoding='utf-8') as f:
        json.dump(default_settings, f, indent=2, ensure_ascii=False)
    print(f"Created default settings at {settings_file}")


def load_settings():
    """Load and merge settings from multiple sources"""
    app_root = Path(__file__).parent.parent.parent
    userdata_path = Path(app_root, 'userdata')
    iso_file = Path(app_root, 'application', 'static', 'standards', 'ISO_216')
    iso_5457_file = Path(app_root, 'application', 'static', 'standards', 'ISO_5457')
    settings_file = Path(userdata_path, 'settings')

    # Initialize settings_data before using it
    settings_data = {}

    # Create userdata directory if it doesn't exist
    userdata_path.mkdir(exist_ok=True)

    # Create default settings if file doesn't exist
    if not settings_file.exists():
        create_default_settings(userdata_path)

    # Load ISO standard
    iso_standards_data = read_json(iso_file)
    iso_5457_data = read_json(iso_5457_file)

    # Load user settings
    if settings_file.exists():
        user_settings = read_json(settings_file)
        settings_data.update(user_settings)

    # Merge ISO standards into drawing template
    if 'drawing_template' not in settings_data:
        settings_data['drawing_template'] = {}

    if iso_standards_data:
        settings_data['drawing_template']['sheet_sizes'] = iso_standards_data.get('sheet_sizes', {})
        settings_data['iso_standards'] = iso_standards_data

    if iso_5457_data:
        settings_data['iso_5457'] = iso_5457_data

    # Ensure notifications structure exists
    if 'notifications' not in settings_data:
        settings_data['notifications'] = {'enabled': False, 'visibility_seconds': 2}

    return settings_data

# Load settings and expose module-level variables
settings_data = load_settings()
drawing_template = settings_data['drawing_template']
part_template = settings_data.get('part_template', {})
product_template = settings_data.get('product_template', {})
yaml_data = settings_data  # Keep for backward compatibility
iso_standards = settings_data.get('iso_standards', {})
iso_5457 = settings_data.get('iso_5457', {})
path_prefix = Path(__file__).parent.parent.parent
