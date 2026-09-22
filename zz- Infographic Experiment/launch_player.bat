@echo off
title Launching Infographics Master Player
cd /d "%~dp0"
echo Starting local web server on port 8508...
start "" http://localhost:8508/full_player.html
python -m http.server 8508
pause
