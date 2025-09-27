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


from pipes import quote
from enigma import eConsoleAppContainer
from .Debug import logger
from .TimeshiftUtils import ERROR_NONE, ERROR_ABORT


class Shell():

    def __init__(self):
        logger.info("...")
        self.container = eConsoleAppContainer()
        self.container_appClosed_conn = self.container.appClosed.connect(
            self.finished)
        self.__abort = False

    def execShellCallback(self, _path, _target_path, _error):
        logger.error("should be overridden in child class")

    def execShell(self, scripts, path, target_path):
        logger.info("path: %s, target_path: %s, scripts: %s",
                    path, target_path, scripts)
        self.path = path
        self.target_path = target_path
        self.__abort = False
        script = '; '.join(scripts)
        self.container.execute("sh -c " + quote(script))

    def finished(self, retval=None):
        logger.info("retval = %s, __abort: %s", retval, self.__abort)
        if not self.__abort:
            self.execShellCallback(self.path, self.target_path, ERROR_NONE)
        else:
            logger.error("container finished despite abort")

    def abortShell(self):
        logger.info("...")
        self.__abort = True
        if self.container and self.container.running():
            self.container.kill()
            self.container = None
        else:
            logger.debug("aborting before container has started execution...")
        self.execShellCallback(self.path, self.target_path, ERROR_ABORT)
