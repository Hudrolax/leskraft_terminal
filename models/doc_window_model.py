from utility.logger_super import LoggerSuper
import logging
from env import SERVER, BASE_NAME, GET_TASK_ROUTE, AUTH_BASIC, FINISH_TASK_ROUTE
from config import CONNECTION_TIMEOUT
import requests

class DocumentForm_model(LoggerSuper):
    logger = logging.getLogger('doc_form_model')
    def __init__(self, db, doc_link, main_window):
        self.main_window = main_window
        self.db = db
        self.doc_link = doc_link
        self.team = None

    def doc(self):
        return self.db.get_doc(self.doc_link)

    def finish_task(self):
        self.logger.info(f'конец работы с документом {self.doc()}')
        try:
            url = f'http://{SERVER}/{BASE_NAME}{FINISH_TASK_ROUTE}'
            headers = {'Content-type': 'application/json',  # Определение типа данных
                       'Accept': 'text/plain',
                       'Authorization': AUTH_BASIC}
            body = {"doc_num": self.doc().num,
                    "doc_date": self.doc().return_date_1c_str()}
            answer = requests.post(url=url, json=body, headers=headers, timeout=CONNECTION_TIMEOUT).content.decode()
            if answer != 'ok':
                self.logger.error(answer)
                return False
            return True
        except (
                requests.exceptions.ConnectionError or requests.exceptions.ConnectTimeout or requests.exceptions.BaseHTTPError) as e:
            self.logger.critical(e)
            return False
        except Exception as e:
            self.logger.critical(e)
            return False

    def get_task(self):
        self.logger.info(f'начало работы с документом {self.doc()}')
        try:
            url = f'http://{SERVER}/{BASE_NAME}{GET_TASK_ROUTE}'
            headers = {'Content-type': 'application/json',  # Определение типа данных
                        'Accept': 'text/plain',
                        'Authorization': AUTH_BASIC}
            body = {"doc_num":self.doc().num, "doc_date":self.doc().return_date_1c_str(), "team_number":self.team.num}
            answer = requests.post(url=url, json=body, headers=headers, timeout=CONNECTION_TIMEOUT).content.decode()
            if answer != 'ok':
                self.logger.error(answer)
                return False
            return True
        except (requests.exceptions.ConnectionError or requests.exceptions.ConnectTimeout or requests.exceptions.BaseHTTPError) as e:
            self.logger.critical(e)
            return False
        except Exception as e:
            self.logger.critical(e)
            return False