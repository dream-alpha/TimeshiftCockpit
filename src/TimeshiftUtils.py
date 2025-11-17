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
from time import strftime, localtime
import eitsave
from Components.config import config
from .Debug import logger
from .ParserMetaFile import ParserMetaFile
from .FileUtils import writeFile
from .PluginUtils import getPlugin, WHERE_JOBCOCKPIT
from .BoxUtils import getBoxType


ERROR_NONE = 0
ERROR_NO_DISKSPACE = 1
ERROR_ABORT = 2
ERROR = 100


def formatTime(seconds):
    return strftime("%Y-%m-%d %H:%M:%S", localtime(seconds))


def calcRecordingTimes(timeshift_start_time, event_start_time, event_duration):
    logger.info("...")
    logger.debug("*in* timeshift_start_time: %s",
                 formatTime(timeshift_start_time))
    logger.debug("*in* event_start_time: %s", formatTime(event_start_time))
    logger.debug("*in* event_duration: %s", event_duration)
    copy_begin_time = max(timeshift_start_time, event_start_time
                          - config.recording.margin_before.value * 60)
    copy_end_time = event_start_time + event_duration + \
        config.recording.margin_after.value * 60
    logger.debug("*out* copy_begin_time: %s", formatTime(copy_begin_time))
    logger.debug("*out* copy_end_time: %s", formatTime(copy_end_time))
    return copy_begin_time, copy_end_time


def createEitFile(service_str, target_path, eventid):
    if getBoxType().startswith("dream"):
        return
    eitsave.SaveEIT(service_str, os.path.splitext(
        target_path)[0] + ".eit", eventid, -1, -1)


def createMetaFile(service_str, target_path, event_start_time, event_title, event_description, event_length):
    logger.info("target_path: %s, event_start_time: %s, event_title: %s, event_description: %s, event_length: %s",
                target_path, event_start_time, event_title, event_description, event_length)
    ParserMetaFile(target_path).updateMeta(
        {
            "name": event_title,
            "description": event_description,
            "rec_time": event_start_time,
            "service_reference": service_str,
            "length": event_length,
            "size": os.path.getsize(target_path)
        }
    )


def createXMetaFile(target_path, copy_begin_time, copy_end_time, event_start_time, event_duration):
    ParserMetaFile(target_path).updateXMeta(
        {
            "recording_start_time": copy_begin_time,
            "recording_stop_time": copy_end_time,
            "timer_start_time": event_start_time,
            "timer_stop_time": event_start_time + event_duration,
            "recording_margin_before": config.recording.margin_before.value * 60,
            "recording_margin_after": config.recording.margin_after.value * 60,
        }
    )


def createTXTFile(target_path, extended_event_description):
    logger.info("...")
    file_name = os.path.splitext(target_path)[0]
    writeFile(file_name + ".txt", extended_event_description)


def manageTimeshiftRecordings(session, plugin_id):
    plugin = getPlugin(WHERE_JOBCOCKPIT)
    if plugin:
        logger.debug("plugin.name: %s", plugin.name)
        plugin(session, plugin_id)
