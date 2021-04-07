import requests
from time import sleep
import json
from utility.logger_super import LoggerSuper
from models.data_base import DB
from env import *
import logging
from utility.threaded_class import Threaded_class
from views.error_message_window import Error_window
from views.main_window import MainWindow
from config import *
import threading


class MainModel(Threaded_class, LoggerSuper):

    logger = logging.getLogger('MainModel')
    def __init__(self):
        self._update = False
        self._observers = []  # список наблюдателей
        self.db = DB()
        self._getdata_thread = threading.Thread(target=self._threaded_get_data, args=(), daemon=False)
        self._getdata_thread.start()
        self._online = False

    def get_online_status(self):
        return self._online

    def update(self):
        if AUTO_UPDATE:
            self._update = True
            while self._update:
                sleep(0.1)
            return True
        else:
            return False

    def _threaded_get_data(self):
        while self.working:
            if AUTO_UPDATE:
                self.get_docs()
                self.get_employees()
                self.get_teams()
                self.get_employee_connections()
                self.interrupted_sleep(AUTO_UPDATE_TIME)

    def interrupted_sleep(self, pause):
        for k in range(10, pause*10):
            if self.working and not self._update:
                sleep(0.1)
            elif self._update:
                self._update = False
                return
            else:
                return

    @staticmethod
    def get_http_data_static(route, parameters=''):
        try:
            answer = requests.get(f'http://{SERVER}/{BASE_NAME}{route}?api_key={API_KEY}{parameters}',
                                   auth=(USER, PASSWORD), timeout=3)
            if answer.status_code == 200:
                return answer.content
            else:
                MainModel.logger.error(f'http_get {route} status code {answer.status_code}:{answer.content.decode()}')
                return None
        except Exception as ex:
            try:
                answer =  requests.get(f'http://{SERVER2}/{BASE_NAME}{route}?api_key={API_KEY}{parameters}',
                                       auth=(USER, PASSWORD), timeout=3)
                if answer.status_code == 200:
                    return answer.content
                else:
                    MainModel.logger.error(f'http_get {route} status code {answer.status_code}:{answer.content.decode()}')
                    return None
            except:
                return None

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
            self._online = True
        except Exception as e:
            self._online = False
            self.logger.error(e)
            sleep(5)

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
    model.get_employees()
    model.get_teams()
    Threaded_class.stop()
