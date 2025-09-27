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

from Components.Task import Job
from Plugins.SystemPlugins.JobCockpit.JobSupervisor import JobSupervisor
from .Debug import logger
from .TSRecordingTask import TSRecordingTask
from .Version import ID
from .__init__ import _


class TSRecordingJob():

    def __init__(self):
        self.job_manager = JobSupervisor.getInstance().getJobManager(ID)

    def addTSRecordingJob(self, event_data, service_ref):
        logger.info("Adding timeshift recording job...")
        logger.debug("event_data: %s", event_data)
        logger.debug("timeshift_file_path: %s", self.timeshift_file_path)
        logger.debug("service_ref_str: %s", service_ref.toString())
        job = Job("%s - %s" % (_("TS recording"), event_data[2]))
        job.keep = True
        TSRecordingTask(job, self.infobar_instance, service_ref,
                        self.timeshift_file_path, self.timeshift_start_time, event_data)
        self.job_manager.AddJob(job)
