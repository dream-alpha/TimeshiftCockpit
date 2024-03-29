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
from time import time
from Components.ActionMap import HelpableActionMap
from Components.config import config
from Components.ServiceEventTracker import ServiceEventTracker, InfoBarBase
from Components.Sources.COCCurrentService import COCCurrentService
from Screens.Screen import Screen
from Screens.HelpMenu import HelpableScreen
from Screens.InfoBarGenerics import InfoBarAudioSelection, InfoBarShowHide, InfoBarNotifications
from Screens.MessageBox import MessageBox
from ServiceReference import ServiceReference
from enigma import iPlayableService
from .__init__ import _
from .Debug import logger
from .CockpitSeek import CockpitSeek
from .CockpitCueSheet import CockpitCueSheet
from .RecordingUtils import stopTimeshiftRecording
from .MovieInfoEPG import MovieInfoEPG
from .SkinUtils import getSkinName
from .CockpitPVRState import CockpitPVRState
from .BoxUtils import getBoxType
from .Version import ID


class CockpitPlayerSummary(Screen):

	def __init__(self, session, parent):
		Screen.__init__(self, session, parent)
		self.skinName = ID + "CockpitPlayerSummary"


class CockpitPlayer(
	Screen, HelpableScreen, InfoBarBase, InfoBarNotifications, CockpitSeek, InfoBarShowHide, InfoBarAudioSelection, CockpitPVRState, CockpitCueSheet):

	ENABLE_RESUME_SUPPORT = False
	ALLOW_SUSPEND = False

	def __init__(self, session, service, config_plugins_plugin, recording_start_time):
		self.service = service
		self.config_plugins_plugin = config_plugins_plugin
		self.recording_start_time = recording_start_time

		Screen.__init__(self, session)
		HelpableScreen.__init__(self)
		InfoBarShowHide.__init__(self)
		InfoBarBase.__init__(self)
		InfoBarAudioSelection.__init__(self)
		InfoBarNotifications.__init__(self)
		CockpitCueSheet.__init__(self, service)

		self["Service"] = COCCurrentService(session.nav, self)

		event_start = True
		self.service_started = False

		CockpitSeek.__init__(self, session, service, event_start, recording_start_time, timeshift=True, service_center=None)
		CockpitPVRState.__init__(self)

		self._event_tracker = ServiceEventTracker(
			screen=self,
			eventmap={
				iPlayableService.evStart: self.__serviceStarted,
			}
		)

		actions = {
			"EXIT":		(self.leavePlayer,	_("Stop timeshift")),
			"STOP":		(self.leavePlayer,	_("Stop timeshift")),
			"POWER":	(self.powerDown,	_("Power off")),
			"INFO":		(self.showMovieInfo,	_("Movie info")),
			"NEXT":		(self.nextEvent,	_("Next event")),
			"PREVIOUS":	(self.previousEvent,	_("Previous event")),
			"HELP":		(self.noOp,		"")
		}

		if config_plugins_plugin.permanent.value:
			actions["UP"] = (self.up, _("Open service list"))
			actions["DOWN"] = (self.down, _("Open service list"))

		self["actions"] = HelpableActionMap(
			self,
			"TimeshiftCockpitActions",
			actions,
			-1
		)

		self.execing = None
		self.is_closing = False
		self.skinName = getSkinName("CockpitPlayer")
		self.cut_list = []

		self.onShown.append(self.__onShown)

	def noOp(self):
		return

	def powerDown(self):
		self.close("power_down")

	def up(self):
		self.close("up")

	def down(self):
		self.close("down")

	def getInfo(self):
		return None

	def getEvent(self):
		return self.event

	def newEvent(self, event):
		self["Service"].newEvent(event)

	def createSummary(self):
		return CockpitPlayerSummary

	def __onShown(self):
		logger.info("...")
		if not os.path.exists(config.usage.timeshift_path.value):
			self.session.open(MessageBox, _("Timeshift directory does not exist") + ": " + config.usage.timeshift_path.value, MessageBox.TYPE_ERROR)
			self.leavePlayer()
		if not self.service_started:
			self.session.nav.playService(self.service)

	def __serviceStarted(self):
		logger.info("...")
		if not self.service_started:
			self.service_started = True
			if self.config_plugins_plugin.permanent.value:
				self.doSkip(int(time()) - self.recording_start_time)
				self.pauseService()

	def showMovieInfo(self):
		if self.event:
			self.session.open(MovieInfoEPG, self.event, ServiceReference(self.service))

	def showPVRStatePic(self, show):
		self.show_state_pic = show

	def leavePlayer(self):
		logger.info("...")
		if not self.config_plugins_plugin.permanent.value:
			stopTimeshiftRecording()
		self.close()

	def doEofInternal(self, playing):
		logger.info("playing: %s, self.execing: %s", playing, self.execing)
		if self.execing:
			logger.debug("switching to playback, seek_state: %s", self.seekstate)
			if not getBoxType().startswith("dream"):
				self.session.nav.stopService()
			self.session.nav.playService(self.service)
			self.recoverEoFFailure()
