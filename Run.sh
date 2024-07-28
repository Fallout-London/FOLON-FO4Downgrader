python -m venv .venv

source venv/bin/activate

pip install -r requirements.txt

env QT_QPA_PLATFORM=xcb WAYLAND_DISPLAY= python3 ./FOLON-Downgrader.py