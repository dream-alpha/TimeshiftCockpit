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
from time import time
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
from Screens.InfoBarGenerics import InfoBarAudioSelection, InfoBarPVRState, InfoBarShowHide, InfoBarNotifications
from CockpitSmartSeek import CockpitSmartSeek
from CockpitCueSheet import CockpitCueSheet
from Components.Sources.COCCurrentService import COCCurrentService
from RecordingUtils import stopRecording
from MovieInfoEPG import MovieInfoEPG
from Components.ServiceEventTracker import ServiceEventTracker, InfoBarBase
from enigma import eEPGCache, iPlayableService
from CutListUtils import ptsToSeconds, secondsToPts
from SkinUtils import getSkinName
from CockpitPVRState import CockpitPVRState


class CockpitPlayerSummary(Screen):

	def __init__(self, session, parent):
		Screen.__init__(self, session, parent)
		self.skinName = getSkinName("CockpitPlayerSummary")
		self["Service"] = COCCurrentService(session.nav, parent)


class CockpitPlayer(
	Screen, HelpableScreen, InfoBarBase, InfoBarNotifications, CockpitSmartSeek, InfoBarShowHide, InfoBarAudioSelection, InfoBarPVRState, CockpitPVRState, CockpitCueSheet):

	ENABLE_RESUME_SUPPORT = False
	ALLOW_SUSPEND = False

	def __init__(self, session, service, ts_start):

		self.service = service
		self.ts_start = ts_start

		Screen.__init__(self, session)
		HelpableScreen.__init__(self)
		InfoBarShowHide.__init__(self)
		InfoBarBase.__init__(self)
		InfoBarAudioSelection.__init__(self)
		CockpitSmartSeek.__init__(self, False, 0, False)
		InfoBarPVRState.__init__(self)
		InfoBarNotifications.__init__(self)
		CockpitCueSheet.__init__(self, service)
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
		self.name = ""
		self.begin = 0
		self.duration = 0
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
		logger.info("...")
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
			logger.info(" path: %s", path)
			if os.path.exists(path):
				self.session.nav.playService(self.service)
				self.doSeek(secondsToPts(0.1))
				self.playpauseService()
			else:
				self.session.open(
					MessageBox,
					_("Movie file does not exist") + "\n" + self.service.getPath(),
					MessageBox.TYPE_ERROR,
					10
				)

	def getEventInfo(self):
		logger.info("...")
		ts_pos = self.ts_start + ptsToSeconds(self.getSeekPosition())
		event = eEPGCache.getInstance().lookupEventTime(self.service_ref, -1, 0)
		if event:
			event_data = (event.getBeginTime(), event.getDuration(), event.getEventName())
			if event_data not in self.events_data:
				self.events_data.append(event_data)
				self.events.append(event)
		logger.info("ts_pos: %s, events: %s", ts_pos, self.events_data)
		self.event = None
		self.name = ""
		self.begin = 0
		self.duration = 0
		for i, event_data in enumerate(self.events_data):
			begin, duration, name = event_data
			event = self.events[i]
			if ts_pos > begin:
				self.name = name
				self.begin = begin
				self.duration = duration
				self.event = event
		logger.debug("begin: %s, duration: %s, name: %s", datetime.fromtimestamp(self.begin), self.duration, self.name)
		self["service_name"].setText(self.name)
		self["lcd_service_name"].setText(self.name)

	def getLength(self):
		length = 0
		if self.service_started:
			length = secondsToPts(self.duration)
		return length

	def getRecordingPosition(self):
		position = 0
		if self.service_started:
			position = secondsToPts(time() - self.begin)
		return position

	def getBeforePosition(self):
		position = 0
		if self.service_started:
			if self.ts_start > self.begin:
				position = secondsToPts(self.ts_start - self.begin)
		return position

	def getSeekPosition(self):
		position = 0
		seek = self.getSeek()
		if seek and self.service_started:
			pos = seek.getPlayPosition()
			if not pos[0]:
				position = pos[1]
#		logger.debug("position: %s", ptsToSeconds(position))
		return position

	def getPosition(self):
		position = 0
		if self.service_started:
			self.getEventInfo()
			if self.begin:
				position = secondsToPts(self.ts_start + ptsToSeconds(self.getSeekPosition()) - self.begin)
#		logger.debug("position: %s", ptsToSeconds(position))
		return position

	def leavePlayer(self):
		logger.info("...")
		stopRecording(self.service.getPath())
		self.close()

	def doEofInternal(self, playing):
		logger.info("playing: %s, self.execing: %s", playing, self.execing)
		if self.execing:
			logger.debug("switching to playback")
			self.doSeekRelative(secondsToPts(-0.1))
