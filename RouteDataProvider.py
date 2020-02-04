# -*- coding: utf-8 -*-
import RouteFeed
import TripsFeed
import StopsFeed
import Stop_TimesFeed
import CalendarFeed
import ShapesFeed

class RouteDataProvider:

    def __init__(self, userdirectorypath):
        self._routes = RouteFeed.RouteFeed(userdirectorypath)
        self._trips = TripsFeed.TripsFeed(userdirectorypath)
        self._stops = StopsFeed.StopsFeed(userdirectorypath)
        self._stop_times = Stop_TimesFeed.Stop_TimesFeed(userdirectorypath)
        self._calendar = CalendarFeed.CalendarFeed(userdirectorypath)
        self._shapes = ShapesFeed.ShapesFeed(userdirectorypath)



    def setStops(self, stops):
        self._stops = stops

    def setRoutes(self, routes):
        self._routes = routes

    def setTrip(self, trips):
        self._trips = trips

    def setStop_Times(self, stop_times):
        self._stop_times = stop_times

    def setCalendar(self, calendar):
        self._calendar = calendar

    def setShapes(self, shapes):
        self._shapes = shapes

    def getStops(self):
        return self._stops

    def getRoutes(self):
        return self._routes

    def getTrips(self):
        return self._trips

    def getStop_Times(self):
        return self._stop_times

    def getCalendar(self):
        return self._calendar

    def getShapes(self):
        return self._shapes
