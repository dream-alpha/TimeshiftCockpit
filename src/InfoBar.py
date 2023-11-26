#!/usr/bin/python
# coding=utf-8
#
# Copyright (C) 2018-2024 by dream-alpha
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
from time import time, strftime, localtime
import NavigationInstance
from Screens.InfoBar import InfoBar as InfoBarOrg
from Components.config import config
from Components.ServiceEventTracker import ServiceEventTracker
from enigma import eTimer, iPlayableService, eEPGCache
from ServiceReference import ServiceReference
from .Debug import logger
from .Recording import Recording
from .RecordState import RecordState
from .FileUtils import deleteFiles
from .ServiceUtils import getService
from .DelayTimer import DelayTimer

instance = None


class InfoBar(InfoBarOrg, Recording):

	def __init__(self, session):
		InfoBarOrg.__init__(self, session)
		InfoBarOrg.instance = self
		Recording.__init__(self, session)
		global instance
		instance = self
		self.events_info = []
		self.service_ref = None
		self.prev_service_ref = None
		self.record_service = None
		self.recording_start_time = 0
		self.first = True
		self.filename = ""
		self.is_timeshifting = False
		session.screen["RecordState"] = RecordState(session)
		self._event_tracker = ServiceEventTracker(
			screen=self,
			eventmap={
				iPlayableService.evStart: self.__serviceStarted,
			}
		)
		self.wait_for_time_timer = eTimer()
		self.wait_for_time_timer_conn = self.wait_for_time_timer.timeout.connect(self.__serviceStarted)

	def __serviceStarted(self):
		logger.info("...")
		if config.plugins.timeshiftcockpit.permanent.value:
			if int(time()):
				DelayTimer(100, self.stopTimeshift)
			else:
				self.wait_for_time_timer.start(1000, True)

	def stopTimeshift(self):
		logger.info("...")
		self.service_ref = self.session.nav.getCurrentlyPlayingServiceReference()
		if self.service_ref:
			if self.prev_service_ref is None or self.prev_service_ref != self.service_ref:
				self.prev_service_ref = self.service_ref
				self.stopTimeshiftRecording()
				self.startTimeshiftRecording()

	def startTimeshift(self):
		logger.info("...")
		if not config.plugins.timeshiftcockpit.permanent.value:
			self.stopTimeshiftRecording()
			self.startTimeshiftRecording()
		self.startPlayback(getService(self.filename), self.recording_start_time, self.first)
		self.first = False

	def stopTimeshiftRecording(self):
		logger.info("record_service: %s", self.record_service)
		if self.record_service:
			logger.debug("stopping recording: %s", self.record_service)
			NavigationInstance.instance.stopRecordService(self.record_service)
			deleteFiles(os.path.join(config.usage.timeshift_path.value, "*Timeshift*"), True)
			self.record_service = None
			self.is_timeshifting = False

	def startTimeshiftRecording(self):
		logger.info("...")
		if not self.record_service:
			self.service_ref = self.session.nav.getCurrentlyPlayingServiceReference()
			logger.debug("service_ref: %s", self.service_ref)
			self.is_timeshifting = True
			self.record_service = self.record(self.service_ref)
			self.recording_start_time = int(time())
			self.events_info = self.lookupEventsInfo(self.recording_start_time)
			logger.debug("record_service: %s", self.record_service)

	def isTimeshifting(self):
		return self.is_timeshifting

	def lookupEventsInfo(self, start_time):
		# I = Event Id, B = Event Begin Time, D = Event Duration, T = Event Title
		# S = Event Short Description, E = Event Extended Description, C = Current Time
		# R = Service Reference String, N = Service Name, n = Short Service Name
		# X = Return a minimum of one tuple per service in the result list... even when no event was found
		logger.info("...")
		events_info = []
		if self.service_ref:
			events_info = eEPGCache.getInstance().lookupEvent(["BDTSENI", (self.service_ref.toString(), -1, start_time, 24 * 60)])
		logger.debug("events_info: %s", events_info)
		return events_info

	def getEventsInfo(self):
		logger.info("...")
		if not self.events_info:
			self.events_info = self.lookupEventsInfo(self.recording_start_time)
		return self.events_info

	def record(self, service_ref):

		def calcFilename(begin, service_ref):
			logger.info("...")
			dirname = config.usage.timeshift_path.value
			service_name = ServiceReference(service_ref).getServiceName()
			begin_date = strftime("%Y%m%d %H%M", localtime(begin))
			event_title = "Timeshift"

			logger.debug("begin_date: %s", begin_date)
			logger.debug("service_name: %s", service_name)
			logger.debug("event_title: %s", event_title)

			filename = begin_date
			if service_name:
				filename += " - " + service_name
			filename += " - " + event_title
			filename = os.path.join(dirname, filename)
			filename += ".ts"
			logger.debug("filename: %s", filename)
			return filename

		logger.info("...")
		record_service = NavigationInstance.instance.recordService(service_ref)
		if not record_service:
			logger.debug("no record_service")
			return None

		begin = end = int(time())
		self.filename = calcFilename(begin, service_ref)
		if record_service.prepare(self.filename, begin, end, -1, "", ""):
			logger.debug("prepare failed.")
			NavigationInstance.instance.stopRecordService(record_service)
			return None

		if record_service.start():
			logger.debug("start record failed.")
			return None
		return record_service
