from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.modalview import ModalView
from kivy.uix.slider import Slider
from kivy.uix.popup import Popup
from kivy.factory import Factory
from kivy.resources import resource_add_path
from kivy.core.text import LabelBase, DEFAULT_FONT
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
from crypt import AESCipher
from MySingleton import MySingleton
from TripManager import TripManager
from BusLocationGetter import BusLocationGetter
from VehiclePositionExporter import VehiclePositonExporter
import pygame.mixer
import zipfile
import datetime
import requests
import time
import os
import subprocess

os.environ['KIVY_GL_BACKEND'] = 'gl'

# 日本語使用するためfont
LabelBase.register(DEFAULT_FONT, r'./font/FONT')

# ServletAPIbaseURL
base_url = "http://FQCN/BusApplicationServerSide"

# ユーザデータ保存用
user_file = os.getcwd()+ r'/savedata/userdata.txt'
voice_file = os.getcwd()+ r'/Voicedata/voicedata.txt'


pass_phrase = 'PASS PHRASE'
cipher = AESCipher(pass_phrase)

volume_data =os.getcwd() + r"/Voicedata/soundvolume.txt"
if os.path.exists(volume_data) == False:
    fw = open(volume_data, 'w')
    fw.write('0')
    fw.close()

# Main
class MainScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        pygame.mixer.init()
        self.evt = None
        self.evt2 = None
        self.ANNOUNCE_ZIP = 'announce_feed.zip'
        self._running = False
        self._vehiclenumber = '1'
        self._skipFlag = False
        self._backFlag = False
        self.counter = 0
        #self.ridenum = 0
        #self.getoffnum = 0
        self._tripManager = TripManager(os.getcwd())
        self._locaiongetter = BusLocationGetter(self._tripManager.onLocationChanged)
        self._vehiclepositionexporter = VehiclePositonExporter(self._locaiongetter, MySingleton().getApiBaseUrl())

    # アプリ終了
    def applicationFinish(self):
        if self._running == False:
            print('Finish Application')
            # ダイアログ
            content = FinishFormContent()
            self.finishform = Popup(title='Finish Dialog',content=content, size_hint=(0.5, 0.5), pos_hint={'center_x':0.5, 'top':0.8},auto_dismiss=False)
            content.ids['No'].bind(on_press=self.finishform.dismiss)
            content.ids['Yes'].bind(on_press=self.finishform.dismiss)
            self.finishform.open()

    # 開始ボタン処理
    def startButtonTouched(self):
        self.counter = 0
        self.ids['routeName'].value = 0
        self.skipCounter = 0
        self.backCounter = 0
        # TripManagerにCallBackを設定
        self._tripManager.setCallback(self.arriveAtStop, self.departFromStop, self.setDistanceCallBack, self.announcePlay, self.skipFlagCheck, self.backFlagCheck, self.announceStop, self.waitDisplay)
        self._vehiclepositionexporter.setCallback(self.addVehicle)
        self.setButtonsEnabledState()
        self.staticFeedfileDownLoad()

    # 終了ボタン処理
    def finishButtonTouched(self):
        if self._running == True:
            self.finishTrip()
            self._vehiclepositionexporter.stop()


    # スキップボタン処理
    def skipButtonTouched(self):
        # Flag設定
        self.skipCounter += 1
        self._skipFlag = True
        return

    # Skip Flag Check
    def skipFlagCheck(self):
        if self._skipFlag:
            self._skipFlag = False
            return True
        else:
            return False

    # バックボタン処理
    def backButtonTouched(self):
        self.backCounter += 1
        self._backFlag = True
        return

    # Back Flag Check
    def backFlagCheck(self):
        if self._backFlag:
            self._backFlag = False
            return True
        else:
            return False

    # 測位開始前
    def waitDisplay(self):
        self.ids['distance'].text = 'お待ちください'





    # 開始ボタンと終了ボタンの有効・無効化
    def setButtonsEnabledState(self):
        if self._running == False:
            self.ids['startbutton'].disabled = True
            self.ids['finishbutton'].disabled = False
            self.ids['skipbutton'].disabled = False
            self.ids['backbutton'].disabled = False
        else:
            self.ids['startbutton'].disabled = False
            self.ids['finishbutton'].disabled = True
            self.ids['skipbutton'].disabled = True
            self.ids['backbutton'].disabled = True

    # 距離を表示
    def setDistanceCallBack(self, distance):
        self.ids['distance'].text = 'Distance : ' + distance + 'm'


    # feedFile DL
    def staticFeedfileDownLoad(self):
        # Server側の更新日を取得
        res = requests.head('http://FQCN/bus/userdata/userfolder/google_transit.zip')
        update_day = res.headers['Last-Modified']
        server_file = datetime.datetime.strptime(update_day, '%a, %d %b %Y %H:%M:%S GMT' )

        # 自身のファイルの更新日を取得
        file_path = os.getcwd()+ r'/google_transit_feed'
        local_file = datetime.datetime.fromtimestamp(os.stat(file_path).st_mtime)

        # 更新日を比較する(サーバの方が最新ならばDLする)
        if local_file < server_file:
            filename = 'google_transit.zip'

            r = requests.post('http://FQCN/bus/userdata/userfolder/google_transit.zip', stream=True)
            with open(filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
                        f.flush()
            zip = zipfile.ZipFile('google_transit.zip')
            file_extract = os.getcwd()+ r'/google_transit_feed'
            zip.extractall(file_extract)
            zip.close()
        self.fileDownLoadCallBack()


    # staticフィード取得後処理
    def fileDownLoadCallBack(self):
        self._provider = MySingleton().getRouteDataProviderCreate()
        # 旅程選択フォームを生成する
        view = self.createRouteSelectForm()
        view.open()


    # RouteForm生成
    def createRouteSelectForm(self):
        def my_callback(instance):
            if self.counter == 0:
                self.counter += 1
                print(instance.content.ids['tripid'].value)
                self.ids['routeName'].value = instance.content.ids['tripid'].value
                return True
            else:
                return False

        content = RouteFormContent()
        content.setRouteName()
        self.routeform = Popup(title='Route Select',content=content, size_hint=(0.5, 0.5), pos_hint={'center_x':0.5, 'top':0.8}, auto_dismiss=False)
        self.routeform.bind(on_dismiss=my_callback)
        content.ids['Finish'].bind(on_press=self.routeform.dismiss)
        return self.routeform


    # 旅程選択後処理
    def onTripSelected(self):
        self.routeform.dismiss()
        self._vehiclepositionexporter.setTripid(self.ids['routeName'].value)
        if  os.path.exists(user_file):
            print('USER FILE EXIST')
        else:
            print('USER FILE NOT EXIST')
            return

        # TripID格納
        _tripid = self.ids['routeName'].value

        if self._provider != None and self._provider.getRoutes() != None and self._provider.getTrips() != None:
            print('show Route Name')
            self.ids['routeName'].text = self._provider.getRoutes().getRoute(self._provider.getTrips().getTrip(_tripid).getRouteId()).getLongName()
            # 旅程の最初の情報取得
            stop_time = self._provider.getStop_Times().getEarliestStop_TimeAmongTrip(_tripid)
            self.changeNextStop(self._provider.getStops().getStop(stop_time.getStopId()).getName(), stop_time.getDepartureTime())
            # Login処理
            self.afterLogging()

     # 運行の開始のメソッド
    def startTrip(self):
        _tripid = self.ids['routeName'].value
        self._running = True
        self._tripManager.start(_tripid)
        self._vehiclepositionexporter.start()
        self._vehiclepositionexporter.updateBusState(None, self._tripManager.getNextStopSequence())
        if os.path.exists(voice_file):
            fr = open(voice_file, 'r')
            id = int(fr.readline())
            fr.close()
        self.evt = Clock.schedule_interval(self._locaiongetter.LocationCallback, 1)
        self.evt2 = Clock.schedule_interval(self._vehiclepositionexporter.vehicleRefreshTask, 10)

    # 旅程選択後
    def afterLogging(self):
        if  os.path.exists(user_file):
            data_check = open(user_file, 'r')
            readData = data_check.readlines()
            name = readData[0].replace('\n','').split(',')[1]
            password = readData[1].replace('\n','').split(',')[1]
            decryptPassword = cipher.decrypt(password[1:])
            # Login処理
            request_url = base_url + '/LoginCheck'
            replacePass = decryptPassword.replace('\x0e', '')
            params = {'username' : name, 'password' : replacePass}
            print(params)
            r = requests.post(request_url, data=params)
            if r.status_code == 200:
                self.cookies = r.cookies.get_dict()
                if r.text == 'login miss':
                    return
                else:
                    # アナウンスファイルのDLを行う
                    self.downloadAnnounceTxt(self.ids['routeName'].value)


    # アナウンスファイルDL
    def  downloadAnnounceTxt(self, tripid):
        if tripid != -1:
            announce_feed_path = os.getcwd() +  r'/announce_feed'
            if  not os.path.exists(announce_feed_path):
                # アナウンスフィードファイルをDLする
                filename = 'announce_feed.zip'
                r = requests.post('http://FQCN/bus/userdata/userfolder/announce_feed.zip', stream=True)
                with open(filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                            f.flush()
                os.mkdir(announce_feed_path)
                # Zipファイル解凍
                zip = zipfile.ZipFile('announce_feed.zip')
                zip.extractall(announce_feed_path)
                zip.close()

            self._announceProvider = MySingleton().getAnnounceProviderCreate()
            triplist = self._announceProvider.getAnnounce_Trips().getAnnounce_Trips(tripid)
            filenamelist = []
            if triplist == None or len(triplist) == 0:
                # 音声無しでTrip開始
                self.startTrip()
                return

            # アナウンスが存在するとき
            for trip in triplist:
                filename = self._announceProvider.getAnnounces().getAnnounce(trip.getAnnounceId()).getFileName()
                filenamelist.append(filename)
            print(filenamelist)
            self.announcePlay(filenamelist[0])

            # 自身の更新日時を取得する
            file_path = os.getcwd()+ r'/announce_data'
            local_file = datetime.datetime.fromtimestamp(os.stat(file_path).st_mtime)

            # Server側の更新日取得
            res = requests.head('http://FQCN/bus/userdata/userfolder/announcedata')
            update_day = res.content
            server_file = datetime.datetime.strptime(update_day, '%a, %d %b %Y %H:%M:%S GMT' )

            # LocalとServerで比較
            if local_file < server_file:
	            for download_filename in filenamelist:
	                url = 'http://FQCN/bus/userdata/userfolder/announcedata/' + download_filename
	                r = requests.post(url, stream=True)
	                if r.status_code == 200:
	                    dl_dir = os.getcwd() +  r'\announce_data\USERDATA' + '\\' + str(self.ids['routeName'].value)  + '\\' + str(download_filename)
	                    with open(dl_dir, 'wb') as file:
	                        for chunk in r.iter_content(chunk_size=1024):
	                            file.write(chunk)
            self.startTrip()
            return


    # アナウンス処理
    def announcePlay(self, filename):
        announceDirctory = os.getcwd() +  r'/announce_data'
        if os.path.exists(voice_file):
            fr = open(voice_file, 'r')
            id = int(fr.readline())
            fr.close()
            # 選択した音声でディレクトリの分岐
            if id == 1:
                filePath = announceDirctory + r'/akane'
                self.announce = filePath + '/' + str(self.ids['routeName'].value) + '/' + filename
            elif id == 2:
                filePath = announceDirctory + r'/aoi'
                self.announce = filePath + '/' + str(self.ids['routeName'].value) + '/' + filename
            elif id == 3:
                filePath = announceDirctory + r'/man'
                self.announce = filePath + '/' + str(self.ids['routeName'].value) + '/' + filename.replace('wav', '3gp')
            # ファイルのロード
            pygame.mixer.music.load(self.announce)
            # 音量をセットする
            if os.path.exists(volume_data):
                fr = open(volume_data, 'r')
                pygame.mixer.music.set_volume(float(fr.readline()) / 100.0)
                fr.close()
            pygame.mixer.music.play()
            return
        return

    # アナウンスを止める(強制遷移時)
    def announceStop(self):
        pygame.mixer.music.stop()
        return



    # 表示の変更
    def changeNextStop(self, nextStop, departureTime):
        if self.ids['busStop'] == None or self.ids['departureTime'] == None:
            return
        self.ids['busStop'].text = 'Next : ' + nextStop
        self.ids['departureTime'].text = departureTime + '発'

    # バス停到着時
    def arriveAtStop(self, tripid, delay, stop):
        fr = open(voice_file, 'r')
        id = int(fr.readline())
        fr.close()
        self.ridenum = str(self.skipCounter)
        self.getoffnum = str(self.backCounter)

        # バス停の順番(sequence)取得
        stopsequence = stop.get_stopSequence()
        check =self._tripManager.checkPost()
        if check > int(stopsequence):
            return
        # 静的データをPOSTする
        self.post(delay, stop.get_stopId(), tripid, stopsequence, self.ridenum, self.getoffnum, 'arrival')



    # バス停出発時
    def departFromStop(self, tripid, delay, stop, nextstop):
        fr = open(voice_file, 'r')
        id = int(fr.readline())
        fr.close()
        # バス停の順番(sequence)を取得
        stopsequence = stop.get_stopSequence()
        check =self._tripManager.checkPost()
        if check > int(stopsequence):
            self.changeNextStop(nextstop.getName(), nextstop.get_departureTime())
            return
        # 静的データをPOSTする
        self.post(delay, stop.get_stopId(), tripid, stopsequence, self.ridenum, self.getoffnum, 'departure')
        if nextstop == None:
            # Trip終了
            self.finishTrip()
            return

        # VehiclePositionExporterにアップデート通知
        self._vehiclepositionexporter.updateBusState('onDeparture', nextstop.get_stopSequence())

        # 表示するバス停の変更
        self.changeNextStop(nextstop.getName(), nextstop.get_departureTime())

    # AddVehiclePosition
    def addVehicle(self, parameter, url):
        request_urls = url
        params = parameter
        try:
            r = requests.post(request_urls, data=params, cookies=self.cookies, timeout=10)
            if r.status_code != 200:
                print('error')
        except:
            return        

    # 乗車人数とかの静的データをPOSTする
    def post(self, delay, stopid, tripid, stopsequence, ridenum, getoffnum, message):
        # 車両ID取得
        vehicleNumber = self._vehiclenumber
        request_url = base_url + '/TripUpdate'
        params = {'delay' : str(delay), 'stopid' : str(stopid), 'tripid' : str(tripid), 'stopsequence' : str(stopsequence), 'ridenum' : str(ridenum), 'getoffnum' : str(getoffnum),  'vehicleid' : str(vehicleNumber),'message' : str(message)}
        try:
            r = requests.post(request_url, data=params, cookies=self.cookies, timeout=10)
            if r.status_code == 200:
                if message == None:
                    self.postFinishTripMessage('finish')
        except:
            return

    # Trip終了通知
    def postFinishTripMessage(self, messages):
        print('PostFinishTripMessage : ' + messages)
        request_url = base_url + '/TripUpdate'
        params = {'vehicleid' : self._vehiclenumber, 'message' : messages}
        try:
            r = requests.post(request_url, data=params, cookies=self.cookies, timeout=10)
            if r.status_code != 200:
                print('Upload error')
        except:
            return

    # Tripの終了処理
    def finishTrip(self):
        print('Trip Finish')
        _tripid = self.ids['routeName'].value
        lastData = self._tripManager.finish()
        print(lastData.items())
        self._vehiclepositionexporter.updateBusState(None, -1)
        self._vehiclepositionexporter.stop()
        self.setButtonsEnabledState()
        self._running = False
        self.evt.cancel()
        self.evt2.cancel()
        self.ids['picture'].source = ''
        self.ids['routeName'].text = ''
        self.ids['busStop'].text = ''
        self.ids['departureTime'].text = ''
        self.ids['distance'].text = ''
        # 最終データをPOSTする処理
        if not lastData:
            return
        else:
            self.post(lastData['delay'], lastData['stopid'], _tripid , lastData['stopsequence'], self.ridenum, self.getoffnum, 'finish')

    # Config処理
    def configButtonTouched(self):
        self.parent.current = 'config'



# RouteForm
class RouteFormContent(BoxLayout):

    # RouteNameをSpinnerに登録
    def setRouteName(self):
        # routeオブジェクトを取得
        self.items = MySingleton().getRouteDataProvider().getRoutes().getRoutes()
        routeName = self.ids['RouteSpinner'].values
        routeName.append('auto select')
        for route in self.items:
            routeName.append(route.getLongName())


    # ルートがspinnerから選択された時
    def selectRoute(self):
        # auto select以外はTrip Spinnerの更新
        if self.ids['RouteSpinner'].text != 'auto select':
            # 選択されたルートIDを持つTripリストを受け取る
            selectRoute = self.items[0]
            # 選択されたRouteIDを持つtripリストを受け取る
            trips = MySingleton().getRouteDataProvider().getTrips().getTripAreIncludeRoute(selectRoute.getId())

            if len(trips) == 0:
                return
            # Calendar情報,Stop_Time情報を取得
            calendar = MySingleton().getRouteDataProvider().getCalendar()
            stop_times = MySingleton().getRouteDataProvider().getStop_Times()

            # Dictオブジェクトを生成
            self.dicts = {}
            # 選択されたRouteIDを持つ旅程一覧からtripIDとservicIDを取得
            for trip in trips:
                tripid = trip.getId()
                serviceid = trip.getServiceId()
                # 運行日ならば
                if calendar.isTravelDay(serviceid):
                    # dictに旅程内最初の出発時刻(key)とvalue(対応tripID)を格納
                    self.dicts[stop_times.getEarliestStop_TimeAmongTrip(tripid).getDepartureTime()] = tripid

            # 現在時刻を取得
            currentTime = datetime.datetime.now().strftime('%H:%M:%S')
            # 今後運行されるやつだけ取得する
            triplist = self.getFutureOperation(currentTime, self.dicts)

            # ソート処理
            print(triplist)
            sortedTriplist = sorted(triplist)

            # TripSpinnerに時刻を格納する
            self.ids['TripSpinner'].values = ''
            tripTime = self.ids['TripSpinner'].values
            for item in sortedTriplist:
                tripTime.append(str(item))
            self.ids['TripSpinner'].disabled = False
        else:
            self.ids['TripSpinner'].disabled = True




    # 現在時刻以降のTripDictを作る
    def getFutureOperation(self, date, dicts):
        now = datetime.datetime.strptime(date, '%H:%M:%S')
        trip = []
        for entry in dicts:
                # 出発時刻をdatetimeに変換
                departure = datetime.datetime.strptime(entry, '%H:%M:%S')
                # 差分を計算
                delta = departure - now
                if '-1' in str(delta):
                    continue
                trip.append(entry)

        return trip


    # OKがタッチされた時の処理
    def okButtonTouch(self):
        print('You Select Ok Button')
        # auto selectならば直近の旅程を計算してTripIDを取得
        if self.ids['RouteSpinner'].text == 'auto select' or self.ids['TripSpinner'].text == '':
            currentTime = (datetime.datetime.now() - datetime.timedelta(minutes=15)).strftime('%H:%M:%S')
            # TripIDを取得する
            _tripid = self.getTripid(currentTime)
            # dialogの処理終わらせてScreenに返る
            self.ids['Finish'].disabled = False
            self.ids['tripid'].value = _tripid
        # auto select以外の処理
        else:
            _tripid = self.dicts[self.ids['TripSpinner'].text]
            self.ids['Finish'].disabled = False
            self.ids['tripid'].value = _tripid


    # 現在時刻からTripIDを求める
    def getTripid(self, date):
        trips = {}
        _provider = MySingleton().getRouteDataProvider()
        if _provider == None or _provider.getTrips() == None:
            return -1
        triplist = _provider.getTrips().getTripAreIncludeRoute(int(number))
        if triplist != None:
            if len(triplist) == 1:
                return triplist[0].getId()
            # 旅程リストをループさせてTripID取得
            for trip in triplist:
                tripid = trip.getId()
                if _provider.getStop_Times() == None:
                    continue
                dTime = _provider.getStop_Times().getFirstDepartureTimeOfTrip(tripid)
                if dTime != None:
                    trips[dTime] = tripid
        if len(trips) == 0:
            return -1
        print(trips)

        # dateとの差が一番小さいものを走査
        minDifference = -1
        now = datetime.datetime.strptime(date, '%H:%M:%S')
        for entry in trips:
            departure = datetime.datetime.strptime(entry, '%H:%M:%S')
            delta = departure - now
            difference = delta.seconds
            if minDifference == -1 or difference < minDifference:
                minDifference = difference
                result = trips[entry]
        return result



# Config画面
class ConfigScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        pygame.mixer.init()
        if os.path.exists(voice_file):
            self.sampleVoiceDirctory = os.getcwd() + r'/Voicedata/sample'
            fr = open(voice_file, 'r')
            mode = int(fr.readline())
            # Akane
            if mode == 1:
                self.testSound = self.sampleVoiceDirctory+ r'/sample_akane.wav'
            # Aoi
            elif mode == 2:
                self.testSound = self.sampleVoiceDirctory+ r'/sample_aoi.wav'
            # Man
            else:
                self.testSound = self.sampleVoiceDirctory+ r'/sample_man.3gp'
            fr.close()
            # Volume情報が格納されたファイルがあるか確認
            if os.path.exists(volume_data):
                fr = open(volume_data, 'r')
                # self.testSound.volume = float(fr.readline()) / 100.0
                fr.close()
            else:
                fw = open(volume_data, 'w')
                fw.write('0')
                fw.close()
                self.testSound.volume = 0

    # Sample押下時の処理
    def sampleButtonTouched(self):
        if  self.ids['sample'].text == 'Sample':
            pygame.mixer.music.load(self.testSound)
            pygame.mixer.music.set_volume(self.ids['volume_slider'].value / 100.0)
            pygame.mixer.music.play(1)
            self.ids['sample'].text = 'Stop'
        else:
            pygame.mixer.music.stop()
            self.ids['sample'].text = 'Sample'

    # アナウンスに使うキャラクター選択時
    def voiceCharacterTouched(self):
        filePath =  os.getcwd() + r'/Voicedata/change'
        # 選択されたキャラクター名を取得する
        selectedCharacter = self.ids['voice'].text
        self.ids['sample'].text = 'Sample'
        # 保存ファイルなかったら作る
        fw = open(voice_file, 'w')
        if selectedCharacter == 'Akane':
            filePath += r'/change_akane.wav'
            fw.write('1')
            self.testSound = self.sampleVoiceDirctory+ r'/sample_akane.wav'
        elif selectedCharacter == 'Aoi':
            filePath += r'/change_aoi.wav'
            fw.write('2')
            self.testSound = self.sampleVoiceDirctory+ r'/sample_aoi.wav'
        elif selectedCharacter == 'Man':
            filePath += r'/change_man.wav'
            fw.write('3')
            self.testSound = self.sampleVoiceDirctory+ r'/sample_man.3gp'
        fw.close()
        # キャラクターが変わったことを通知
        pygame.mixer.music.load(filePath)
        pygame.mixer.music.set_volume(self.ids['volume_slider'].value / 100.0)
        pygame.mixer.music.play()


    # スライダーの音処理
    def changeVolume(self):
        pygame.mixer.music.set_volume(self.ids['volume_slider'].value / 100.0)

    # Registration押された時の処理
    def RegisterButtonTouched(self):
        content = RegistFormContent()
        content.setLabel(str(int(self.ids['volume_slider'].value)),self.ids['voice'].text)
        self.registform = Popup(title='Registration Check',content=content, size_hint=(0.5, 0.5), pos_hint={'center_x':0.5, 'top':0.8},auto_dismiss=False)
        content.ids['Cancel'].bind(on_press=self.registform.dismiss)
        content.ids['OK'].bind(on_press=self.registform.dismiss)
        self.registform.open()

    # 戻るボタン押下時の処理
    def backButtonTouched(self):
        pygame.mixer.music.stop()
        self.ids['sample'].text = 'Sample'
        self.parent.current = 'main'


class MySlider(Slider):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        fr = open(volume_data, "r")
        self.value = fr.readline()

# RegistFormの中身
class RegistFormContent(BoxLayout):
    # 登録する情報をLabelに書き込む
    def setLabel(self, volume, voice):
        self.vol = volume
        self.ids['volume'].text += volume
        self.ids['voice'].text += voice
    # ファイルに音量を保存
    def okButtonTouched(self):
        fw = open(volume_data, "w")
        fw.write(self.vol)
        fw.close()

class FinishFormContent(BoxLayout):
    # アプリを落とす
    def yesButtonTouched(self):
        App().get_running_app().stop()
        os.system('./shut.sh')

class BusApplicationApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(ConfigScreen(name='config'))
        return sm

BusApplicationApp().run()
