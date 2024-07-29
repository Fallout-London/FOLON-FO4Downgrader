python -m venv .venv\win

call .venv\win\Scripts\activate.bat

python -m pip install -r requirements.txt
python -m pip install -U pyinstaller
python -m pip install -U black
python -m black FOLON-Downgrader.py

python -m PyInstaller --clean -y "FOLON-Downgrader.spec"

call .venv\win\Scripts\deactivate.bat

echo "https://gist.github.com/PaulCreusy/7fade8d5a8026f2228a97d31343b335e"
echo "signtool sign /f ./certificate.pfx /p <password> /fd SHA256 /tr http://timestamp.digicert.com /td SHA256 .\dist\FOLON-Downgrader.exe"