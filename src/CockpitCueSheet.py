# coding=utf-8
# Copyright (C) 2018-2025 by dream-alpha
# License: GNU General Public License v3.0 (see LICENSE file for details)


from Screens.InfoBarGenerics import InfoBarCueSheetSupport
from .Debug import logger
from .CutList import CutList


class CockpitCueSheet(InfoBarCueSheetSupport, CutList):

    def __init__(self, service):
        self.service = service
        InfoBarCueSheetSupport.__init__(self)
        CutList.__init__(self)
        self.cut_list = []

    def getCutList(self):
        logger.info("cut_list: %s", self.cut_list)
        # return self.cut_list
        return []

    def downloadCuesheet(self):
        path = self.service.getPath() if self.service else None
        self.cut_list = self.readCutList(path)
        logger.debug("path: %s, cut_list: %s", path, self.cut_list)

    def uploadCuesheet(self):
        path = self.service.getPath() if self.service else None
        logger.debug("path: %s, cut_list: %s", path, self.cut_list)
        self.writeCutList(self.service.getPath(), self.cut_list)
