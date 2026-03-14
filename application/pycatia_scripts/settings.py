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
            'parameters': {
                'APPROVED-BY': '[ approved ]',
                'DATE': '[ mm / yyyy ]',
                'DRAWING-NUMBER': '[ drawing number ]',
                'CREATED-BY': '',
                'REVISION': 'XX',
                'SCALE': '[ scale ]',
                'SIZE': 'aa',
                'TICKET': '[ #00000 ]',
                'TITLE': '[ title ]',
                'TOTAL-SHEETS': '00',
                'YEAR': '[ year ]'
            },
            'sheet_names': ['Sheet.1', 'Sheet.2'],
            'logo': 'autocatia-logo.jpg',
            'template_name': 'DT-001 A',
            'tolerances': {
                ',X': '±1,5',
                ',XX': '±,75',
                ',XXX': '±,25'
            },
            'units': ['METRIC', 'MILLIMETRES']
        },
        'part_template': {
            'geometric_sets': ['ReferenceGeometry', 'MasterGeometry', 'ConstructionGeometry'],
            'parameters': {
                'Thickness': {'type': 'length', 'value': 2},
                'InternalBendRadius': {'type': 'length', 'value': 2}
            }
        },
        'product_template': {
            'user_ref_properties': {
                'TITLE': '',
                'DRAWN BY': '',
                'CHECKED BY': '',
                'DATE APPROVED': '',
                'REVISION': 'A'
            }
        },
        'drawing': {
            'pdf': {'exclude_sheets': ['Details', 'DXF']},
            'dxf': {'include_sheets': ['DXF']}
        }
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
