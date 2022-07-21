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


from __init__ import _
from Debug import logger
from Components.ActionMap import HelpableActionMap
from Screens.InfoBarGenerics import InfoBarSeek
from enigma import eTimer
from CutListUtils import secondsToPts, ptsToSeconds
from DelayTimer import DelayTimer
from BoxUtils import getBoxType


SKIP_TIMEOUT = 5000  # milliseconds
STOP_BEFORE_EOF = 5  # seconds


class CockpitSmartSeek(InfoBarSeek):

	def __init__(self, config_event_start, config_skip_first_long, is_recording):
		logger.info("SKIP")
		InfoBarSeek.__init__(self)

		self["InfoBarSmartSeek"] = HelpableActionMap(
			self,
			"InfoBarSmartSeekActions",
			{
				"CHANNELUP":	(self.skipForward,	_("Skip forward")),
				"CHANNELDOWN":	(self.skipBackward,	_("Skip backward")),
			},
			prio=-2
		)

		self.config_event_start = config_event_start
		self.skip_first = True
		self.config_skip_first_long = config_skip_first_long
		self.is_recording = is_recording
		self.skip_forward = True
		self.skip_index = 0
		self.skip_distance_long = [300, 60, 30, 15]
		self.skip_distance_short = [60, 30, 15]
		self.skip_distance = self.skip_distance_long
		self.reset_skip_timer = eTimer()
		self.reset_skip_timer_conn = self.reset_skip_timer.timeout.connect(self.resetSkipTimer)

	def resetSkipTimer(self):
		logger.info("SKIP ================================================")
		self.skip_first = True
		self.skip_distance = self.skip_distance_long
		self.skip_index = 0
		self.skip_forward = True
		self.showPVRStatePic(True)

	def setSkipDistance(self):
		if self.skip_first and self.config_event_start:
			_before, _offset, _event_length, self.event_start_time, _recording_start_time = self.getEventInfo()
			logger.debug("position: %s, event_start_time: %s", ptsToSeconds(self.getPosition()), self.event_start_time)
			if abs(self.event_start_time - self.recording_start_time - ptsToSeconds(self.getSeekPosition())) <= 60:
				self.skip_distance = self.skip_distance_short
			else:
				self.skip_distance = self.skip_distance_long
			logger.debug("skip_distance: %s", self.skip_distance)

	def skipForward(self):
		logger.info("SKIP")
		self.reset_skip_timer.start(SKIP_TIMEOUT, True)
		self.setSkipDistance()
		if not self.skip_first and (not self.skip_forward or (self.config_skip_first_long and self.skip_distance == self.skip_distance_long and self.skip_index == 0)):
			self.skip_index = len(self.skip_distance) - 1 if self.skip_index >= len(self.skip_distance) - 1 else self.skip_index + 1
		self.skip_forward = True
		self.skip_first = False
		distance = self.skip_distance[self.skip_index]
		length, position = self.getLengthPosition()
		self.showPVRStatePic(False)
		self.doSkip(position, distance, length)

	def skipBackward(self):
		logger.info("SKIP")
		self.reset_skip_timer.start(SKIP_TIMEOUT, True)
		self.setSkipDistance()
		if not self.skip_first and self.skip_forward:
			self.skip_index = len(self.skip_distance) - 1 if self.skip_index >= len(self.skip_distance) - 1 else self.skip_index + 1
		self.skip_forward = False
		self.skip_first = False
		distance = self.skip_distance[self.skip_index]
		length, position = self.getLengthPosition()
		distance = min(distance, position)
		self.doSkip(position, -distance, length)

	def doSkip(self, position, distance, length):
		logger.info("SKIP >>>: distance: %s, position: %s, target: %s, length: %s", distance, position, position + distance, length)
		target = position + distance
		if target > length:
			target = length - STOP_BEFORE_EOF
		target = max(0, target)
		self.doSeek(secondsToPts(target))
		self.showAfterSeek()
		DelayTimer(500, self.getLengthPosition)

	def getLengthPosition(self):
		if self.is_recording:
			length = ptsToSeconds(self.getRecordingLength())
		else:
			length = ptsToSeconds(self.getLength())
		position = ptsToSeconds(self.getSeekPosition())
		logger.info("SKIP <<<: length: %s, position: %s", length, position)
		return length, position

	def recoverEoFFailure(self):
		logger.info("SKIP: skip_forward: %s, skip_index: %s", self.skip_forward, self.skip_index)
		length = ptsToSeconds(self.getRecordingLength())
		logger.debug("target: %s", length - STOP_BEFORE_EOF)
		if not getBoxType().startswith("dream"):
			self.doSeek(secondsToPts(length - STOP_BEFORE_EOF))
		else:
			self.doSeekRelative(-secondsToPts(STOP_BEFORE_EOF))
