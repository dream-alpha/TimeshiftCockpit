# !/usr/bin/python
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


from time import time, strftime, localtime
from Screens.InfoBar import InfoBar
from Screens.ChoiceBox import ChoiceBox
from .__init__ import _
from .Debug import logger
from .Version import PLUGIN


class EventChoiceBox():
    def __init__(self):
        logger.info("...")

    def openEventChoiceBox(self, session, title, callback):
        logger.info("...")
        events_data = InfoBar.instance.getEventsInfo()
        if events_data:
            now = int(time())
            alist = []
            for event_data in events_data:
                logger.debug("event_data: %s", event_data)
                if event_data[0] < now:
                    alist.append(
                        ("%s - %s" % (strftime("%H:%M", localtime(event_data[0])), event_data[2]), list(event_data)))
        alist.sort(key=lambda x: x[0], reverse=True)

        session.openWithCallback(
            callback,
            ChoiceBox,
            title=PLUGIN,
            list=alist,
            keys=[],
            windowTitle=title,
            allow_cancel=True,
            titlebartext=_("Select")
        )
