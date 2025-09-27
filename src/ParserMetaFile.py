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
from .FileUtils import readFile, writeFile
from .CutListUtils import ptsToSeconds, secondsToPts


class ParserMetaFile():

    meta_keys = [
        "service_reference", "name", "description", "rec_time", "tags", "length", "size", "service_data"
    ]

    xmeta_keys = [
        "timer_start_time", "timer_stop_time", "recording_start_time", "recording_stop_time", "recording_margin_before",
        "recording_margin_after"
    ]

    def __init__(self, path):
        self.path = path
        self.meta_path = path + ".meta"
        self.xmeta_path = path + ".xmeta"
        self.meta = {}
        self.xmeta = {}

        self.meta_list = self.readMeta(self.meta_path)
        if self.meta_list:
            self.meta = self.list2dict(self.meta_list, self.meta_keys)
            logger.debug("self.meta: %s", self.meta)
            if self.meta and self.meta["length"]:
                self.meta["length"] = ptsToSeconds(self.meta["length"])
            self.xmeta_list = self.readMeta(self.xmeta_path)
            self.xmeta = self.list2dict(self.xmeta_list, self.xmeta_keys)
            if self.meta and not self.xmeta:
                self.xmeta["recording_start_time"] = self.meta["rec_time"]
                self.xmeta["recording_stop_time"] = 0
                self.xmeta["recording_margin_before"] = config.recording.margin_before.value * 60
                self.xmeta["recording_margin_after"] = config.recording.margin_after.value * 60

    def list2dict(self, alist, keys):
        adict = {}
        for i, key in enumerate(keys):
            if i < len(alist):
                try:
                    adict[key] = int(alist[i])
                except ValueError:
                    adict[key] = alist[i]
        return adict

    def dict2list(self, adict, keys):
        logger.debug("adict: %s", adict)
        alist = []
        for key in keys:
            if key in adict:
                alist.append(adict[key])
            else:
                alist.append("")
        return alist

    def readMeta(self, path):
        meta_list = readFile(path).splitlines()
        meta_list = [list_item.strip() for list_item in meta_list]
        return meta_list

    def getMeta(self):
        self.meta.update(self.xmeta)
        logger.debug("meta: %s", self.meta)
        return self.meta

    def updateMeta(self, meta):
        if "length" in meta:
            meta["length"] = secondsToPts(meta["length"])
        self.meta.update(meta)
        logger.debug("self.meta: %s", self.meta)
        self.saveMeta()

    def saveMeta(self):
        alist = self.dict2list(self.meta, self.meta_keys)
        data = "\n".join([str(line) for line in alist])
        logger.debug("path: %s, data: %s", self.meta_path, data)
        writeFile(self.meta_path, data)

    def updateXMeta(self, xmeta):
        logger.debug("xmeta: %s", xmeta)
        self.xmeta.update(xmeta)
        logger.debug("self.xmeta: %s", self.xmeta)
        self.saveXMeta()

    def saveXMeta(self):
        alist = self.dict2list(self.xmeta, self.xmeta_keys)
        data = "\n".join([str(line) for line in alist])
        writeFile(self.xmeta_path, data)
