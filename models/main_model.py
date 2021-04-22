import requests
import json
from utility.logger_super import LoggerSuper
from models.data_base import DB
from env import *
import logging
from config import AUTO_UPDATE_TIME, CONNECTION_TIMEOUT
from PyQt5 import QtCore

# класс для заполнения БД в отдельном потоке
class DBUpdateHandler(QtCore.QObject, LoggerSuper):
    update_GUI_signal = QtCore.pyqtSignal(object)
    logger = logging.getLogger('DBUpdateHandler')
    def __init__(self):
        super().__init__()
        self.db = None

    # метод, который будет выполнять алгоритм в другом потоке
    def run(self):
        while True:
            # print(f'начало запроса БД')
            self.db = DB()  # База, создаваемая для получения и передачи в основную базу
            self.get_docs()
            self.get_employees()
            self.get_teams()
            self.get_employee_connections()
            # print(f'конец запроса БД')
            self.update_GUI_signal.emit(self.db)
            QtCore.QThread.sleep(AUTO_UPDATE_TIME)

    def _get_docs(self, decoded_json):
        json_docs = decoded_json.get('docs')
        self.db.clear_docs()
        for json_doc in json_docs:
            args = []
            args.append(json_doc.get('link'))
            args.append(json_doc.get('num'))
            args.append(json_doc.get('date'))
            args.append(json_doc.get('date_sending'))
            args.append(json_doc.get('type'))
            args.append(json_doc.get('storage'))
            args.append(json_doc.get('doc_status'))
            args.append(json_doc.get('execute_to'))
            args.append(json_doc.get('team_leader'))
            args.append(json_doc.get('team_number'))
            args.append(json_doc.get('team_date'))
            args.append(json_doc.get('start_time'))
            args.append(json_doc.get('end_time'))
            args.append(json_doc.get('destination'))
            args.append(json_doc.get('autos_number'))
            self.db.add_document(*args)
            _table = json_doc.get('table')
            for json_str in _table:
                args_str = []
                args_str.append(args[0])
                args_str.append(json_str.get('num'))

                _nomenclature_code = json_str.get('nomenclature_code')
                _nomenclature_name = json_str.get('nomenclature_name')
                self.db.add_nomenclature(_nomenclature_code, _nomenclature_name)

                args_str.append(_nomenclature_code)
                args_str.append(json_str.get('amount'))
                args_str.append(json_str.get('status'))
                args_str.append(json_str.get('adress_shelf'))
                args_str.append(json_str.get('adress_floor'))
                args_str.append(json_str.get('cancelled'))
                args_str.append(json_str.get('reason_for_cancellation'))
                self.db.add_doc_table_string(*args_str)

    def _get_employees(self, decoded_json):
        json_records = decoded_json.get('employees')
        self.db.clear_employees()
        for json_rec in json_records:
            args = []
            args.append(json_rec.get('name'))
            args.append(json_rec.get('card_number'))
            args.append(json_rec.get('role'))
            self.db.add_employee(*args)

    def _get_teams(self, decoded_json):
        json_records = decoded_json.get('teams')
        self.db.clear_teams()
        for json_rec in json_records:
            args = []
            args.append(json_rec.get('num'))
            args.append(json_rec.get('date'))
            args.append(json_rec.get('team_leader'))
            args.append(json_rec.get('terminal_api'))
            self.db.add_team(*args)

    def _get_employee_connections(self, decoded_json):
        json_records = decoded_json.get('employee_connections')
        self.db.clear_employee_connections()
        for json_rec in json_records:
            args = []
            args.append(json_rec.get('card_number'))
            args.append(json_rec.get('team_num'))
            args.append(json_rec.get('team_date'))
            self.db.add_employee_connection(*args)

    def get_docs(self):
        self.get_http_data(GET_DOCS_ROUTE, self._get_docs)

    def get_employees(self):
        self.get_http_data(GET_EMPLOYEES_ROUTE, self._get_employees)

    def get_teams(self):
        self.get_http_data(GET_TEAMS_ROUTE, self._get_teams)

    def get_employee_connections(self):
        self.get_http_data(GET_EMPLOYEE_CONNECTIONS_ROUTE, self._get_employee_connections)

    def get_http_data(self, route, func):
        try:
            content = self.get_http_data_static(route)
            if content is not None:
                content = content.decode()
            else:
                raise Exception('exaption content is None')

            decoded_json = json.loads(content)
            self.logger.debug(f'Get JSON: {decoded_json}')
            func(decoded_json)
            self.db.online = True
        except Exception as e:
            self.db.online = False
            self.logger.error(e)
            QtCore.QThread.msleep(3000)

    @staticmethod
    def get_http_data_static(route, parameters=''):
        try:
            answer = requests.get(f'http://{SERVER}/{BASE_NAME}{route}?api_key={API_KEY}{parameters}',
                                  auth=(USER, PASSWORD), timeout=CONNECTION_TIMEOUT)
            if answer.status_code == 200:
                return answer.content
            else:
                MainModel.logger.error(f'http_get {route} status code {answer.status_code}:{answer.content.decode()}')
                return None
        except Exception as ex:
            try:
                answer = requests.get(f'http://{SERVER2}/{BASE_NAME}{route}?api_key={API_KEY}{parameters}',
                                      auth=(USER, PASSWORD), timeout=CONNECTION_TIMEOUT)
                if answer.status_code == 200:
                    return answer.content
                else:
                    MainModel.logger.error(
                        f'http_get {route} status code {answer.status_code}:{answer.content.decode()}')
                    return None
            except:
                return None

class MainModel(LoggerSuper):
    logger = logging.getLogger('MainModel')
    def __init__(self, main_window):
        self.main_window = main_window
        self.db = DB() # основная база данных

        # поток запроса данных из 1С
        self.db_update_thread = QtCore.QThread()
        self.db_update_handler = DBUpdateHandler()
        self.db_update_handler.moveToThread(self.db_update_thread)
        self.db_update_handler.update_GUI_signal.connect(self.slot_update_UI)
        self.db_update_thread.started.connect(self.db_update_handler.run)
        self.db_update_thread.start()

    def slot_update_UI(self, db):
        self.db = db # записываем заполненный объект БД в объект БД модели