# coding=utf-8
# Copyright (C) 2018-2025 by dream-alpha
# License: GNU General Public License v3.0 (see LICENSE file for details)


import os
from Components.config import config
from .FileUtils import readFile


def dimmOSD(hide):
    dimm = config.av.osd_alpha.value if hide else 0
    if os.path.exists("/proc/stb/video/alpha"):
        device = "/proc/stb/video/alpha"
    else:  # dream one, dream two
        device = "/sys/devices/platform/meson-fb/graphics/fb0/osd_plane_alpha"
    with open(device, "w", encoding="utf-8") as f:
        f.write(f"{dimm}")


def getBoxType():
    box_type = "dm9XX"
    if os.path.exists("/proc/stb/info/model"):
        box_type = readFile("/proc/stb/info/model")
        box_type = box_type.replace("\n", "")
        if box_type == "one":
            box_type = "dreamone"
        if box_type == "two":
            box_type = "dreamtwo"
        if box_type == "seven":
            box_type = "dreamseven"
    return box_type
