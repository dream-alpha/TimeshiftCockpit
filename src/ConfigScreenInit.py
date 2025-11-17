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


from Components.config import config
from .Debug import logger
from .__init__ import _
from .RecordingUtils import stopTimeshift, startTimeshift
from .ChannelSelection import ChannelSelection


class ConfigScreenInit(ChannelSelection):

    def __init__(self, csel, session):
        logger.info("...")
        self.csel = csel
        ChannelSelection.__init__(self, session)
        self.csel["key_blue"].text = _("Reset")
        self.csel["actions"].actions["blue"] = self.resetElement

        self.section = 400 * "¯"
        # text, config, on save, on ok, e2 usage level, depends on rel parent, description
        self.config_list = [
            (self.section, _("GENERAL"), None, None, 0, [], ""),
            (_("Enable plugin"), config.plugins.timeshiftcockpit.enabled, self.needsRestart, None, 0, [], _("Select whether to enable or disable the plugin.")),
            (_("Permanent timeshift"), config.plugins.timeshiftcockpit.permanent, self.setTimeshift, None, 0, [], _("Select to enable permanent timeshift.")),
            (_("Fixed timeshift service #1"), config.plugins.timeshiftcockpit.fixed1, self.restartTimeshifts, self.selectChannel, 0, [-1], _("Press OK to select service for fixed timeshift #1.")),
            (_("Fixed timeshift service #2"), config.plugins.timeshiftcockpit.fixed2, self.restartTimeshifts, self.selectChannel, 0, [-2], _("Press OK to select service for fixed timeshift #2.")),
            (self.section, _("RECORDING"), None, None, 2, [], ""),
            (_("Timeshift playback on zap"), config.plugins.timeshiftcockpit.ts_playback_on_zap, None, None, 0, [], _("Play back timeshift recording instead of live TV after zap.")),
            (_("Recording directory"), config.plugins.timeshiftcockpit.videodir, None, None, 0, [], _("Select directory for timeshift recordings.")),
            (_("Cover source"), config.plugins.timeshiftcockpit.cover_source, None, None, 0, [], _("Select the cover source.")),
            (self.section, _("DEBUG"), None, None, 2, [], ""),
            (_("Log level"), config.plugins.timeshiftcockpit.debug_log_level, self.setLogLevel, None, 2, [], _("Select debug log level.")),
        ]

    def needsRestart(self, _element):
        return True

    def setLogLevel(self, _element):
        return True

    def resetElement(self):
        x = self.csel["config"].getCurrent()
        if len(x) > 1:
            x[1].value = x[1].default
            self.csel["config"].invalidate(x)

    def selectChannel(self, _element):
        self.getChannel(callback=self.channelSelected)

    def channelSelected(self, service_str):
        logger.info("service_str: %s", service_str)
        if service_str is not None:
            self.csel["config"].getCurrent()[1].value = service_str
            self.csel["config"].invalidate(self.csel["config"].getCurrent())

    def restartTimeshifts(self, element):
        logger.debug("element: %s", element.value)
        stopTimeshift()
        startTimeshift()
        return True

    def setTimeshift(self, element):
        logger.info("element: %s", element.value)
        if element.value:
            startTimeshift()
        else:
            stopTimeshift()
        return True
