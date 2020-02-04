# -*- coding: utf-8 -*-
import os


class RouteFeed:

    def __init__(self, userdirectorypath):
        self.routes = []
        self.FILE_NAME = 'routes.txt'
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
                self.addRoute(int(token[0]), token[1], token[2])
            fileRead.close()


    # 引数のRouteIDを持っているrouteを返す
    def getRoute(self, id):
        if self.routes == None:
            return None
        for i in self.routes:
            if i.getId() == id:
                return i

    def getRoutes(self):
        return self.routes

    # RouteクラスのオブジェクトをListに格納
    def addRoute(self, id, shortname, longname):
        if self.routes == None:
            print('Error')
            return
        self.routes.append(RouteFeed.Route(id, shortname, longname))

    

    # routes.txtのデータ構造を表したクラス
    class Route:
        def __init__(self, id, shortname, longname):
            self._id = id
            self._shortname = shortname
            self._longname = longname
            self._routetype = '3'
            
        def getId(self):
            return self._id

        def getShortName(self):
            return self._shortname

        def getLongName(self):
            return self._longname
