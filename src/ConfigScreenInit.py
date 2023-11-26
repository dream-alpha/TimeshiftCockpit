#!/usr/bin/python
# coding=utf-8
#
# Copyright (C) 2018-2024 by dream-alpha
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
from .RecordingUtils import stopTimeshiftRecording, startTimeshiftRecording


class ConfigScreenInit():

	def __init__(self, _session):
		logger.info("...")

		self.section = 400 * "¯"
		#        config list entry
		#                                                           , config element
		#                                                           ,                                                               , function called on save
		#                                                           ,                                                               ,                       , function called if user has pressed OK
		#                                                           ,                                                               ,                       ,                       , usage setup level from E2
		#                                                           ,                                                               ,                       ,                       ,   0: simple+
		#                                                           ,                                                               ,                       ,                       ,   1: intermediate+
		#                                                           ,                                                               ,                       ,                       ,   2: expert+
		#                                                           ,                                                               ,                       ,                       ,       , depends on relative parent entries
		#                                                           ,                                                               ,                       ,                       ,       ,   parent config value < 0 = true
		#                                                           ,                                                               ,                       ,                       ,       ,   parent config value > 0 = false
		#                                                           ,                                                               ,                       ,                       ,       ,             , context sensitive help text
		#                                                           ,                                                               ,                       ,                       ,       ,             ,
		#        0                                                  , 1                                                             , 2                     , 3                     , 4     , 5           , 6
		self.config_list = [
			(self.section                                       , _("GENERAL")                                                  , None                  , None                  , 0     , []          , ""),
			(_("Enable plugin")                                 , config.plugins.timeshiftcockpit.enabled                       , self.needsRestart     , None                  , 0     , []          , _("Select whether to enable or disable the plugin.")),
			(_("Permanent timeshift")                           , config.plugins.timeshiftcockpit.permanent                     , self.setTimeshift     , None                  , 0     , []          , _("Select to enable permanent timeshift.")),
			(self.section                                       , _("DEBUG")                                                    , None                  , None                  , 2     , []          , ""),
			(_("Log level")                                     , config.plugins.timeshiftcockpit.debug_log_level               , self.setLogLevel      , None                  , 2     , []          , _("Select debug log level.")),
		]

	def needsRestart(self, _element):
		return True

	def setLogLevel(self, _element):
		return True

	def setTimeshift(self, element):
		logger.info("element: %s", element.value)
		if element.value:
			startTimeshiftRecording()
		else:
			stopTimeshiftRecording()
		return True
