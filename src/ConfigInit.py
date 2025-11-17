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


from APIs.ServiceData import getServiceList
from Screens.ChannelSelection import service_types_tv
from Components.config import config
from Components.config import ConfigSelection, ConfigYesNo, ConfigSubsection, ConfigNothing, NoSave
from .MovieCoverDownloadUtils import choices_cover_source
from .Debug import logger, log_levels, initLogging
from .__init__ import _


def getChannelChoices(bouquet):
    logger.info("...")
    servicetypes = bouquet + " ORDER BY name"
    service_list = getServiceList(servicetypes)
    # logger.debug("service_list: %s", service_list)
    choices = [("", _("Inactive"))]
    if service_list:
        for service_str, service_name in service_list:
            if "::" not in service_str:
                choices.append((service_str, service_name))
    # logger.debug("choices: %s", choices)
    return choices


class ConfigInit():

    def __init__(self):
        logger.debug("...")
        config.plugins.timeshiftcockpit = ConfigSubsection()
        config.plugins.timeshiftcockpit.fake_entry = NoSave(ConfigNothing())
        config.plugins.timeshiftcockpit.cover_source = ConfigSelection(
            default="tvs_id", choices=choices_cover_source)
        config.plugins.timeshiftcockpit.debug_log_level = ConfigSelection(
            default="INFO", choices=list(log_levels.keys()))
        config.plugins.timeshiftcockpit.enabled = ConfigYesNo(default=True)
        config.plugins.timeshiftcockpit.permanent = ConfigYesNo(default=False)
        config.plugins.timeshiftcockpit.fixed1 = ConfigSelection(
            default="", choices=getChannelChoices(service_types_tv))
        logger.debug(
            "fixed1: %s", config.plugins.timeshiftcockpit.fixed1.value)
        config.plugins.timeshiftcockpit.fixed2 = ConfigSelection(
            default="", choices=getChannelChoices(service_types_tv))
        logger.debug(
            "fixed2: %s", config.plugins.timeshiftcockpit.fixed2.value)
        config.plugins.timeshiftcockpit.videodir = ConfigSelection(
            default=config.movielist.videodirs.value[0], choices=config.movielist.videodirs.value)
        config.plugins.timeshiftcockpit.ts_playback_on_zap = ConfigYesNo(
            default=False)
        initLogging()
