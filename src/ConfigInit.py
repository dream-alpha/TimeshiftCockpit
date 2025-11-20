# coding=utf-8
# Copyright (C) 2018-2025 by dream-alpha
# License: GNU General Public License v3.0 (see LICENSE file for details)


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
