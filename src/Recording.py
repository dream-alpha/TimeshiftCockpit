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
from Debug import logger
import NavigationInstance
from timer import TimerEntry
from Components.config import config
from ServiceUtils import getService
from CockpitPlayer import CockpitPlayer
from FileUtils import deleteFiles
from BufferingProgress import BufferingProgress
from DelayTimer import DelayTimer
from Tools.BoundFunction import boundFunction
from BufferingProgress import BUFFERING


class Recording():

	def __init__(self, session):
		logger.info("...")
		self.session = session
		deleteFiles(os.path.join(config.usage.timeshift_path.value, "*Timeshift*"))
		NavigationInstance.instance.RecordTimer.on_state_change.append(self.recordingEvent)

	def doneBufferingProgress(self, timer_filename, ts_start):
		logger.info("...")
		self.session.open(CockpitPlayer, getService(timer_filename), ts_start)

	def recordingEvent(self, timer):
		TIMER_STATES = ["StateWaiting", "StatePrepared", "StateRunning", "StateEnded"]
		if timer and not timer.justplay and hasattr(timer, "timeshift"):
			logger.debug(
				"timer.Filename: %s, timer.state: %s",
				timer.Filename, (TIMER_STATES[timer.state] if timer.state in range(0, len(TIMER_STATES)) else timer.state)
			)
			if timer.state == TimerEntry.StateRunning:
				logger.debug("REC START for: %s, afterEvent: %s", timer.Filename, timer.afterEvent)
				ts_start = int(time()) - BUFFERING
				self.session.openWithCallback(boundFunction(self.doneBufferingProgress, timer.Filename, ts_start), BufferingProgress)
			elif timer.state == TimerEntry.StateEnded or timer.state == TimerEntry.StateWaiting:
				logger.debug("REC END for: %s, afterEvent: %s", timer.Filename, timer.afterEvent)
				file_name = os.path.splitext(timer.Filename)[0]
				DelayTimer(1000, deleteFiles, file_name + ".*")
