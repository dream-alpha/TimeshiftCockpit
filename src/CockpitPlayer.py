# coding=utf-8
# Copyright (C) 2018-2025 by dream-alpha
# License: GNU General Public License v3.0 (see LICENSE file for details)


import os
from time import time
from Components.ActionMap import HelpableActionMap
from Components.config import config
from Components.ServiceEventTracker import ServiceEventTracker, InfoBarBase
from Components.Sources.COCCurrentService import COCCurrentService
from Screens.Screen import Screen
from Screens.HelpMenu import HelpableScreen
from Screens.InfoBarGenerics import InfoBarAudioSelection, InfoBarShowHide, InfoBarNotifications
from Screens.MessageBox import MessageBox
from ServiceReference import ServiceReference
from enigma import iPlayableService
from .__init__ import _
from .Debug import logger
from .CockpitSeek import CockpitSeek
from .CockpitCueSheet import CockpitCueSheet
from .MovieInfoEPG import MovieInfoEPG
from .SkinUtils import getSkinName
from .CockpitPVRState import CockpitPVRState
from .BoxUtils import getBoxType
from .Version import ID
from .EventChoiceBox import EventChoiceBox
from .DelayTimer import DelayTimer
from .TimeshiftUtils import manageTimeshiftRecordings
from .TimeshiftOverview import TimeshiftOverview


class CockpitPlayerSummary(Screen):

    def __init__(self, session, parent):
        Screen.__init__(self, session, parent)
        self.skinName = ID + "CockpitPlayerSummary"


class CockpitPlayer(
        Screen, HelpableScreen, InfoBarBase, InfoBarNotifications, CockpitSeek, InfoBarShowHide, InfoBarAudioSelection, CockpitPVRState, CockpitCueSheet, EventChoiceBox):

    ENABLE_RESUME_SUPPORT = False
    ALLOW_SUSPEND = False

    def __init__(self, session, service, config_plugins_plugin, timeshift_start_time, infobar_instance, service_ref, dont_pause):
        logger.info("timeshift_start_time: %s", timeshift_start_time)
        self.service = service
        self.config_plugins_plugin = config_plugins_plugin
        self.timeshift_start_time = timeshift_start_time
        self.infobar_instance = infobar_instance
        self.service_ref = service_ref
        self.dont_pause = dont_pause

        Screen.__init__(self, session)
        HelpableScreen.__init__(self)
        InfoBarShowHide.__init__(self)
        InfoBarBase.__init__(self)
        InfoBarAudioSelection.__init__(self)
        InfoBarNotifications.__init__(self)
        CockpitCueSheet.__init__(self, service)
        EventChoiceBox.__init__(self)

        self["Service"] = COCCurrentService(session.nav, self)

        event_start = True
        self.service_started = False

        CockpitSeek.__init__(self, session, service, event_start,
                             timeshift_start_time, timeshift=True, service_center=None)
        CockpitPVRState.__init__(self)

        self._event_tracker = ServiceEventTracker(
            screen=self,
            eventmap={
                iPlayableService.evStart: self.__serviceStarted,
            }
        )

        actions = {
            "EXIT": (self.leavePlayer, _("Stop timeshift")),
            "STOP": (self.leavePlayer, _("Stop timeshift")),
            "POWER": (self.powerDown, _("Power off")),
            "INFO": (self.showMovieInfo, _("Movie info")),
            "NEXT": (self.nextEvent, _("Next event")),
            "PREVIOUS":	(self.previousEvent, _("Previous event")),
            "MENU": (self.selectEventPlayback, _("Show events")),
            "RECORD": (self.selectEventRecording, _("Record timeshift Event")),
            "BLUE": (self.blueKey, _("Show active timeshifts")),
            "YELLOW": (self.yellowKey, _("Manage timeshift recordings")),
            "HELP": (self.noOp,	"")
        }

        if config_plugins_plugin.permanent.value:
            actions["UP"] = (self.up, _("Open service list"))
            actions["DOWN"] = (self.down, _("Open service list"))

        self["actions"] = HelpableActionMap(
            self,
            "TimeshiftCockpitActions",
            actions,
            -1
        )

        self.execing = None
        self.is_closing = False
        self.skinName = getSkinName("CockpitPlayer")
        self.cut_list = []

        self.onShown.append(self.__onShown)

    def noOp(self):
        return

    def blueKey(self):
        self.session.open(TimeshiftOverview, self.infobar_instance)

    def yellowKey(self):
        manageTimeshiftRecordings(self.session, ID)

    def powerDown(self):
        self.close("power_down")

    def up(self):
        self.close("up")

    def down(self):
        self.close("down")

    def getInfo(self):
        return None

    def getEvent(self):
        return self.event

    def newEvent(self, event):
        self["Service"].newEvent(event)

    def selectEventPlayback(self):
        self.openEventChoiceBox(self.session, _(
            "Select a timeshift event for playback"), self.selectEventPlaybackCallback)

    def selectEventPlaybackCallback(self, answer=None):
        logger.info("...")
        if answer:
            event_start = answer[1][0]
            logger.debug("event_start: %s", event_start)
            self.doSkip(max(0, event_start - self.timeshift_start_time))
            self.setSeekState(self.SEEK_STATE_PLAY)

    def selectEventRecording(self):
        logger.info("...")
        self.openEventChoiceBox(self.session, _(
            "Select a timeshift event for recording"), self.selectEventRecordingCallback)

    def selectEventRecordingCallback(self, answer=None):
        logger.info("...")
        if answer:
            event_data = answer[1]
            logger.debug("event_data: %s", event_data)
            self.infobar_instance.startTSRecording(
                self.service_ref, event_data)
            DelayTimer(1000, self.session.open, MessageBox, _(
                "Recording timeshift event now") + "...", MessageBox.TYPE_INFO, 5)

    def createSummary(self):
        return CockpitPlayerSummary

    def __onShown(self):
        logger.info("...")
        if not os.path.exists(config.usage.timeshift_path.value):
            self.session.open(MessageBox, _("Timeshift directory does not exist")
                              + ": " + config.usage.timeshift_path.value, MessageBox.TYPE_ERROR)
            self.leavePlayer()
        if not self.service_started:
            self.session.nav.playService(self.service)

    def __serviceStarted(self):
        logger.info("...")
        if not self.service_started:
            self.service_started = True
            if self.config_plugins_plugin.permanent.value:
                self.doSkip(int(time()) - self.timeshift_start_time)
                if not self.dont_pause:
                    self.pauseService()

    def showMovieInfo(self):
        if self.event:
            self.session.open(MovieInfoEPG, self.event,
                              ServiceReference(self.service))

    def showPVRStatePic(self, show):
        self.show_state_pic = show

    def leavePlayer(self):
        logger.info("...")
        self.close()

    def doEofInternal(self, playing):
        logger.info("playing: %s, self.execing: %s", playing, self.execing)
        if self.execing:
            logger.debug("switching to playback, seek_state: %s",
                         self.seekstate)
            if not getBoxType().startswith("dream"):
                self.session.nav.stopService()
            self.session.nav.playService(self.service)
            self.recoverEoFFailure()
