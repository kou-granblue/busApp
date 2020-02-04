from MySingleton import MySingleton
from math import sin, cos, sqrt, atan2, radians
import datetime

class TripManager:

    # アナウンスファイル格納用パス設定
    def __init__(self, directory):
        self._busState = False
        self._isRunning = False
        self.forcedTransitionFlag = False
        self.MAX_DISTANCE = 30
        self.ANNOUNCE_DISTANCE = 40.0
        self.ANNOUNCE_DATA_DIRECTORY = directory + MySingleton().get_annunceDataDirectoryName()

    # CallBackの設定
    def setCallback(self, arriveAtStopCallback, departFromStopCallback, setDistanceCallback, announcePlay, skipCheck, backCheck, announceStop, waitDisplay):
        self._arriveAtStopCallback = arriveAtStopCallback
        self._departFromStopCallback = departFromStopCallback
        self._setDistanceCallback = setDistanceCallback
        self._announcePlayCallback = announcePlay
        self._skipFlagCheckCallback = skipCheck
        self._backFlagCheckCallback = backCheck
        self._announceStopCallback = announceStop
        self._waitDisplayCallback = waitDisplay

    # Trip開始
    def start(self, tripid):
        # アナウンス用,静的フィードのproviderを取得
        self._announceProvider = MySingleton().getAnnounceProvider()
        self._provider = MySingleton().getRouteDataProvider()

        # 運行旅程のTripIDをインスタンス変数に代入
        self._tripid = tripid

        # バス停情報とアナウンス用のsequence番号に0をセット
        self.stopSequenceNum = 0
        self.announceSequenceNum = 0
        self.postCounter = -1
        self.postMAX = -1

        # バス停リスト用のList
        self._stopList = []

        # バス停の停車順序
        self._stopSequence = -1

        if self._provider != None and self._provider.getStop_Times() != None:
            # 運行旅程内のStop_Timeを取得
            stoptimeList = self._provider.getStop_Times().getStop_Time(self._tripid)

            if stoptimeList != None:
                for stop_time in stoptimeList:
                    if self._provider == None or self._provider.getStops() == None:
                        print('stops not found')
                        continue
                    # stop_timeからstopIDを取得
                    stopdata = self._provider.getStops().getStop(stop_time.getStopId())

                    # Stopクラス格納用リストに追加
                    self._stopList.append(TripManager.Stop(stopdata.getId(), stopdata.getName(), stop_time.getArrivalTime(), stop_time.getDepartureTime(), stopdata.getLatitude(), stopdata.getLongitude(), stop_time.getStopSequence()))
        else:
            print('stop_times not found')

        # アナウンスリストを生成する
        self.createAnnounceList()
        # 走行中にする
        self._isRunning = True


    # Trip終了処理
    def finish(self):
        result = {}
        if self._busState == True:
            # バス停情報を取得
            if self._stopList != None and self.stopSequenceNum < len(self._stopList):
                stop = self._stopList[self.stopSequenceNum]
                # Delayの計算
                date = stop.get_departureTime()
                now = datetime.datetime.now().strftime('%H:%M:%S')
                nowTime = datetime.datetime.strptime(now, '%H:%M:%S')
                departureTime = datetime.datetime.strptime(date, "%H:%M:%S")
                if nowTime > departureTime:
                    _delay = (nowTime - departureTime).seconds
                else:
                    _delay = -(departureTime - nowTime).seconds
                # Dictに各値(Delay stopID, StopSequence)を格納
                result['delay'] = _delay
                result['stopid'] = stop.get_stopId()
                result['stopsequence'] = stop.get_stopSequence()
            self._busState = False
        self._isRunning = False
        return result



    # 最終停留所のStopを返す
    def getLastStop(self):
        if self._stopList != None or len(self._stopList) < self.stopSequenceNum:
            return None
        return self._stopList[self.stopSequenceNum]


    # バス停停車中かどうか返す
    def getBusState(self):
        return self._busState

    # 走行中かどうか返す
    def isRunning(self):
        return self._isRunning

    # Postしていいか確認する
    def checkPost(self):
        return self.postMAX

    # 定期実行されるcallbackメソッドから呼ばれるメソッド
    def onLocationChanged(self, location):
        if self.isRunning() != True:
            return
        # sropListのフィード取得できてなかったら以下の処理しない
        if self._stopList == None or len(self._stopList) <= 0 or self.stopSequenceNum >= len(self._stopList):
            print('stoplist not available')
            return

        # 取得した緯度と経度をもらう
        try:
            lat = float(location[0])
            lon = float(location[1])
        except:
            self._waitDisplayCallback()
            return

        # Backフラグのチェック
        if self._backFlagCheckCallback():
            # バス停,アナウンス音声のSequenceを2つ前に(実質的には1つ戻る)
            self.postCounter = self.stopSequenceNum
            if self.postCounter > self.postMAX:
                self.postMAX = self.postCounter
            self.announceSequenceNum -= 2
            self.stopSequenceNum -= 2
            # 強制遷移フラグをTrueにする
            self.forcedTransitionFlag = True


        # バス停を取得
        stop = self._stopList[self.stopSequenceNum]

        # 取得したバス停の緯度と経度を取得
        stoplat = stop.getLatitude()
        stoplon = stop.getLongitude()

        # 現在地との距離を計算(単位 : m)
        distance = self.getDistance(stoplat, stoplon, lat, lon)
        self._setDistanceCallback(str(int(distance)))


        # 最後のアナウンス処理用
        if self._announceList != None and (self.announceSequenceNum + 2) ==  len(self._announceList):
            # アナウンスデータ取得
            announce = self._announceList[self.announceSequenceNum + 1]
            # アナウンスを流す条件
            if self.getDistance(lat, lon, announce.getLatitude(), announce.getLongitude()) <= self.ANNOUNCE_DISTANCE and announce.getStopSequences() == self._stopSequence:
                self._announcePlayCallback(announce.getFileName())
                self.announceSequenceNum +=  1

        # SKIPフラグがたっているか or 強制遷移フラグがたっているか
        if self._skipFlagCheckCallback() or self.forcedTransitionFlag:
            self.forcedTransitionFlag = True
            # 強制遷移
            self.arriveAtStop(stop)

        # バス停までの距離が30m以内
        if distance <= self.MAX_DISTANCE:
            self.arriveAtStop(stop)

        # バス停までの距離が30m以上
        if distance > self.MAX_DISTANCE:
            self.departFromStop(stop)


    # バス停までの距離が30m以内(バス停到着時)
    def arriveAtStop(self, stop):
        # 走行中か否か
        if self.isRunning() == False:
            return
        # _busStateはTrueであればバス停停車中
        if self._busState == False:
            self._busState = True
            self._stopSequence = stop.get_stopSequence()

            # BackかSKIP押された時に現在のアナウンスを一度止める(強制遷移フラグで確認)
            if self.forcedTransitionFlag:
                self.forcedTransitionFlag = False
                # 現在のアナウンスを止める
                self._announceStopCallback()

            # delay(遅延時間を計算する) 単位 : s
            date = stop.get_arrivalTime()
            now = datetime.datetime.now().strftime('%H:%M:%S')
            nowTime = datetime.datetime.strptime(now, '%H:%M:%S')
            arrivalTime = datetime.datetime.strptime(date, "%H:%M:%S")
            if nowTime > arrivalTime:
                _delay = (nowTime - arrivalTime).seconds
            else:
                _delay = -(arrivalTime - nowTime).seconds
            self._arriveAtStopCallback(self._tripid, _delay, stop)


    # バス停までの距離が30mより大きいとき
    def departFromStop(self, stop):
        # バスが走ってるか否か
        if self.isRunning() == False:
            return
        if self._busState == False or stop == None:
            return
        # 停車から出発に遷移
        print('depart at stop')

        # バス停出発時にアナウンスを流す
        if self._announceList != None and self.announceSequenceNum < len(self._announceList):
            # アナウンスデータ取得
            self.announceSequenceNum += 1
            announce = self._announceList[self.announceSequenceNum]
            # アナウンスを流す条件
            if announce.getStopSequences() == self._stopSequence:
                self._announcePlayCallback(announce.getFileName())

         # delay(遅延時間を計算する) 単位 : s
        date = stop.get_departureTime()
        now = datetime.datetime.now().strftime('%H:%M:%S')
        nowTime = datetime.datetime.strptime(now, '%H:%M:%S')
        departureTime = datetime.datetime.strptime(date, "%H:%M:%S")
        if nowTime > departureTime:
            _delay = (nowTime - departureTime).seconds
        else:
            _delay = -(departureTime - nowTime).seconds

        # バス停を出発した状態にする
        self._busState = False
        # 次のバス停の要素を取得するためのシーケンス番号をインクリメント
        self.stopSequenceNum += 1
        # _stopListがNoneでない且つまだ、要素が残っているとき(最終停留所じゃないとき)
        if self._stopList != None and self.stopSequenceNum < len(self._stopList):
            # 次のバス停得るためにこっち実行
            self._departFromStopCallback(self._tripid, _delay, stop, self._stopList[self.stopSequenceNum])
        else:
            # 終了を伝えるためこっち実行
            self._departFromStopCallback(self._tripid, _delay, stop, None)








    # 距離を計算する
    def getDistance(self, lat1, lon1, lat2, lon2):
        R = 6373.0

        lat1 = radians(float(lat1))
        lon1 = radians(float(lon1))
        lat2 = radians(float(lat2))
        lon2 = radians(float(lon2))

        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        distance = R * c
        return distance * 1000


    # 再生するアナウンスのリストを作成
    def createAnnounceList(self):
        self._announceList = []
        if self._announceProvider != None and self._announceProvider.getAnnounce_Trips() != None:
            triplist = self._announceProvider.getAnnounce_Trips().getAnnounce_Trips(self._tripid)
        if self._announceProvider == None or self._announceProvider.getAnnounces() == None:
            return
        if triplist != None and len(triplist) != 0:
            for trip in triplist:
                self._announceList.append(self._announceProvider.getAnnounces().getAnnounce(trip.getAnnounceId()))



    # 音声を再生する
    def playAnnounce(self, filepath):
        pass

    # 音声を止める
    def stopAnnounce(self):
        pass

    # 次のバス停のstopSequenceを返す
    def getNextStopSequence(self):
        if self._stopList == None:
            print('stoplist not found')
            return -1
        if len(self._stopList) <= (self.stopSequenceNum+1):
            return -1
        return self._stopList[self.stopSequenceNum+1].get_stopSequence()

    class Stop:
        def __init__(self, stopid, name, arrivalTime, departureTime, latitude, longitude, stopSequence):
            self._stopId = stopid
            self._name = name
            self._arrivalTime = arrivalTime
            self._departureTime = departureTime
            self._latitude = latitude
            self._longitude = longitude
            self._stopSequence = stopSequence


        def get_stopId(self):
            return self._stopId

        def getLongitude(self):
            return self._longitude

        def getLatitude(self):
            return self._latitude

        def getName(self):
            return self._name

        def get_arrivalTime(self):
            return self._arrivalTime

        def get_departureTime(self):
            return self._departureTime

        def get_stopSequence(self):
            return self._stopSequence
