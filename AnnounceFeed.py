import os

class AnnounceFeed:

    def __init__(self, userdirectorypath):
        self.announces = []
        self.FILE_NAME = 'announces_wav.txt'
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
                self.addAnnounce(int(token[0]), token[1], float(token[2]), float(token[3]), int(token[4]))
            fileRead.close()

    # 引数のIDを持つannouncesを返す
    def getAnnounce(self, id):
        if self.announces == None:
            return None
        for announce in self.announces:
            if announce.getId() == id:
                return announce
        return None

    def addAnnounce(self, id, filename, latitude, longitude, stop_sequence):
        if self.announces == None:
            print('Error')
            return
        self.announces.append(AnnounceFeed.Announce(id, filename, latitude, longitude, stop_sequence))


    class Announce:
        def __init__(self, id, filename, latitude, longitude, stop_sequence):
            self._id = id
            self._filename = filename
            self._latitude = latitude
            self._longitude = longitude
            self._stopSequence = stop_sequence
            
        def getId(self):
            return self._id

        def getFileName(self):
            return self._filename

        def getLatitude(self):
            return self._latitude

        def getLongitude(self):
            return self._longitude

        def getStopSequences(self):
            return self._stopSequence

        def getString(self):
            return str(self._id)+','+self._filename+','+str(self._latitude)+','+str(self._longitude)+','+str(self._stopSequence)
