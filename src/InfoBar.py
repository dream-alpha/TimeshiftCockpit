#!/usr/bin/python
# coding=utf-8
#
# Copyright (C) 2018-2022 by dream-alpha
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
from __init__ import _
from Debug import logger
from Screens.InfoBar import InfoBar as InfoBarOrg
from Screens.MessageBox import MessageBox
from RecordTimer import RecordTimerEntry, parseEvent
from ServiceReference import ServiceReference
from Components.config import config
from time import time, localtime, strftime
from enigma import eServiceReference, eEPGCache
from SkinUtils import getSkinName
from RecordingUtils import isTimeshifting


class InfoBar(InfoBarOrg):

	def __init__(self, session):
		InfoBarOrg.__init__(self, session)
		InfoBarOrg.instance = self
		self.index = 0
		self.last_name = ""

	def startTimeshift(self):
		logger.info("...")
		if getSkinName("") == getSkinName("NoSupport"):
			self.session.open(MessageBox, _("Only Full HD skins are supported at this time."), MessageBox.TYPE_INFO)
			return
		if not os.path.exists(config.usage.timeshift_path.value):
			self.session.open(MessageBox, _("Timeshift directory does not exist") + ": " + config.usage.timeshift_path.value, MessageBox.TYPE_ERROR)
			return
		if isTimeshifting():
			return

		begin = int(time())
		end = begin + 3600  # dummy
		name = "Timeshift"
		description = ""
		eventid = None

		serviceref = self.session.nav.getCurrentlyPlayingServiceReference()
		service = self.session.nav.getCurrentService()
		event = eEPGCache.getInstance().lookupEventTime(serviceref, -1, 0)
		if event is None:
			info = service.info()
			event = info and info.getEvent(0)

		if event is not None:
			cur_event = parseEvent(event)
			name += cur_event[2]
			description = cur_event[3]
			eventid = cur_event[4]

		if name == self.last_name:
			self.index += 1
			name += "_%03d" % self.index
		else:
			self.index = 0
			self.last_name = name

		if isinstance(serviceref, eServiceReference):
			serviceref = ServiceReference(serviceref)

		recording = RecordTimerEntry(serviceref, begin, end, name, description, eventid, dirname=config.usage.timeshift_path.value)
		recording.dontSave = True
		recording.timeshift = True
		recording.autoincrease = True
		recording.setAutoincreaseEnd()
		self.recording.append(recording)

		simulTimerList = self.session.nav.RecordTimer.record(recording)
		if simulTimerList is not None:
			if len(simulTimerList) > 1:
				name = simulTimerList[1].name
				name_date = ' '.join((name, strftime('%c', localtime(simulTimerList[1].begin))))
				logger.info("timer conflicts with", name_date)
				recording.autoincrease = True	# start with max available length, then increment
				if recording.setAutoincreaseEnd():
					self.session.nav.RecordTimer.record(recording)
					self.session.open(MessageBox, _("Limited timeshifting due to conflicting timer %s") % name_date, MessageBox.TYPE_INFO)
				else:
					self.recording.remove(recording)
					self.session.open(MessageBox, _("Couldn't timeshift due to conflicting timer %s") % name, MessageBox.TYPE_INFO)
			else:
				self.recording.remove(recording)
				self.session.open(MessageBox, _("Couldn't timeshift due to invalid service %s") % serviceref, MessageBox.TYPE_INFO)
			recording.autoincrease = False
