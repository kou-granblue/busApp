import os
import datetime

class BusLocationGetter:
    def __init__(self, mycallback):
        self._myCallback = mycallback

    # 2s毎に実行
    def LocationCallback(self, dt):
        locationPath = os.getcwd() + r'/rtk_location/rtk_file.pos'
        print('LocationGetter : ' + str(datetime.datetime.today()))
        if self._myCallback != None:
            fileRead = open(locationPath, 'r')
            lines = fileRead.readlines()
            stripList = lines[-1].split()
            fileRead.close()
            self.mCurrentLocation = []
            self.mCurrentLocation.append(stripList[2])
            self.mCurrentLocation.append(stripList[3])
            self._myCallback(self.mCurrentLocation)          
        else:
            return
            
    def getLocation(self):
        return self.mCurrentLocation
