python -m venv .venv

call .venv\Scripts\activate.bat

python -m pip install -r requirements.txt
python -m pip install -U pyinstaller
python -m pip install -U black
python -m black FOLON-Installer.py

pyinstaller --clean -y FOLON-Installer.spec

call .venv\Scripts\deactivate.bat