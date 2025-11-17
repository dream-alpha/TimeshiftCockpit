#!/usr/bin/python
# coding=utf-8
#
# Copyright (C) 2018-2025 by dream-alpha
#
# In case of reuse of this source code please do not remove this copyright.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# For more information on the GNU General Public License see:
# <http://www.gnu.org/licenses/>.


from time import time
from Components.config import config
from Tools.BoundFunction import boundFunction
import Screens.Standby
from .Debug import logger
from .CockpitPlayer import CockpitPlayer
from .BufferingProgress import BufferingProgress
from .ServiceUtils import getService


BUFFERING = 3


class Playback():

    def __init__(self):
        logger.info("...")
        self.service = None

    def startPlayer(self, dont_pause):
        logger.info("...")
        if self.service:
            self.session.openWithCallback(self.startPlayerCallback, CockpitPlayer, self.service, config.plugins.timeshiftcockpit,
                                          self.timeshift_start_time, self.infobar_instance, self.service_ref, dont_pause)
        else:
            logger.error("service: %s", self.service)

    def startPlayerCallback(self, action=""):
        logger.info("action: %s", action)
        if not config.plugins.timeshiftcockpit.permanent.value:
            self.stopTimeshift()
        if action == "up":
            self.infobar_instance.switchChannelUp()
        elif action == "down":
            self.infobar_instance.switchChannelDown()
        elif action == "power_down":
            self.session.open(Screens.Standby.TryQuitMainloop, 1)

    def startPlayback(self, first, dont_pause=False):
        logger.info("first: %s", first)
        self.service = getService(self.timeshift_file_path)
        if not config.plugins.timeshiftcockpit.permanent.value:
            wait = 3 * BUFFERING if first else BUFFERING
            abuffer = 0
        else:
            wait = 3 * BUFFERING if first else 0
            abuffer = int(time()) - self.timeshift_start_time
        delay = max(0, wait - abuffer)
        logger.debug("abuffer: %s, delay: %s", abuffer, delay)
        if delay:
            self.session.openWithCallback(boundFunction(
                self.startPlayer, dont_pause), BufferingProgress, delay)
        else:
            self.startPlayer(dont_pause)
