from utility.logger_super import LoggerSuper
import logging
from env import SERVER, BASE_NAME, GET_TASK_ROUTE, AUTH_BASIC
from config import CONNECTION_TIMEOUT
import requests

class DocumentForm_model(LoggerSuper):
    logger = logging.getLogger('doc_form_model')
    def __init__(self, controller, db, doc_link):
        self.controller = controller
        self.db = db
        self.doc_link = doc_link
        self.team = None

    def start_work_with_document(self):
        self.logger.info(f'начало работы с документом {self.db.get_doc(self.doc_link)}')
        return self._get_task()

    def stop_work_with_document(self):
        self.logger.info(f'конец работы с документом {self.db.get_doc(self.doc_link)}')
        return True

    def _get_task(self):
        try:
            url = f'http://{SERVER}/{BASE_NAME}{GET_TASK_ROUTE}'
            headers = {'Content-type': 'application/json',  # Определение типа данных
                        'Accept': 'text/plain',
                        'Authorization': AUTH_BASIC}
            body = {"doc_num":self.db.get_doc(self.doc_link).num, "doc_date":self.db.get_doc(self.doc_link).return_date_1c_str(), "team_number":1}
            answer = requests.post(url=url, json=body, headers=headers, timeout=CONNECTION_TIMEOUT).content.decode()
            if answer != 'ok':
                self.logger.error(answer)
            return answer
        except (requests.exceptions.ConnectionError or requests.exceptions.ConnectTimeout or requests.exceptions.BaseHTTPError) as e:
            self.logger.critical(e)
            return str(e)
        except Exception as e:
            self.logger.critical(e)
            return str(e)

    # def cancel_string(self, str_num, cancelled, reason):
    #     #     print(f'док {self.doc} строка {str_num} {cancelled} {reason}')
    #     #     return True