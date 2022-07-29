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
from Debug import log_levels
from Components.config import config
from Components.config import ConfigSelection, ConfigYesNo, ConfigSubsection


class ConfigInit():

	def __init__(self):
		logger.debug("...")
		config.plugins.timeshiftcockpit                           = ConfigSubsection()
		config.plugins.timeshiftcockpit.debug_log_level           = ConfigSelection(default="INFO", choices=log_levels.keys())
		config.plugins.timeshiftcockpit.enabled                   = ConfigYesNo(default=True)
