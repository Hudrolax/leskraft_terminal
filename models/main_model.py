import requests
from time import sleep
import json
from datetime import datetime
from utility.logger_super import LoggerSuper
from models.decument import Document
from env import *
import logging


class MainModel(LoggerSuper):
    _USER = USER
    _PASSWORD = PASSWORD
    _SERVER = SERVER
    _GET_DOCS_ROUTE = GET_DOCS_ROUTE
    _API_KEY = API_KEY

    logger = logging.getLogger('MainModel')
    def __init__(self):
        self._observers = []  # список наблюдателей
        self.docs = []

    def get_docs(self):
        self.docs.clear()
        try:
            content = requests.get(f'http://{self._SERVER}{self._GET_DOCS_ROUTE}?api_key={self._API_KEY}', auth=(self._USER, self._PASSWORD)).content.decode()
            decoded_json = json.loads(content)
            self.logger.debug(f'Get JSON: {decoded_json}')
            json_docs = decoded_json.get('docs')
            for json_doc in json_docs:
                _num = json_doc.get('num')
                _date = json_doc.get('date')
                _type = json_doc.get('type')
                _storage = json_doc.get('storage')
                _doc_status = json_doc.get('doc_status')
                doc = Document(_num, _date, _type, _storage, _doc_status)
                self.docs.append(doc)
        except requests.exceptions.ConnectionError or requests.exceptions.ConnectTimeout or requests.exceptions.BaseHTTPError:
            print('Ошибка подключения к серверу')
            sleep(5)
        self.notify_observers()

    def add_observer(self, observer):
        self._observers.append(observer)

    def remove_observer(self, observer):
        self._observers.remove(observer)

    def notify_observers(self):
        for x in self._observers:
            x.model_is_changed()

if __name__ == '__main__':
    model = MainModel()
    model.get_docs()
    for doc in model.docs:
        print(doc)