#!/usr/bin/env python

import logging
import os
import signal
import sys
import time
from datetime import datetime

import requests
import schedule

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

# Set our hosts from the HOSTS environmental variable
# See docker-compose.yml for how that works.
hosts = os.environ.get("HOSTS", "127.0.0.1").split(",")

# Settings is the dict which holds ... the settings
settings = {}

# Default apps - enable time and disable the rest
settings["TIM"] = os.environ.get("TIM", True)
settings["DAT"] = os.environ.get("DAT", False)
settings["HUM"] = os.environ.get("HUM", False)
settings["TEMP"] = os.environ.get("TEMP", False)
settings["BAT"] = os.environ.get("BAT", False)

# Auto Brightness & Auto App Switch (if more than one)
settings["ABRI"] = True
settings["ATRANS"] = True
settings["TEFF"] = os.environ.get("TEFF", 10)  # Transition Effect

# Time Format, Day of Week, C or F Temp
settings["SOM"] = os.environ.get(
    "SOM", True
)  # Week start on Monday; false is start on Sunday
settings["CEL"] = os.environ.get("CEL", True)  # Degrees C; False is Degrees F
settings["TMODE"] = os.environ.get("TMODE", 0)  # 1 is the default, I like no calendar
settings["TFORMAT"] = os.environ.get("TFORMAT", "%H:%M")  # 12 hour time
settings["WD"] = os.environ.get("WD", False)  # Show the day of week?
settings["OVERLAY"] = "clear"  # Zero out weather by default


def night_mode_on():
    """Activate night mode settings on all connected clocks.

    Night mode features:
    - Red time display color
    - Fixed low brightness (1)
    - Disabled auto-brightness
    - Disabled automatic app switching
    """
    settings["TIME_COL"] = "#FF0000"
    settings["ABRI"] = False
    settings["BRI"] = 1
    settings["ATRANS"] = False
    logger.info("Night Mode On")
    update_device()


def night_mode_off():
    """Deactivate night mode and restore day mode settings on all connected clocks.

    Day mode features:
    - White text color
    - Auto brightness enabled
    - Automatic app switching enabled
    - Weather overlay cleared
    """
    settings["TIME_COL"] = "#FFFFFF"
    settings["ABRI"] = True
    settings["ATRANS"] = True
    settings["OVERLAY"] = "clear"
    logger.info("Night Mode Off")
    update_device()


def update_device():
    """Update all connected clock devices with current settings.

    Sends settings, switches to time app, and turns off indicators for each host.
    Handles various error types with appropriate logging.
    """
    for host in hosts:
        try:
            # First, load our settings
            response = requests.post(
                f"http://{host}/api/settings", json=settings, timeout=10
            )
            response.raise_for_status()

            # Now switch to the time app
            response = requests.post(
                f"http://{host}/api/switch", json={"name": "Time"}, timeout=10
            )
            response.raise_for_status()

            # Turn off all three indicators (they sometimes turn on unexpectedly)
            for indicator in ["indicator1", "indicator2", "indicator3"]:
                response = requests.post(
                    f"http://{host}/api/{indicator}", json={"color": "0"}, timeout=10
                )
                response.raise_for_status()

            logger.info(f"{host} updated successfully")

        except requests.exceptions.Timeout:
            logger.error(f"Timeout while updating {host}")
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection failed to {host} - host may be unreachable")
        except requests.exceptions.HTTPError as e:
            logger.error(
                f"HTTP error {e.response.status_code} from {host}: {e.response.text}"
            )
        except requests.exceptions.RequestException as e:
            logger.error(f"Unexpected error updating {host}: {e}")


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    logger.info(f"Received signal {signum}, exiting gracefully...")
    sys.exit(0)


def main():
    """Main application entry point.

    Initializes signal handlers, sets initial day/night mode based on current time,
    and runs the scheduled update loop.
    """
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    logger.info(f"AwTrix Manager starting at {datetime.now()}")

    # Set initial mode based on current time
    if datetime.now().hour < 6 or datetime.now().hour >= 20:
        night_mode_on()
    else:
        night_mode_off()

    # Schedule Day / Night Mode updates:
    schedule.every().day.at("06:00").do(night_mode_off)
    schedule.every().day.at("20:00").do(night_mode_on)

    # Start the schedule loop
    logger.info("Starting Schedule Loop")
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
