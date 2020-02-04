# -*- coding: utf-8 -*-
import os

class TripsFeed:

    def __init__(self, userdirectorypath):
        self.trips = []
        self.FILE_NAME = 'trips.txt'
        self.FEED_DIRECTORY = 'google_transit_feed'
        self.state = False

        filePath = userdirectorypath+'/'+self.FEED_DIRECTORY+'/'+self.FILE_NAME

        if os.path.exists(filePath):
            fileRead =open(filePath, 'r',  encoding="utf-8")
            readData = fileRead.readlines()

            for line in readData:
                if self.state == False:
                    self.state = True
                    continue
                token = line.split(',')
                self.addTrip(int(token[0]), int(token[1]), int(token[2]), int(token[3]))

            fileRead.close()

    # 使用するTripを返す
    def getTrip(self, id):
        if id == -1:
            print('id = -1')
        if self.trips == None:
            print('trips is null')
        for i in self.trips:
            if i.getId() == id:
                return i

    # 旅程選択フォームで選択されたRouteIDを持つ旅程リストを返す
    def getTripAreIncludeRoute(self, routeid):
        triplist = []
        if routeid == -1:
            print('routeid = -1')
            return None
        if self.trips == None:
            print('trips is null')
            return None

        # 全旅程が入ったListから選択されたRouteIDを持つtripのみのListを作成
        for trip in self.trips:
            if trip.getRouteId() == routeid:
                triplist.append(trip)
        
        if len(self.trips) == 0:
            return None
        
        return triplist


    # TripクラスのオブジェクトをListに格納
    def addTrip(self, routeid, serviceid, id, shapeid):
        if self.trips == None:
            print('Error')
            return
        self.trips.append(TripsFeed.Trip(routeid, serviceid, id, shapeid))


    # Trips.txtのデータ構造を表したクラス
    class Trip:
        def __init__(self, routeid, serviceid, id, shapeid):
            self._routeid = routeid
            self._serviceid = serviceid
            self._id = id
            self._shapeid = shapeid
            
        def getId(self):
            return self._id

        def getRouteId(self):
            return self._routeid

        def getServiceId(self):
            return self._serviceid

        def getShapeId(self):
            return self._shapeid

