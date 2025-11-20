# coding=utf-8
# Copyright (C) 2018-2025 by dream-alpha
# License: GNU General Public License v3.0 (see LICENSE file for details)


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
        print(f"RECSTATE: timeshift_recordings: {timeshift_recordings}")
        recordings += len(timeshift_recordings)
        return recordings

    def gotRecordEvent(self, _service, _event):
        return

    def gotRecordingEvent(self, _timer=None):
        prev_records = self.records_running
        self.records_running = self.getRecordings()
        print(f"RECSTATE: records: {self.records_running}, prev_records: {prev_records}")
        if self.records_running != prev_records:
            self.changed((self.CHANGED_ALL,))
