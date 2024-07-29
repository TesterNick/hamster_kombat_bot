import logging
import os
import subprocess
import time


class Adb:
    """
    Class represents the adb utility.
    Handles the connection with the real device.
    """

    def __init__(self) -> None:
        self.ip = ''
        self.port = 5555

    def connect(self) -> None:
        """
        Establish Wi-Fi connection between the computer and the device.
        """
        self.run(f'connect {self.ip}:{self.port}')

    def get_connected_devices(self) -> list:
        """
        Check devices connected via a cable as well as Wi-Fi.
        :return: list of lists. Each of them consists of 2 elements:
                    device name and its status.
        """
        out = self.run('devices')
        return [line.split() for line in out[1:]]

    def reconnect(self) -> None:
        """
        Run adb reconnect command. Sometimes it is helpful,
        but usually it just breaks all connections and force device
        to reconnect.
        """
        logging.debug(f'Reconnecting')
        self.run('reconnect')
        time.sleep(1)

    @staticmethod
    def run(command: str) -> list:
        """
        Wrapper for subprocess.run. It gets a string and passes it to adb.
        The output is captured and all non-empty lines are returned as a list.

        :param command: adb command to run
        :return: command output
        """
        command = ('adb', *command.split())
        logging.debug(f'Running command: {command}')
        p = subprocess.run(command, capture_output=True, check=True)
        output = p.stdout.decode().split(os.linesep)
        logging.debug(f'{output=}')
        return [line.strip() for line in output if line.strip()]
