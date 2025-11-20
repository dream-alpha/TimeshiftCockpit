# coding=utf-8
# Copyright (C) 2018-2025 by dream-alpha
# License: GNU General Public License v3.0 (see LICENSE file for details)


import os
from Plugins.Plugin import PluginDescriptor
from Components.config import config
import Screens.InfoBar
from .__init__ import _
from .Debug import logger
from .Version import VERSION
from .ConfigInit import ConfigInit
from .InfoBar import InfoBar
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
