# -*- coding: utf-8 -*-
import os
import datetime

class CalendarFeed:

    def __init__(self, userdirectorypath):
        self.calendars = []
        self.FILE_NAME = 'calendar.txt'
        self.FEED_DIRECTORY = 'google_transit_feed'
        self.state = False

        filePath = userdirectorypath+'/'+self.FEED_DIRECTORY+'/'+self.FILE_NAME
        # calendar.txtが存在
        if os.path.exists(filePath):
            fileRead =open(filePath, 'r',  encoding="utf-8")
            readData = fileRead.readlines()

            for line in readData:
                if self.state == False:
                    self.state = True
                    continue
                token = line.split(',')

                # サービス利用日をまとめてList
                calendarlist = []
                for i in range(7):
                    calendarlist.append(int(token[i+1]))
                
                self.addCalendar(int(token[0]), calendarlist, token[8], token[9])

            fileRead.close()


    # 引数のserviceIdを持つcalendarを返す
    def hasId(self, serviceid):
        if self.calendars == None:
            print('calendars is null')
            return None

        for calendar in self.calendars:
            if calendar.getServiceId() == serviceid:
                return calendar
        return None

    def isTravelDay(self, serviceid):
        calendar = self.hasId(serviceid)
        if calendar == None:
            return False
        return calendar.isTravelDay()



    # calendarsリストを返す
    def getCalendar(self):
        return self.calendars


    # CalendarクラスのオブジェクトをListに格納
    def addCalendar(self, serviceid, weekcalendar, startdate, enddate):
        if self.calendars == None:
            print('Error')
            return
        self.calendars.append(CalendarFeed.Calendar(serviceid, weekcalendar, startdate, enddate))


    # Calendar.txtのデータ構造を表したクラス
    class Calendar:
        def __init__(self, serviceid, weekcalendar, startdate, enddate):
            self._serviceid = serviceid
            self._weekcalendar = weekcalendar
            self._startdate = startdate
            self._enddate = enddate

        # 本日運行日かどうか返す trueは運行日
        def isTravelDay(self):
            # 現在の日付
            today = datetime.date.today()

            # 文字列からdate型に変換
            start = self._startdate
            startdatetime = datetime.datetime.strptime(start, '%Y%m%d')
            startdate = datetime.date(startdatetime.year, startdatetime.month, startdatetime.day)

            end = self._enddate
            # 改行文字を取り除く
            end = end.replace('\n', '')
            enddatetime = datetime.datetime.strptime(end, '%Y%m%d')
            enddate = datetime.date(enddatetime.year, enddatetime.month, enddatetime.day)

            if today >= startdate and today <= enddate and self._weekcalendar[datetime.date.today().weekday()] == 1:
                return True
            return False

            
               
        def getServiceId(self):
            return self._serviceid

        def getCalendar(self):
            return self._weekcalendar

        def getStartDate(self):
            return self._startdate

        def getEndDate(self):
            return self._enddate
