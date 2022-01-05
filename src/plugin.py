#!/usr/bin/python
# coding=utf-8
#
# Copyright (C) 2018-2022 by dream-alpha
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


from Debug import logger
from Version import VERSION
from Plugins.Plugin import PluginDescriptor
from ConfigInit import ConfigInit
from InfoBar import InfoBar  # pylint: disable=W0611
from Components.config import config
from SkinUtils import initPluginSkinPath, loadPluginSkin
from Recording import Recording
import Screens.InfoBar


def enableTimeshiftCockpit():
	enabled = config.plugins.timeshiftcockpit.enabled.value
	logger.debug("enabled: %s", enabled)
	if enabled:
		Screens.InfoBar.InfoBar = InfoBar


def autostart(reason, **kwargs):
	if reason == 0:  # startup
		if "session" in kwargs:
			logger.info("+++ Version: %s starts...", VERSION)
			logger.info("reason: %s", reason)
			session = kwargs["session"]
			enableTimeshiftCockpit()
			Recording(session)
			initPluginSkinPath()
			loadPluginSkin("skin.xml")
	elif reason == 1:  # shutdown
		logger.info("--- shutdown")
	else:
		logger.info("reason not handled: %s", reason)


def Plugins(**__):
	logger.debug("...")
	ConfigInit()

	return [
		PluginDescriptor(
			where=[
				PluginDescriptor.WHERE_SESSIONSTART,
				PluginDescriptor.WHERE_AUTOSTART
			],
			fnc=autostart
		),
	]
