# -*- coding: utf-8 -*-
import os

class ShapesFeed:

    def __init__(self, userdirectorypath):
        self.shapes = []
        self.FILE_NAME = 'shapes.txt'
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
                self.addShape(int(token[0]), token[1], token[2], int(token[3]))

            fileRead.close()

    def getShape(self, shapeid):
        shapelist = []
        if self.shapes == None or shapeid == -1:
            return None
        for shape in self.shapes:
            if shape.getShapeId() == shapeid:
                shapelist.append(shape)

        return shapelist

     # ShapeクラスのオブジェクトをListに格納
    def addShape(self, shapeid, lat, lon, sequence):
        if self.shapes == None:
            print('shapes is null')
            return
        self.shapes.append(ShapesFeed.Shape(shapeid, lat, lon, sequence))

    # shapes.txtのデータ構造を表したクラス
    class Shape:
        def __init__(self, shapeid, shape_pt_lat, shape_pt_lon, sequence):
            self._shapeid = shapeid
            self._shape_pt_lat = shape_pt_lat
            self._shape_pt_lon = shape_pt_lon
            self._shape_pt_sequence = sequence 
            
        def getShapeId(self):
            return self._shapeid

        def getLat(self):
            return self._shape_pt_lat

        def getLon(self):
            return self._shape_pt_lon

        def getSequence(self):
            return self._shape_pt_sequence

        
