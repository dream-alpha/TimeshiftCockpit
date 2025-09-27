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


from enigma import iRecordableService
from Screens.MessageBox import MessageBox
from Tools import Notifications
import NavigationInstance
from timer import TimerEntry
from .__init__ import _
from .Debug import logger
try:
    from Components.FrontPanelLed import frontPanelLed
except Exception:
    from .FrontPanelLed import frontPanelLed
from .DelayTimer import DelayTimer


BLINKING_DELAY = 100


class Recording():

    def __init__(self, session):
        logger.info("...")
        self.session = session
        NavigationInstance.instance.RecordTimer.on_state_change.append(
            self.gotRecordingEvent)
        NavigationInstance.instance.record_event.append(self.gotRecordEvent)
        self.on_timeshift_recording_change.append(self.setLedBlinking)

    def setLedBlinking(self):
        recordings = len(self.session.nav.getRecordings())
        timeshifts = len(self.timeshifts)
        timeshift_recordings = len(self.getTimeshiftRecordings())
        logger.debug("recordings: %s, timeshifts: %s, timeshift_recordings: %s",
                     recordings, timeshifts, timeshift_recordings)
        if recordings + timeshift_recordings <= timeshifts:
            frontPanelLed.stopRecording()
        else:
            frontPanelLed.recording()

    def gotRecordEvent(self, _recservice, event):
        if event in [iRecordableService.evStart]:
            logger.debug("RECORD START")
            DelayTimer(BLINKING_DELAY, self.setLedBlinking)
        elif event in [iRecordableService.evEnd]:
            logger.debug("RECORD END")
            DelayTimer(BLINKING_DELAY, self.setLedBlinking)
        elif event == iRecordableService.evRecordWriteError:
            self.removeTimeshift()
            Notifications.AddPopup(text=_("Write error while recording. Disk full?"),
                                   type=MessageBox.TYPE_ERROR, timeout=0, id="DiskFullMessage", domain="Timeshift")

    def gotRecordingEvent(self, timer):
        TIMER_STATES = ["StateWaiting", "StatePrepared",
                        "StateRunning", "StateEnded"]
        if timer.isRunning and not timer.justplay:
            logger.debug(
                "timer.Filename: %s, timer.state: %s",
                timer.Filename, (TIMER_STATES[timer.state] if timer.state in range(
                    0, len(TIMER_STATES)) else timer.state)
            )
            if timer.state in [TimerEntry.StateRunning]:
                logger.debug("TIMER START for: %s", timer.Filename)
                DelayTimer(BLINKING_DELAY, self.setLedBlinking)
            elif timer.state in [TimerEntry.StateEnded]:
                logger.debug("TIMER END for: %s", timer.Filename)
                DelayTimer(BLINKING_DELAY, self.setLedBlinking)
