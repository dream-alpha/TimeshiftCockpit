# coding=utf-8
# Copyright (C) 2018-2025 by dream-alpha
# License: GNU General Public License v3.0 (see LICENSE file for details)


from ServiceReference import ServiceReference
from Screens.Screen import Screen
from Screens.HelpMenu import HelpableScreen
from Components.Button import Button
from Components.Sources.List import List
from Components.ActionMap import HelpableActionMap
from .__init__ import _
from .SkinUtils import getSkinName
from .ServiceUtils import getPicon
from .Debug import logger


class TimeshiftOverview(Screen, HelpableScreen):

    def __init__(self, session, infobar_instance):
        self.infobar_instance = infobar_instance
        Screen.__init__(self, session)
        HelpableScreen.__init__(self)
        self.skinName = getSkinName("TimeshiftOverview")

        self["actions"] = HelpableActionMap(
            self,
            "TimeshiftCockpitActions",
            {
                "OK": (self.exit, _("Exit")),
                "EXIT":	(self.exit, _("Exit")),
                "RED": (self.exit, _("Exit")),
                "GREEN": (self.exit, _("Exit")),
            },
            prio=-1
        )

        self.setTitle(_("Timeshifts Overview"))
        self["list"] = List()
        self["key_green"] = Button()
        self["key_red"] = Button(_("Cancel"))
        self["key_yellow"] = Button()
        self["key_blue"] = Button()
        self.onLayoutFinish.append(self.fillList)

    def exit(self):
        self.close()

    def fillList(self):
        logger.info("...")
        alist = []
        for service_str in self.infobar_instance.timeshifts.keys():
            pixmap_ptr = getPicon(service_str)
            service_name = ServiceReference(service_str).getServiceName()
            timeshift_type = f"{_('type')}: {_('fixed') if service_str in self.infobar_instance.fixed_services else _('variable')}"
            timeshift_recordings = f"{_('recordings')}: {len(self.infobar_instance.getTimeshiftRecordings(service_str))}"
            alist.append((pixmap_ptr, service_name, timeshift_type, timeshift_recordings))
        alist = sorted(alist, key=lambda x: (x[2], x[1]))
        self["list"].setList(alist)
        self["list"].master.downstream_elements.setSelectionEnabled(0)
