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


import os
from time import time
import NavigationInstance
from Components.config import config
from enigma import eEPGCache
from .Debug import logger
from .Playback import Playback
from .FileUtils import deleteFiles
from .TSRecordingJob import TSRecordingJob
from .TimeshiftUtils import formatTime
from .RecordingUtils import calcRecordingFilename


class Timeshift(Playback, TSRecordingJob):

    def __init__(self, session, service_ref, infobar_instance):
        logger.info("service_ref: %s", service_ref.toString())
        Playback.__init__(self)
        TSRecordingJob.__init__(self)
        self.session = session
        self.service_ref = service_ref
        self.service_str = service_ref.toString()
        self.infobar_instance = infobar_instance
        self.record_service = None
        self.timeshift_start_time = 0
        self.timeshift_file_path = ""
        self.events_info = []

    def stopTimeshift(self):
        logger.info("record_service: %s", self.record_service)
        logger.info("timeshift_file_path: %s", self.timeshift_file_path)
        if self.record_service:
            NavigationInstance.instance.stopRecordService(self.record_service)
            deleteFiles(os.path.splitext(
                self.timeshift_file_path)[0] + ".*", True)
            self.record_service = None

    def startTimeshift(self):
        logger.info("...")
        if not self.record_service:
            self.record_service = self.record(self.service_ref)
            self.timeshift_start_time = int(time())
            logger.debug("timeshift_start_time: %s",
                         formatTime(self.timeshift_start_time))
            self.events_info = self.getEventsInfo()
            logger.debug("record_service: %s", self.record_service)
            logger.debug("timeshift_file_path: %s", self.timeshift_file_path)
        return self.record_service

    def getEventsInfo(self):
        # I = Event Id, B = Event Begin Time, D = Event Duration, T = Event Title
        # S = Event Short Description, E = Event Extended Description, C = Current Time
        # R = Service Reference String, N = Service Name, n = Short Service Name
        # X = Return a minimum of one tuple per service in the result list... even when no event was found
        logger.info("...")
        if self.service_ref:
            events_info = eEPGCache.getInstance().lookupEvent(
                ["BDTSENI", (self.service_ref.toString(), -1, self.timeshift_start_time, 24 * 60)])
            if len(events_info) > len(self.events_info):
                self.events_info = events_info
                logger.debug("events_info: %s", self.events_info)
        return self.events_info

    def record(self, service_ref):
        logger.info("...")
        record_service = NavigationInstance.instance.recordService(service_ref)
        if not record_service:
            logger.debug("no record_service")
            return None

        begin = end = int(time())
        self.timeshift_file_path = calcRecordingFilename(
            begin, service_ref, "Timeshift", config.usage.timeshift_path.value) + ".ts"
        if record_service.prepare(self.timeshift_file_path, begin, end, -1, "", ""):
            logger.debug("prepare failed.")
            NavigationInstance.instance.stopRecordService(record_service)
            return None

        if record_service.start():
            logger.debug("start record failed.")
            return None
        return record_service
