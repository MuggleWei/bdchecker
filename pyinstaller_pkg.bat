@echo off

setlocal ENABLEDELAYEDEXPANSION

set origin_dir=%~dp0
cd %origin_dir%

python -m venv venv
call venv\Scripts\activate.bat
pip install -r requirements-dev.txt

pyinstaller -F bdchecker\main.py --distpath dist\bdchecker -n bdchecker
xcopy README.md dist\bdchecker\ /Y
xcopy README_cn.md dist\bdchecker\ /Y
xcopy LICENSE dist\bdchecker\ /Y

call venv\Scripts\deactivate.bat