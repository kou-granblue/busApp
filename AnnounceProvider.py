# -*- coding: utf-8 -*-
import AnnounceFeed
import Announce_TripFeed

class AnnounceProvider:

    def __init__(self, userdirectorypath):
        self._announces = AnnounceFeed.AnnounceFeed(userdirectorypath)
        self._trips = Announce_TripFeed.Announce_TripFeed(userdirectorypath)


    def getAnnounces(self):
        return self._announces

    def getAnnounce_Trips(self):
        return self._trips

