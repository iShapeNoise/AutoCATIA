from pathlib import Path
import json
import os
from flask import session, request

class LanguageManager:
    def __init__(self, lang_dir='static/lang'):
        app_root = Path(os.path.dirname(__file__)).parent
        self.lang_dir = Path(app_root, lang_dir)
        self.translations = self._load_translations()

    @property
    def current_lang(self):
        """Lazy load current language from session or settings file"""
        # First check session (current request)
        if 'language' in session:
            return session['language']

        # If not in session, try to load from settings file
        try:
            app_root = Path(__file__).parent.parent.parent
            settings_path = Path(app_root, 'userdata', 'settings')
            if settings_path.exists():
                with open(settings_path, 'r') as f:
                    settings_data = json.load(f)
                    if settings_data and 'language' in settings_data:
                        # Store in session for future requests
                        session['language'] = settings_data['language']
                        return settings_data['language']
        except:
            pass

        # Fall back to English
        return 'en'

    def _load_translations(self):
        translations = {}
        for lang_file in self.lang_dir.glob('*'):
            if lang_file.is_file() and lang_file.suffix == '':  # Files without extension
                lang_code = lang_file.name
                with open(lang_file, 'r', encoding='utf-8') as f:
                    translations[lang_code] = json.load(f)
        return translations

    def get_available_languages(self):
        return list(self.translations.keys())

    def set_language(self, lang_code):
        if lang_code in self.translations:
            session['language'] = lang_code

    def t(self, key, default=None):
        keys = key.split('.')
        value = self.translations.get(self.current_lang, {})

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                # Fallback to English if key not found
                value = self.translations.get('en', {})
                for k in keys:
                    if isinstance(value, dict) and k in value:
                        value = value[k]
                    else:
                        return default or key
                break

        return value if value != '' else (default or key)

# Global instance
lang_manager = LanguageManager()
