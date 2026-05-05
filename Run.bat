@echo off
:: Change directory to the folder where this batch file is located
cd /d "%~dp0"

:: Set the Flask application variable
set FLASK_APP=application.py

:: Set debug mode
set FLASK_DEBUG=1

:: Run the Flask development server
flask run --debug

:: Pause to see output
pause