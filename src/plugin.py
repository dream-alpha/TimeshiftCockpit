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
from Plugins.Plugin import PluginDescriptor
from Components.config import config
import Screens.InfoBar
from .__init__ import _
from .Debug import logger
from .Version import VERSION
from .ConfigInit import ConfigInit
from .InfoBar import InfoBar  # pylint: disable=W0611
from .SkinUtils import loadPluginSkin
from .ConfigScreen import ConfigScreen
from .FileUtils import deleteFiles


def openSettings(session, **__):
    logger.info("...")
    session.open(ConfigScreen, config.plugins.timeshiftcockpit)


def autoStart(reason, **__):
    if reason == 0:  # startup
        if config.plugins.timeshiftcockpit.enabled.value:
            logger.info("+++ Version: %s starts...", VERSION)
            Screens.InfoBar.InfoBar = InfoBar
        loadPluginSkin("skin.xml")
    elif reason == 1:  # shutdown
        logger.info("--- shutdown")
        deleteFiles(os.path.join(
            config.usage.timeshift_path.value, "*Timeshift*"))


def Plugins(**__):
    ConfigInit()
    descriptors = [
        PluginDescriptor(
            where=[
                PluginDescriptor.WHERE_AUTOSTART
            ],
            fnc=autoStart
        ),
        PluginDescriptor(
            name="TimeshiftCockpit" + " - " + _("Setup"),
            description=_("Open setup"),
            icon="TimeshiftCockpit.svg",
            where=[
                PluginDescriptor.WHERE_PLUGINMENU,
            ],
            fnc=openSettings
        )
    ]
    return descriptors
