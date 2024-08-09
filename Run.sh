python3 -m venv .venv

source .venv/bin/activate

if ! env QT_QPA_PLATFORM=xcb WAYLAND_DISPLAY= python3 ./FOLON-Downgrader.py --linux ; then
    echo "Please check dependencies from here https://github.com/Fallout-London/FOLON-FO4Downgrader/blob/main/LinuxDeps.md"
fi
