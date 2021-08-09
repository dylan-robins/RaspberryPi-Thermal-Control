#!/usr/bin/env python3

import argparse
import logging

from systemd.journal import JournaldLogHandler
from time import sleep
from gpiozero import CPUTemperature, OutputDevice
from typing import *


# set up logging to systemd
logger = logging.getLogger(__name__)
journald_handler = JournaldLogHandler()
journald_handler.setFormatter(
    logging.Formatter("[%(levelname)s] %(message)s")
)
logger.addHandler(journald_handler)

logger.setLevel(logging.INFO)


class FanController:
    """ Class responsible for controlling a fan connected to a GPIO of the RPi """
    def __init__(
            self,
            pin_number: int,
            on_threshold: float,
            off_threshold: float,
            poll_interval: int,
            cpu: CPUTemperature
    ):
        self.on_threshold  = on_threshold
        self.off_threshold = off_threshold
        self.poll_interval = poll_interval
        self.cpu           = cpu

        self.fan = OutputDevice(pin_number)

        self.run_status = False

    def main_loop(self):
        """ Starts the controller main loop. Can be interrupted by calling FanController.terminate() """
        logger.info(f"Starting fan control main loop")
        self.run_status = True
        while self.run_status:
            print("Temp =", self.cpu.temperature)

            # Start the fan if the temperature has reached the limit and the fan
            # isn't already running
            if self.cpu.temperature > self.on_threshold and self.fan.value == 0:
                logger.info(f"Enabling fan: temperature is {self.cpu.temperature}")
                self.fan.on()

            # Stop the fan if the fan is running and the temperature has dropped
            # to the lower limit.
            if self.cpu.temperature < self.off_threshold and self.fan.value == 1:
                logger.info(f"Disabling fan: temperature is {self.cpu.temperature}")
                self.fan.off()

            # Wait a bit
            sleep(self.poll_interval)

    def terminate(self):
        """ Terminates the main loop and turns off the fan """
        logger.info(f"Stopping fan control main loop")
        self.run_status = False
        self.fan.off()
        

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pin",           type = int,   default = 17)
    parser.add_argument("--on_threshold",  type = float, default = 65)
    parser.add_argument("--off_threshold", type = float, default = 55)
    parser.add_argument("--poll_interval", type = int,   default = 5)
    args = parser.parse_args()
    
    cpu = CPUTemperature()
    fan_ctlr = FanController(
        args.pin,
        args.on_threshold,
        args.off_threshold,
        args.poll_interval,
        cpu
    )

    try:
        fan_ctlr.main_loop()
    except KeyboardInterrupt:
        fan_ctlr.terminate()

if __name__ == "__main__":
    main()

