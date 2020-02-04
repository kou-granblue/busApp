# -*- coding: utf-8 -*-
import os

class StopsFeed:

    def __init__(self, userdirectorypath):
        self.stops = []
        self.FILE_NAME = 'stops.txt'
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
                self.addStop(int(token[0]), token[1], token[2], token[3])

            fileRead.close()

    # 引数の持つstopを返す
    def getStop(self, id):
        if id == -1:
            print('id = -1')
            return None
        if self.stops == None:
            print('stops is null')
        for stop in self.stops:
            if stop.getId() == id:
                return stop
        return None


     # StopクラスのオブジェクトをListに格納
    def addStop(self, id, name, lat, lon):
        if self.stops == None:
            print('Error')
            return
        self.stops.append(StopsFeed.Stop(id, name, lat, lon))


    # Stops.txtのデータ構造を表したクラス
    class Stop:
        def __init__(self, id, name, lat, lon):
            self._id = id
            self._name = name
            self._lat = lat
            self._lon = lon
            
        def getId(self):
            return self._id

        def getName(self):
            return self._name

        def getLatitude(self):
            return self._lat

        def getLongitude(self):
            return self._lon
