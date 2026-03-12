from flask import Blueprint, redirect, url_for, session, request
from application.pycatia_scripts.language import lang_manager

language_bp = Blueprint('language', __name__)

@language_bp.route('/set_language/<lang_code>')
def set_language(lang_code):
    lang_manager.set_language(lang_code)
    return redirect(request.referrer or url_for('home'))
