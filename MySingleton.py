# -*- coding: utf-8 -*-
import RouteDataProvider
import AnnounceProvider
import os

class MySingleton:
    _instance = None        

    def __new__(cls, *args, **kwargs):
        if not cls._instance:       
            cls._instance = super(MySingleton, cls).__new__(cls, *args, **kwargs)
            # ここに初期化処理を記述する(cls.はselfで参照可能)
            print('create singleton')
            cls.state = False
            cls._apiBaseUrl = 'http://FQCN/BusApplicationServerSide/'
            cls._userDirUrl = 'http://FQCN/bus/userdata/'
            cls._announceDirctoryName = 'announce'
            cls._annouceDataDirectoryName = 'annoucedata'
            cls._errorDialogTitle = 'Error'
        return cls._instance        

    def getRequestQueue(self):
        pass

    def get_errorDialogTitle(self):
        return self._errorDialogTitle
    
    # RouteDataProviderを生成
    def getRouteDataProviderCreate(self):
        self._provider = RouteDataProvider.RouteDataProvider(os.getcwd())

        return self._provider

    # Createで生成した_providerを返す(StaticFeedFileの情報を保持)
    def getRouteDataProvider(self):
        return self._provider


    # AnnounceProvider生成
    def getAnnounceProviderCreate(self):
        self._announceProvider = AnnounceProvider.AnnounceProvider(os.getcwd())

        return self._announceProvider


    def getAnnounceProvider(self):
        return self._announceProvider

    def getApiBaseUrl(self):
        return self._apiBaseUrl

    def get_userDirUrl(self):
        return self._userDirUrl

    def get_annunceDirectoryName(self):
        return self._announceDirctoryName

    def get_annunceDataDirectoryName(self):
        return self._annouceDataDirectoryName




    

    

    