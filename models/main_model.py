import requests
from time import sleep
import json
from utility.logger_super import LoggerSuper
from models.data_base import DB
from env import *
import logging
from utility.threaded_class import Threaded_class
from views.error_message import Error_window
from views.main_window import MainWindow
from config import *
import threading


class MainModel(Threaded_class, LoggerSuper):
    _USER = USER
    _PASSWORD = PASSWORD
    _SERVER = SERVER
    _GET_DOCS_ROUTE = GET_DOCS_ROUTE
    _API_KEY = API_KEY

    logger = logging.getLogger('MainModel')
    def __init__(self):
        self._observers = []  # список наблюдателей
        self.db = DB()
        self._getdata_thread = threading.Thread(target=self._threaded_get_data, args=(), daemon=False)
        self._getdata_thread.start()

    def _threaded_get_data(self):
        while self.working:
            if AUTO_UPDATE:
                self.get_docs()
                self.interrupted_sleep(AUTO_UPDATE_TIME)

    def get_docs(self):
        try:
            content = requests.get(f'http://{self._SERVER}{self._GET_DOCS_ROUTE}?api_key={self._API_KEY}', auth=(self._USER, self._PASSWORD)).content.decode()
            decoded_json = json.loads(content)
            self.logger.debug(f'Get JSON: {decoded_json}')
            json_docs = decoded_json.get('docs')
            self.db.clear_db()
            for json_doc in json_docs:
                _link = json_doc.get('link')
                _num = json_doc.get('num')
                _date = json_doc.get('date')
                _date_sending= json_doc.get('date_sending')
                _type = json_doc.get('type')
                _storage = json_doc.get('storage')
                _doc_status = json_doc.get('doc_status')
                _execute_to = json_doc.get('execute_to')
                _team_leader = json_doc.get('team_leader')
                _team_number = json_doc.get('team_number')
                _start_time = json_doc.get('start_time')
                _end_time = json_doc.get('end_time')
                _destination = json_doc.get('destination')
                _autos_number = json_doc.get('autos_number')
                self.db.add_document(_link, _num, _date, _date_sending, _type, _storage, _doc_status, _execute_to, _team_leader, _team_number, _start_time, _end_time, _destination, _autos_number)

                _table = json_doc.get('table')
                for json_str in _table:
                    _num = json_str.get('nomenclature_code')
                    _nomenclature_code = json_str.get('nomenclature_code')
                    _nomenclature_name = json_str.get('nomenclature_name')
                    self.db.add_nomenclature(_nomenclature_code, _nomenclature_name)
                    _amount = json_str.get('amount')
                    _status = json_str.get('status')
                    _cancelled = json_str.get('cancelled')
                    _reason_for_cancellation = json_str.get('reason_for_cancellation')
                    self.db.add_doc_table_string(_link, _num, _nomenclature_code, _amount, _status, _cancelled, _reason_for_cancellation)
        except (requests.exceptions.ConnectionError or requests.exceptions.ConnectTimeout or requests.exceptions.BaseHTTPError) as e:
            self.logger.critical(e)
            sleep(5)
        except Exception as e:
            self.logger.critical(e)
            sleep(5)
            # if e.__class__.__name__ == "ProgrammingError":
            #     self.show_error_message('Ошибка базы данных', True)
            # else:
            #     self.show_error_message('Ошибка парсинга входящих данных', False)

    def show_error_message(self, message, exit):
        for observer in self._observers:
            if isinstance(observer, MainWindow):
                sleep(1)
                Error_window(observer, message, exit)
                return

if __name__ == '__main__':
    model = MainModel()
    model.get_docs()
    for doc in model.db.documents:
        model.db.get_fuul_doc_description(doc.link)
    Threaded_class.stop()
