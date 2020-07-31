#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import sys
from time import time, sleep
import subprocess


logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)


def setup_env():
    """
    Any initial setup can be added here 
    """
    try:
        MONITOR_BOT_TOKEN = os.environ["MONITOR_BOT_TOKEN"]
        with open("covid19indiatracker_bot/credentials/TOKEN", "w") as f:
            print(MONITOR_BOT_TOKEN, file=f)
    except KeyError:
        logging.error("Bot credentials not found in environment")
        raise


def main():
    """
    Setup env and execute the process in a different thread
    Sleep till LIFESPAN
    Once awake, pass on genes and die

    """
    # How long the container exist
    LIFESPAN = 1 * 60 * 60

    setup_env()
    cmd = ["python3", "covid19indiatracker_bot.py"]
    p = subprocess.Popen(cmd, stderr=sys.stdout, cwd="covid19indiatracker_bot/tracker/")
    logging.info("Start sleeping... 💤")
    sleep(LIFESPAN)
    logging.info("Enough for the day! Passing on to next Meeseek")


if __name__ == "__main__":
    main()
