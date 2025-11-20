# coding=utf-8
# Copyright (C) 2018-2025 by dream-alpha
# License: GNU General Public License v3.0 (see LICENSE file for details)


device = "/proc/stb/fp/led0_pattern"


class FrontPanelLed():

    def __init__(self):
        return

    @staticmethod
    def stopRecording():
        with open(device, "w", encoding="utf-8") as f:
            f.write("00000000")

    @staticmethod
    def recording():
        with open(device, "w", encoding="utf-8") as f:
            f.write("55555555")


frontPanelLed = FrontPanelLed()
