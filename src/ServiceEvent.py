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


from time import localtime, strftime
from .Debug import logger


class ServiceEvent():

    def __init__(self, event_data):
        logger.info("event_data: %s", event_data)
        self.begin, self.duration, self.name, self.short_description, self.extended_description, _, _ = event_data

    def getBeginTime(self):
        return self.begin

    def getDuration(self):
        return self.duration

    def getEventId(self):
        return 0

    def getEventName(self):
        return self.name

    def getShortDescription(self):
        return self.short_description

    def getExtendedDescription(self, _original=False):
        return self.extended_description

    def getBeginTimeString(self):
        return strftime("%d.%m. %H:%M", localtime(self.begin))
