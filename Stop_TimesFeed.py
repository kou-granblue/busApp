# -*- coding: utf-8 -*-
import os

class Stop_TimesFeed:

    def __init__(self, userdirectorypath):
        self.stop_times = []
        self.FILE_NAME = 'stop_times.txt'
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
                self.addStop_Time(int(token[0]), token[1], token[2], int(token[3]), int(token[4]))

            fileRead.close()

    # TripIDと一致した要素のListを返す
    def getStop_Time(self, tripid):
        result = []
        if self.stop_times == None:
            print('stop_times is null')
            return None
        
        for stop_time in self.stop_times:
            if stop_time.getTripId() == tripid:
                result.append(stop_time)

        if len(result) == 0:
            print('stop_time not found')
            return None

        return result

    # その旅程(TripID)内で最初の出発バス停の要素を返す sequence : 0
    def getEarliestStop_TimeAmongTrip(self, tripid):
        if tripid == -1:
            print('tripid = -1')
            return None
        if self.stop_times == None:
            print('stop_times is null')
            return None

        for stop_time in self.stop_times:
            # TripIDを検索
            if stop_time.getTripId() == tripid:
                # stopsequence=0ならば(旅程内最初のバス停)
                if stop_time.getStopSequence() == 0:
                    return stop_time


        return None

     # Stop_TimeクラスのオブジェクトをListに格納
    def addStop_Time(self, tripid, arrivaltime, departuretime, stopid, stopsequence):
        if self.stop_times == None:
            print('Error')
            return
        self.stop_times.append(Stop_TimesFeed.Stop_Time(tripid, arrivaltime, departuretime, stopid, stopsequence))

    # 引数のTrip内の1番最初のバス停出発時刻を返す
    def getFirstDepartureTimeOfTrip(self, tripid):
        sequence = -1
        result = None
        if tripid == -1:
            return None
        # TripID内で最小のStopSequenceを求める
        for stop_time in self.stop_times:
            if stop_time.getTripId() != tripid:
                continue
            num = stop_time.getStopSequence()
            if sequence == -1 or sequence > num:
                sequence = num
                result = stop_time.getDepartureTime()


        return result


    # Stop_times.txtのデータ構造を表したクラス
    class Stop_Time:
        def __init__(self, tripid, arrivaltime, departuretime, stopid, stopsequence):
            self._tripid = tripid
            self._arrivaltime = arrivaltime
            self._departuretime = departuretime
            self._stopid = stopid
            self._stopsequence = stopsequence
            
        def getTripId(self):
            return self._tripid

        def getArrivalTime(self):
            return self._arrivaltime

        def getDepartureTime(self):
            return self._departuretime

        def getStopId(self):
            return self._stopid

        def getStopSequence(self):
            return self._stopsequence
