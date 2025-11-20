# !/usr/bin/python
# coding=utf-8
# Copyright (C) 2018-2025 by dream-alpha
# License: GNU General Public License v3.0 (see LICENSE file for details)


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
                        (f"{strftime('%H:%M', localtime(event_data[0]))} - {event_data[2]}", list(event_data)))
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
