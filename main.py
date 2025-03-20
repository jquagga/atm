#!/usr/bin/env python

import os
import time
from datetime import datetime

import requests
import schedule

# Set our hosts from the HOSTS environmental variable
# See docker-compose.yml for how that works.
hosts = os.environ.get("HOSTS", "127.0.0.1").split(",")

# Settings is the dict which holds ... the settings
settings = {}

# Default apps - enable time and disable the rest
settings["TIM"] = True
settings["DAT"] = False
settings["HUM"] = False
settings["TEMP"] = False
settings["BAT"] = False

# Auto Brightness & Auto App Switch (if more than one)
settings["ABRI"] = True
settings["ATRANS"] = True
settings["TEFF"] = 10  # Transition Effect

# Time Format, Day of Week, C or F Temp
settings["SOM"] = False  # Week start on Monday; false is start on Sunday
settings["CEL"] = False  # Degrees C; False is Degrees F
settings["TMODE"] = 0  # 1 is the default, I like no calendar
settings["TFORMAT"] = "%l:%M"  # 12 hour time
settings["WD"] = False  # Show the day of week?
settings["OVERLAY"] = "clear"  # Zero out weather by default


def night_mode_on():
    # Red screen, no app switching, minimal brightness
    settings["TIME_COL"] = "#FF0000"
    settings["ABRI"] = False
    settings["BRI"] = 1
    settings["ATRANS"] = False
    print("Night Mode On")
    update_device()


def night_mode_off():
    # White text, auto brightness, app switching (if more than one)
    settings["TIME_COL"] = "#FFFFFF"
    settings["ABRI"] = True
    settings["ATRANS"] = True
    settings["OVERLAY"] = "clear"
    print("Night Mode Off")
    update_device()


def update_device():
    for host in hosts:
        print(host)
        # Ok, first lets load our settings
        requests.post(f"http://{host}/api/settings", json=settings)
        # Now switch to the time app
        requests.post(f"http://{host}/api/switch", json={"name": "Time"})
        # And now lets go through and make sure the 3 indicators are turned off
        # They seem to turn on for no reason?
        for indicator in ["indicator1", "indicator2", "indicator3"]:
            requests.post(f"http://{host}/api/{indicator}", json={"color": "0"})


def main():
    print(datetime.now())
    if datetime.now().hour < 6 or datetime.now().hour >= 20:
        night_mode_on()
    else:
        night_mode_off()

    # Schedule Day / Night Mode updates:
    schedule.every().day.at("06:00").do(night_mode_off)
    schedule.every().day.at("20:00").do(night_mode_on)

    # Finally, let's start the loop to run updates on the schedule:
    print("Starting Schedule Loop")
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
