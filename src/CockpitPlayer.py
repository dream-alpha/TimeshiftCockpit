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
from datetime import datetime
from __init__ import _
from Debug import logger
from Components.Label import Label
from Components.Sources.StaticText import StaticText
from Components.ActionMap import HelpableActionMap
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.HelpMenu import HelpableScreen
from ServiceReference import ServiceReference
from Screens.InfoBarGenerics import InfoBarAudioSelection, InfoBarShowHide, InfoBarNotifications
from CockpitSeek import CockpitSeek
from CockpitCueSheet import CockpitCueSheet
from Components.Sources.COCCurrentService import COCCurrentService
from RecordingUtils import stopRecording
from MovieInfoEPG import MovieInfoEPG
from Components.ServiceEventTracker import ServiceEventTracker, InfoBarBase
from enigma import eEPGCache, iPlayableService
from CutListUtils import ptsToSeconds
from SkinUtils import getSkinName
from CockpitPVRState import CockpitPVRState
from BoxUtils import getBoxType


STOP_BEFORE_EOF = 5  # seconds


class CockpitPlayerSummary(Screen):

	def __init__(self, session, parent):
		Screen.__init__(self, session, parent)
		self.skinName = getSkinName("CockpitPlayerSummary")
		self["Service"] = COCCurrentService(session.nav, parent)


class CockpitPlayer(
	Screen, HelpableScreen, InfoBarBase, InfoBarNotifications, CockpitSeek, InfoBarShowHide, InfoBarAudioSelection, CockpitPVRState, CockpitCueSheet):

	ENABLE_RESUME_SUPPORT = False
	ALLOW_SUSPEND = False

	def __init__(self, session, service, recording_start_time):
		self.service = service
		self.recording_start_time = recording_start_time

		Screen.__init__(self, session)
		HelpableScreen.__init__(self)
		InfoBarShowHide.__init__(self)
		InfoBarBase.__init__(self)
		InfoBarAudioSelection.__init__(self)
		InfoBarNotifications.__init__(self)
		CockpitCueSheet.__init__(self, service)
		CockpitSeek.__init__(self, service, True)
		CockpitPVRState.__init__(self)

		self["Service"] = COCCurrentService(session.nav, self)

		self._event_tracker = ServiceEventTracker(
			screen=self,
			eventmap={
				iPlayableService.evStart: self.__serviceStarted,
			}
		)

		self["actions"] = HelpableActionMap(
			self,
			"TimeshiftCockpitActions",
			{
				"STOP":		(self.leavePlayer,	_("Stop Timeshift")),
				"POWER":	(self.leavePlayer,	_("Stop Timeshift")),
				"INFO":		(self.showMovieInfo,	_("Movie Info")),
				"NEXT":		(self.nextEvent,	_("Next Event")),
				"PREVIOUS":	(self.previousEvent,	_("Previous Event")),
				"HELP":		(self.noOp,		""),
			},
			-1
		)

		self.execing = None
		self.is_closing = False
		self.skinName = getSkinName("CockpitPlayer")
		self.cut_list = []
		self.events = []
		self.events_data = []
		self.event = None
		self.event_index = None
		self.event_name = ""
		self.event_start_time = 0
		self.event_length = 0
		self["service_name"] = Label()
		self["lcd_service_name"] = StaticText()
		self.service_ref = None
		self.service_started = False
		self.onShown.append(self.__onShow)

	def noOp(self):
		return

	def createSummary(self):
		return CockpitPlayerSummary

	def __serviceStarted(self):
		logger.info("SKIP")
		if not self.is_closing:
			self.service_started = True

	def showMovieInfo(self):
		if self.event:
			self.session.open(MovieInfoEPG, self.event, ServiceReference(self.service))

	def __onShow(self):
		logger.info("...")
		if not self.service_ref:
			self.service_ref = self.session.nav.getCurrentlyPlayingServiceReference()
			path = self.service and self.service.getPath()
			logger.info("path: %s", path)
			if os.path.exists(path):
				self.session.nav.playService(self.service)
				self.doSeek(0)
				self.playpauseService()
			else:
				self.session.open(
					MessageBox,
					_("Movie file does not exist") + "\n" + path,
					MessageBox.TYPE_ERROR,
					10
				)

	def previousEvent(self):
		logger.info("SKIP2")
		target = 0
		self.getEventInfo()
		if self.event_index:
			event_data = self.events_data[self.event_index - 1]
			event_start_time, _event_length, _event_name = event_data
			target = event_start_time - self.recording_start_time
			logger.debug("SKIP2: target: %s", target)
		self.doSkip(target, 0, ptsToSeconds(self.getRecordingLength()))

	def nextEvent(self):
		logger.info("SKIP2")
		self.getEventInfo()
		target = ptsToSeconds(self.getRecordingLength()) - STOP_BEFORE_EOF
		logger.debug("SKIP2: event_index: %s, len(events_data): %s", self.event_index, len(self.events_data))
		if self.event_index is not None and self.event_index < len(self.events_data) - 1:
			event_data = self.events_data[self.event_index + 1]
			event_start_time, _event_length, _event_name = event_data
			target = event_start_time - self.recording_start_time
			logger.debug("SKIP2: target: %s", target)
		self.doSkip(target, 0, ptsToSeconds(self.getRecordingLength()))

	def getEventInfo(self):
		logger.info("...")
		self.event = None
		self.event_index = None
		self.event_name = ""
		self.event_start_time = 0
		self.event_length = 0
		if self.service_started:
			recording_position = self.recording_start_time + ptsToSeconds(self.getSeekPosition())
			event = eEPGCache.getInstance().lookupEventTime(self.service_ref, -1, 0)
			if event:
				event_data = (event.getBeginTime(), event.getDuration(), event.getEventName())
				if event_data not in self.events_data:
					self.events_data.append(event_data)
					self.events.append(event)
			logger.info("recording_position: %s, events: %s", recording_position, self.events_data)
			for i, event_data in enumerate(self.events_data):
				event_start_time, event_length, event_name = event_data
				event = self.events[i]
				if recording_position >= event_start_time:
					self.event_name = event_name
					self.event_start_time = event_start_time
					self.event_length = event_length
					self.event = event
					self.event_index = i
			before = self.recording_start_time - self.events_data[0][0]
			offset = 0
			if self.event_index > 0:
				offset = self.events_data[self.event_index][0] - self.events_data[0][0] - before
				before = 0
			logger.debug("before: %s, offset: %s, event_length: %s, event_start_time: %s, recording_start_time: %s, event_name: %s", before, offset, self.event_length, datetime.fromtimestamp(self.event_start_time), datetime.fromtimestamp(self.recording_start_time), self.event_name)
			self["service_name"].setText(self.event_name)
			self["lcd_service_name"].setText(self.event_name)
		return before, offset, self.event_length, self.event_start_time, self.event_start_time

	def showPVRStatePic(self, show):
		self.show_state_pic = show

	def leavePlayer(self):
		logger.info("...")
		stopRecording(self.service.getPath())
		self.close()

	def doEofInternal(self, playing):
		logger.info("SKIP: playing: %s, self.execing: %s", playing, self.execing)
		if self.execing:
			logger.debug("switching to playback, seek_state: %s", self.seekstate)
			if not getBoxType().startswith("dream"):
				self.session.nav.stopService()
			self.session.nav.playService(self.service)
			self.recoverEoFFailure()
