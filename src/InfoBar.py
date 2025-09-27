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
from Screens.InfoBar import InfoBar as InfoBarOrg
from Screens.MessageBox import MessageBox
from Screens.Standby import inStandby
from Components.config import config
from Components.ServiceEventTracker import ServiceEventTracker
from Tools import Notifications
from enigma import eTimer, eServiceReference, iPlayableService
from .Debug import logger
from .Timeshift import Timeshift
from .RecordState import RecordState
from .DelayTimer import DelayTimer
from .Recording import Recording
from .JobUtils import getPendingJobs
from .Playback import BUFFERING
from .__init__ import _
from .Version import ID


instance = None


class InfoBar(InfoBarOrg, Recording):

    def __init__(self, session):
        InfoBarOrg.__init__(self, session)
        InfoBarOrg.instance = self
        global instance
        instance = self
        self.on_timeshift_recording_change = []
        Recording.__init__(self, session)
        config.misc.epgcache_outdated_timespan.value = 10
        config.misc.epgcache_outdated_timespan.save()
        self.service_str = ""
        self.service_ref = None
        self.first = True
        self.fixed_services = []
        self.timeshifts = {}
        session.screen["RecordState"] = RecordState(session, instance)
        self._event_tracker = ServiceEventTracker(
            screen=self,
            eventmap={
                iPlayableService.evStart: self.__serviceStarted,
            }
        )
        self.wait_for_time_timer = eTimer()
        self.wait_for_time_timer_conn = self.wait_for_time_timer.timeout.connect(
            self.__serviceStarted)
        self.max_timeshifts = 0
        self.setFixedServices()

    def setFixedServices(self):
        fixed1 = config.plugins.timeshiftcockpit.fixed1.value
        if fixed1:
            self.fixed_services.append(fixed1)
        fixed2 = config.plugins.timeshiftcockpit.fixed2.value
        if fixed2:
            self.fixed_services.append(fixed2)
        self.max_timeshifts = len(self.fixed_services) + 1
        logger.debug("max_timeshifts: %s", self.max_timeshifts)

    def __serviceStarted(self):
        logger.info("...")
        if config.plugins.timeshiftcockpit.permanent.value:
            if int(time()):
                DelayTimer(100, self.startTimeshifts)
            else:
                self.wait_for_time_timer.start(1000, True)

    def startTimeshift(self):
        # pause
        logger.info("...")
        if not config.plugins.timeshiftcockpit.permanent.value:
            self.service_ref = self.session.nav.getCurrentlyPlayingServiceReference()
            self.service_str = self.service_ref.toString()
            self.addTimeshift(self.service_str)
        if self.service_str in self.timeshifts:
            self.timeshifts[self.service_str].startPlayback(self.first)
            self.first = False
        else:
            Notifications.AddPopup(text=_("No timeshift available for playback"),
                                   type=MessageBox.TYPE_INFO, timeout=5, id="No_Timeshift", domain="Timeshift")

    def startTimeshifts(self):
        # zap
        logger.info("first: %s", self.first)
        last_service_str = self.service_str
        self.service_ref = self.session.nav.getCurrentlyPlayingServiceReference()
        if self.service_ref:
            self.service_str = self.service_ref.toString()
            # logger.debug("zapping to: %s", self.service_str)
            for fixed_service_str in self.fixed_services:
                self.addTimeshift(fixed_service_str)
            if self.service_str != last_service_str:
                # logger.debug("service changed")
                if last_service_str and last_service_str not in self.fixed_services:
                    self.removeTimeshift(last_service_str)
                self.addTimeshift(self.service_str)
                if (
                        config.plugins.timeshiftcockpit.ts_playback_on_zap.value
                        and self.service_str in self.timeshifts
                        and self.service_str in self.fixed_services
                        and int(time()) - self.timeshifts[self.service_str].timeshift_start_time > BUFFERING
                ):
                    # logger.debug("start playback")
                    self.timeshifts[self.service_str].startPlayback(
                        self.first, dont_pause=True)

    def addTimeshift(self, service_str=None):
        logger.info("service_str: %s, timeshifts: %s",
                    service_str, self.timeshifts.keys())
        if service_str is not None:
            logger.debug("max_timeshifts: %s", self.max_timeshifts)
            if service_str not in self.timeshifts and len(self.timeshifts) < self.max_timeshifts:
                self.timeshifts[service_str] = Timeshift(
                    self.session, eServiceReference(service_str), instance)
                if self.timeshifts[service_str].startTimeshift() is None:
                    self.timeshifts.pop(service_str, None)
        else:
            self.setFixedServices()
            self.service_str = ""
            self.startTimeshifts()

    def removeTimeshift(self, service_str=None):
        logger.info("service_str: %s, timeshifts: %s",
                    service_str, self.timeshifts.keys())
        if service_str is not None:
            if service_str in self.timeshifts and not self.isTimeshiftRecording(service_str):
                self.timeshifts[service_str].stopTimeshift()
                self.timeshifts.pop(service_str, None)
        else:
            for tmp_service_str in self.timeshifts.copy():
                self.removeTimeshift(tmp_service_str)
        logger.info("service_str: %s, timeshifts: %s",
                    service_str, self.timeshifts.keys())

    def startTSRecording(self, service_ref, event_data):
        logger.info("...")
        service_str = service_ref.toString()
        self.timeshifts[service_str].addTSRecordingJob(event_data, service_ref)

    def stopTSRecording(self, service_str):
        logger.info("service_str: %s, self.service_str: %s",
                    service_str, self.service_str)
        if not inStandby:
            if service_str not in self.fixed_services and self.service_str != service_str:
                self.removeTimeshift(service_str)
                self.addTimeshift(self.service_str)
        else:
            self.removeTimeshift(service_str)

    def onTSRecordingChange(self):
        for function in self.on_timeshift_recording_change:
            function()

    def getEventsInfo(self):
        logger.info("service_str: %s", self.service_str)
        return self.timeshifts[self.service_str].getEventsInfo()

    def isTimeshifting(self):
        is_timeshifting = len(self.timeshifts) > 0
        logger.info("service_str: %s, is_timeshifting: %s",
                    self.service_str, is_timeshifting)
        return is_timeshifting

    def isTimeshiftRecording(self, path_or_ref=""):
        is_timeshift_recording = False
        jobs = getPendingJobs(ID)
        for job in jobs:
            if path_or_ref:
                if path_or_ref in [job.target_path, job.service_str]:
                    is_timeshift_recording = True
                    break
            else:
                is_timeshift_recording = True
                break
        logger.debug("path_or_ref: %s, is_timeshift_recording: %s",
                     path_or_ref, is_timeshift_recording)
        return is_timeshift_recording

    def getTimeshiftRecordings(self, service_str=""):
        logger.info("...")
        recordings_list = []
        jobs = getPendingJobs(ID)
        for job in jobs:
            if service_str:
                if job.service_str == service_str:
                    recordings_list.append(job.target_path)
            else:
                recordings_list.append(job.target_path)
        return recordings_list
