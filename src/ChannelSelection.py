# !/usr/bin/python
# coding=utf-8
# Copyright (C) 2018-2025 by dream-alpha
# License: GNU General Public License v3.0 (see LICENSE file for details)


from APIs.ServiceData import getTVBouquets, getServiceList
from Screens.ChoiceBox import ChoiceBox
from Screens.ChannelSelection import service_types_tv
from .__init__ import _
from .Debug import logger


class ChannelSelection():
    def __init__(self, session):
        self.session = session
        self.callback = None

    def getChannel(self, callback):
        logger.info("...")
        self.__callback = callback
        bouquet_list = self.getBouquets()
        self.session.openWithCallback(
            self.gotBouquet,
            ChoiceBox,
            titlebartext=_("Select bouquet"),
            list=bouquet_list,
            keys=[]
        )

    def getBouquets(self):
        tvbouquets = getTVBouquets()
        alist = []
        alist.append(["Alle Sender (Enigma)", service_types_tv])
        for bouquet in tvbouquets:
            logger.debug("bouquet: %s", bouquet)
            alist.append([bouquet[1], bouquet[0]])
        return alist

    def gotBouquet(self, choice):
        if choice:
            channel_list = self.getChannels(choice[1])
            self.session.openWithCallback(
                self.gotChannel,
                ChoiceBox,
                titlebartext=_("Select channel"),
                list=channel_list,
                keys=[]
            )
        else:
            self.__callback(None)

    def getChannels(self, bouquet):
        logger.info("...")
        servicetypes = bouquet + " ORDER BY name"
        service_list = getServiceList(servicetypes)
        logger.debug("service_list: %s", service_list)
        if service_list:
            alist = []
            for service, ename in service_list:
                if "::" not in service:
                    alist.append((ename, service))
        return alist

    def gotChannel(self, choice):
        logger.debug("choice: %s", choice)
        if choice:
            self.__callback(choice[1])
        else:
            self.__callback(None)
