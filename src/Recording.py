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


from time import time
from enigma import iRecordableService
from Screens.MessageBox import MessageBox
from Tools import Notifications
from Components.config import config
import NavigationInstance
from timer import TimerEntry
import Screens.Standby
from .__init__ import _
from .Debug import logger
from .CockpitPlayer import CockpitPlayer
from .BufferingProgress import BufferingProgress
from .BoxUtils import startLedBlinking, stopLedBlinking
from .RecordingUtils import isRecording
from .DelayTimer import DelayTimer


BUFFERING = 3


class Recording():

	def __init__(self, session):
		logger.info("...")
		self.session = session
		self.recording_start_time = 0
		self.service = None
		self.timers = 0
		self.recordings = 0
		NavigationInstance.instance.RecordTimer.on_state_change.append(self.gotRecordingEvent)
		NavigationInstance.instance.record_event.append(self.gotRecordEvent)

	def gotRecordEvent(self, _recservice, event):
		if event == iRecordableService.evEnd:
			logger.debug("REC END")
			if self.recordings:
				self.recordings = max(0, self.recordings - 1)
			logger.debug("recordings: %s, timers: %s", self.recordings, self.timers)
		elif event == iRecordableService.evStart:
			logger.debug("REC START")
			self.recordings += 1
			logger.debug("recordings: %s, timers: %s", self.recordings, self.timers)
			if self.timers < 1 and not isRecording():
				DelayTimer(100, stopLedBlinking)
		elif event == iRecordableService.evRecordWriteError:
			Notifications.AddPopup(text=_("Write error while recording. Disk full?"), type=MessageBox.TYPE_ERROR, timeout=0, id="DiskFullMessage", domain="Timeshift")

	def gotRecordingEvent(self, timer):
		TIMER_STATES = ["StateWaiting", "StatePrepared", "StateRunning", "StateEnded"]
		if timer.isRunning and not timer.justplay:
			logger.debug(
				"timer.Filename: %s, timer.state: %s",
				timer.Filename, (TIMER_STATES[timer.state] if timer.state in range(0, len(TIMER_STATES)) else timer.state)
			)
			if timer.state in [TimerEntry.StatePrepared, TimerEntry.StateRunning]:
				logger.debug("TIMER START for: %s, afterEvent: %s", timer.Filename, timer.afterEvent)
				self.timers += 1
				startLedBlinking()
			elif timer.state in [TimerEntry.StateEnded, TimerEntry.StateWaiting]:
				logger.debug("TIMER END for: %s, afterEvent: %s", timer.Filename, timer.afterEvent)
				self.timers = max(0, self.timers - 2)
				if self.timers < 1:
					stopLedBlinking()

	def switchChannelUp(self):
		logger.error("should be overridden in child class.")

	def switchChannelDown(self):
		logger.error("should be overridden in child class.")

	def startPlayer(self):
		logger.info("...")
		if self.service:
			self.session.openWithCallback(self.startPlayerCallback, CockpitPlayer, self.service, config.plugins.timeshiftcockpit, self.recording_start_time)
		else:
			logger.error("service: %s", self.service)

	def startPlayerCallback(self, action=""):
		logger.info("action: %s", action)
		if action == "up":
			self.switchChannelUp()
		elif action == "down":
			self.switchChannelDown()
		elif action == "power_down":
			self.session.open(Screens.Standby.TryQuitMainloop, 1)

	def startPlayback(self, service, recording_start_time, first):
		logger.info("first: %s", first)
		self.service = service
		self.recording_start_time = recording_start_time
		if not config.plugins.timeshiftcockpit.permanent.value:
			wait = 3 * BUFFERING if first else BUFFERING
			buffer = 0
		else:
			wait = 3 * BUFFERING if first else 0
			buffer = int(time()) - self.recording_start_time
		delay = max(0, wait - buffer)
		logger.debug("buffer: %s, delay: %s", buffer, delay)
		if delay:
			self.session.openWithCallback(self.startPlayer, BufferingProgress, delay)
		else:
			self.startPlayer()
