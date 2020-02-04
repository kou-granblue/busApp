import datetime

class VehiclePositonExporter:
    # 初期化メソッド
    def __init__(self, locationgetter, url):
        self._stopSequence = -1
        self._tripid = 0
        self._trainnumber = '1'
        self._running = False
        self._locationgetter = locationgetter
        self.REQUEST_URL_RESEPONSE_STRING = url+'AddVehiclePosition'
        # isRunning 走行中 / onBusStop バス停停車中
        self.ISRUNNING = 'isRunning'
        self.ONBUSSTOP = 'onBusStop'
        self._busState = self.ISRUNNING 

    # CallBackの設定
    def setCallback(self, addVehicleCallback):
        self._addVehicleCallback = addVehicleCallback

       
    # 10s毎に実行されるprocess
    def vehicleRefreshTask(self, dt):
        print('Exporter : ' + str(datetime.datetime.today()))
        if self._running == True:
            self.refreshVehicles()
        else:
            return



    # 10s毎に送信を開始する
    def start(self):
        self._running = True
        return True

    # 送信処理を終了する
    def stop(self):
        self._running = False

    # バス停情報の更新
    def updateBusState(self, message, stopSequence):
        if stopSequence != -1:
            # 次のバス停に遷移
            self._stopSequence = stopSequence
        else:
            parameters = {'trainNumber' : str(self._trainnumber), 'message' : 'finish'}
            print('POST AddVehicle Position(Finish)')
            self._addVehicleCallback(parameters, self.REQUEST_URL_RESEPONSE_STRING)
        if message == None:
            return
        if message == 'onArrival':
            self._busState = self.ONBUSSTOP
        elif message == 'onDeparture':
            self._busState = self.ISRUNNING    



    # 位置情報のPOSTを行う本体
    def refreshVehicles(self):
        # BusLocationGetterで取得している位置情報を取得
        location = self._locationgetter.getLocation()
        # 緯度と経度のみを取得
        try:
            longitude = float(location[1])
            latitude = float(location[0])
        except:
            return

        # 運行されているTripIDを取得
        trip = self._tripid

        # サーバに送信するパラメータ
        parameters = {'trainNumber' : str(self._trainnumber), 'longitude' :  str(longitude), 'latitude' : str(latitude), 'trip' : str(trip)}
        if self._stopSequence >= 0:
            # パラメータの追加
            parameters['nextStopSequence'] = str(self._stopSequence)
        # POST
        self._addVehicleCallback(parameters, self.REQUEST_URL_RESEPONSE_STRING)
        
    def setTripid(self, trip_id):
        self._tripid = trip_id