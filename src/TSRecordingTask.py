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


import os
from Components.config import config
from Components.Task import Task, Job
try:
    from Plugins.SystemPlugins.CacheCockpit.FileManager import FileManager
except Exception:
    FileManager = None
from .Debug import logger
from .TSRecordingTaskExecution import TSRecordingTaskExecution
from .RecordingUtils import calcRecordingFilename
from .TimeshiftUtils import ERROR_NONE, ERROR
from .__init__ import _
from .FileUtils import deleteFiles
from .DelayTimer import DelayTimer


class TSRecordingTask(Task, TSRecordingTaskExecution):

    def __init__(self, job, infobar_instance, service_ref, timeshift_file_path, timeshift_start_time, event_data):
        logger.info("timeshift_file_path = %s", timeshift_file_path)
        Task.__init__(self, job, _("Timeshift recording"))
        self.service_ref = service_ref
        self.service_str = service_ref.toString()
        self.target_path = calcRecordingFilename(
            event_data[0], self.service_ref, event_data[2], config.plugins.timeshiftcockpit.videodir.value) + ".ts"
        job.target_path = self.target_path
        job.service_str = self.service_str
        self.job = job
        self.callback = None
        self.infobar_instance = infobar_instance
        self.service_ref = service_ref
        self.service_str = service_ref.toString()
        self.event_data = event_data
        self.event_start_time = event_data[0]
        self.event_duration = event_data[1]
        self.event_title = event_data[2]
        self.event_description = event_data[3]
        self.event_extended_description = event_data[4]
        self.event_service_name = event_data[5]
        self.event_id = event_data[6]
        self.timeshift_file_path = timeshift_file_path
        self.path = timeshift_file_path
        self.timeshift_start_time = timeshift_start_time
        self.error = ERROR_NONE
        TSRecordingTaskExecution.__init__(self)

    def abort(self, *args):
        logger.info("args: %s", args)
        force = args[0] if args else True
        logger.debug("timeshift_file_path: %s, status: %s, force: %s",
                     self.timeshift_file_path, Job.IN_PROGRESS, force)
        if self.job.status == Job.IN_PROGRESS:
            if force:
                self.abortTSRecording()
            else:
                self.stopTSRecording()

    def run(self, callback):
        logger.info("self.timeshift_file_path: %s, self.target_path: %s, callback: %s",
                    self.timeshift_file_path, self.target_path, callback)
        if os.path.exists(self.target_path):
            deleteFiles(os.path.splitext(self.target_path)[0] + ".*")

        self.callback = callback
        if os.path.exists(self.timeshift_file_path):
            self.execTSRecording()
            self.infobar_instance.onTSRecordingChange()
        else:
            logger.error("timeshift file %s does not exist",
                         self.timeshift_file_path)
            self.execTSRecordingCallback(ERROR)

    def execTSRecordingCallback(self, error):
        logger.info("timeshift_file_path: %s, target_path: %s, error: %s",
                    self.timeshift_file_path, self.target_path, error)
        self.error = error
        self.finish()

    def afterRun(self):
        logger.info("service_str: %s", self.service_str)
        DelayTimer(50, self.completeTask, self.error,
                   self.service_str, self.target_path)

    def completeTask(self, error, service_str, target_path):
        logger.info("error: %s, service_str: %s, target_path: %s",
                    error, service_str, target_path)
        if error == ERROR_NONE:
            if FileManager:
                FileManager.getInstance("MVC").loadDatabaseFile(target_path)
            self.infobar_instance.stopTSRecording(service_str)
        self.infobar_instance.onTSRecordingChange()
