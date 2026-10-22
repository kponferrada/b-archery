#!/bin/sh
# Jamie's Crossbows - every offline check. Needs python3 (Pillow, numpy) and lua5.1.
#   sh run_all.sh [<game media folder>]     (with the game folder: also checks vanilla sounds and animation clips)
set -e
cd "$(dirname "$0")"
MEDIA=../../Contents/mods/JamiesCrossbowsWIP/42/media
python3 lint.py ../../Contents
if [ -n "$1" ]; then python3 check_scripts.py "$MEDIA" --game "$1"; else python3 check_scripts.py "$MEDIA"; fi
lua5.1 run_tests.lua > /tmp/jc_server_tests.txt || { cat /tmp/jc_server_tests.txt; exit 1; }
tail -1 /tmp/jc_server_tests.txt
lua5.1 run_client.lua > /tmp/jc_client_tests.txt || { cat /tmp/jc_client_tests.txt; exit 1; }
tail -1 /tmp/jc_client_tests.txt
echo "all offline checks passed"
