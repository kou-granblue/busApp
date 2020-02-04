import os
from operator import attrgetter

class Announce_TripFeed:
    def __init__(self, userdirectorypath):
        self.announce_trips = []
        self.FILE_NAME = 'trips.txt'
        self.FEED_DIRECTORY = 'announce_feed'
        self.state = False

        # ファイルパスを用意
        filePath = userdirectorypath+'/'+self.FEED_DIRECTORY+'/'+self.FILE_NAME
        if os.path.exists(filePath):
            fileRead =open(filePath, 'r',  encoding="utf-8")
            readData = fileRead.readlines()

            for line in readData:
                if self.state == False:
                    self.state = True
                    continue
                token = line.split(',')
                self.addAnnounce_Trip(int(token[0]), int(token[1]), int(token[2]))
            fileRead.close()

    # 運行される旅程IDのみで構成されたリストを返す
    def getAnnounce_Trips(self, tripid):
        sortlist = []
        # 全要素を検索
        for trip in self.announce_trips:
            if trip.getId() == tripid:
                sortlist.append(trip)
        if len(sortlist) == 0:
            return None
        # announces_sequenceでソートを行う
        sort_finish = sorted(sortlist)

        return sort_finish
        


    
    
    def addAnnounce_Trip(self, tripid, announceid, announce_sequences):
        if self.announce_trips == None:
            print('Error')
            return
        self.announce_trips.append(Announce_TripFeed.Announce_Trip(tripid, announceid, announce_sequences))


   
    class Announce_Trip:
        def __init__(self, tripid, announce_id, announce_sequence):
            self._tripid = tripid
            self._announceid = announce_id
            self._announceSequence = announce_sequence

        def __lt__(self, other):
            return (self._announceSequence) < (other._announceSequence)

        def getId(self):
            return self._tripid

        def getAnnounceId(self):
            return self._announceid

        def getAnnounceSequences(self):
            return self._announceSequence

