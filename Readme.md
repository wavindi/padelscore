#!/bin/bash
# Boot directly to Padel Scoreboard

sleep 5
unclutter -idle 0.5 -root &
xset s off && xset -dpms && xset s noblank

# Start your Python backend
cd /home/pi/padel-scoreboard  
python3 padel_backend_final.py &

# Wait for Flask server to start
sleep 3

# Launch in fullscreen kiosk mode
chromium-browser \
    --kiosk \
    --start-maximized \
    --disable-infobars \
    --noerrdialogs \
    http://localhost:5000
Make it executable and auto-start:

bash
chmod +x ~/start_padel_kiosk.sh

# Add to autostart
nano ~/.config/lxsession/LXDE-pi/autostart
# Add this line:
@/home/pi/start_padel_kiosk.sh
Why This is PERFECT for Your Scoreboard:
✅ Super Simple: One script, no extra dependencies
✅ True Fullscreen: --kiosk mode, no way to exit accidentally
✅ Touch Optimized: Works perfectly with Pi touchscreen
✅ Auto-Starts: Boots directly to your scoreboard
✅ Reliable: Python + Chromium, battle-tested combination
✅ Fast: Minimal overhead, maximum performance

Your Raspberry Pi will:

Boot up normally

Start the GUI

Launch your script

Start Python backend

Open Chromium in fullscreen kiosk mode

Display your beautiful padel scoreboard!

Users will see ONLY your scoreboard - no desktop, no menu bars, no distractions. Pure professional touch interface!

This is exactly what you want for a dedicated padel scoring device. Simple, robust, and foolproof!

