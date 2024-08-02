python3 -m venv .venv

source .venv/bin/activate

python3 -m pip install -r requirements.txt

env QT_QPA_PLATFORM=xcb WAYLAND_DISPLAY= python3 ./FOLON-Downgrader.py
