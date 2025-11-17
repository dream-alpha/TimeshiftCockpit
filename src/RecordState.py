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


from Components.Sources.RecordState import RecordState as RecordStateOrg
import NavigationInstance
from .RecordingUtils import getTimeshiftRecordings


class RecordState(RecordStateOrg):
    def __init__(self, session, infobar_instance):
        self.records_running = 0
        RecordStateOrg.__init__(self, session)
        NavigationInstance.instance.RecordTimer.on_state_change.append(
            self.gotRecordingEvent)
        if hasattr(infobar_instance, "on_timeshift_recording_change"):
            infobar_instance.on_timeshift_recording_change.append(
                self.gotRecordingEvent)
        self.gotRecordingEvent(None)

    def getRecordings(self):
        recordings = 0
        for timer in NavigationInstance.instance.RecordTimer.timer_list:
            if timer.isRunning() and not timer.justplay:
                recordings += 1
        timeshift_recordings = getTimeshiftRecordings()
        print("RECSTATE: timeshift_recordings: %s" % timeshift_recordings)
        recordings += len(timeshift_recordings)
        return recordings

    def gotRecordEvent(self, _service, _event):
        return

    def gotRecordingEvent(self, _timer=None):
        prev_records = self.records_running
        self.records_running = self.getRecordings()
        print(("RECSTATE: records: %s, prev_records: %s" % (self.records_running, prev_records)))
        if self.records_running != prev_records:
            self.changed((self.CHANGED_ALL,))
