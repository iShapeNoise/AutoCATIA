from pathlib import Path
import os
import yaml

def read_yaml(f: Path):
    """Reads the contents of the yaml file `f` and returns the data."""
    data = None
    try:
        with open(f, encoding='utf-8') as file:
            data = yaml.safe_load(file)
    except (FileNotFoundError, yaml.YAMLError) as e:
        print(f"Error reading {f}: {e}")
    return data

def create_default_settings(userdata_path: Path):
    """Create default settings.yaml in userdata/ folder"""
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
                'APPROVED-BY': "",
                'DATE': "",
                'DRAWING-NUMBER': "",
                'CREATED-BY': "",
                'REVISION': "",
                'SCALE': "",
                'SIZE': "",
                'TICKET': "",
                'TITLE': "",
                'TOTAL-SHEETS': "",
                'YEAR': ""
            },
            'sheet_names': ['Sheet.1', 'Sheet.2'],
            'template_name': 'AutoCATIA Template',
            'tolerances': {
                'x': '±0.1',
                'xx': '±0.01',
                'xxx': '±0.001'
            },
            'units': 'MILLIMETERS',
            'logo': 'autocatia-logo.jpg'
        },
        'part_template': {
            'geometric_sets': ['Geometrical Set.1', 'Geometrical Set.2'],
            'parameters': {
                'Thickness': {
                    'type': 'length',
                    'value': 2
                },
                'InternalBendRadius': {
                    'type': 'length',
                    'value': 2
                }
            }
        },
        'product_template': {
            'user_ref_properties': {
                'TITLE': '',
                'CHECKED BY': '',
                'DATE APPROVED': '',
                'REVISION': 'A'
            }
        },
        'drawing': {
            'pdf': {
                'exclude_sheets': ['Details', 'DXF']
            },
            'dxf': {
                'include_sheets': ['DXF']
            }
        },
        'language': 'en'
    }

    settings_file = userdata_path / 'settings.yaml'
    try:
        with open(settings_file, 'w', encoding='utf-8') as f:
            yaml.dump(default_settings, f, default_flow_style=False, allow_unicode=True)
        print(f"Created default settings at {settings_file}")
    except Exception as e:
        print(f"Error creating default settings: {e}")

def load_settings():
    """Load and merge settings from multiple sources"""
    # Get application root (3 levels up from pycatia_scripts/settings.py)
    app_root = Path(__file__).parent.parent.parent
    userdata_path = Path(app_root, 'userdata')

    # Read ISO standards
    iso_file = Path(app_root, 'application', 'static', 'standards', 'ISO_216')
    iso_standards = read_yaml(iso_file) or {}

    # Read user settings
    settings_file = userdata_path / 'settings.yaml'

    if not settings_file.exists():
        print("Settings file not found, creating defaults...")
        userdata_path.mkdir(exist_ok=True)
        create_default_settings(userdata_path)
        yaml_data = read_yaml(settings_file)
    else:
        yaml_data = read_yaml(settings_file)

    # Merge ISO standards with user settings
    if yaml_data and 'drawing_template' in yaml_data:
        # Override sheet_sizes with ISO standards
        yaml_data['drawing_template']['sheet_sizes'] = iso_standards.get('sheet_sizes', {})
    else:
        # Fallback if no user settings
        yaml_data = {
            'drawing_template': {
                'sheet_sizes': iso_standards.get('sheet_sizes', {}),
                # Add other required defaults...
            }
        }

    return yaml_data

# Get application root for path construction
app_root = Path(__file__).parent.parent.parent
path_prefix = app_root

# Load all settings
yaml_data = load_settings()

# Extract template data with defaults
drawing_template = yaml_data.get('drawing_template', {})
part_template = yaml_data.get('part_template', {})
product_template = yaml_data.get('product_template', {})
