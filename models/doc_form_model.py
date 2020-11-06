from utility.logger_super import LoggerSuper
import logging
from env import *
import requests

class DocumentForm_model(LoggerSuper):
    logger = logging.getLogger('doc_form_model')
    def __init__(self, controller, db, doc):
        self.controller = controller
        self.db = db
        self.doc = doc

    def start_work_with_document(self):
        self.logger.info(f'начало работы с документом {self.doc}')
        return self._get_task()

    def stop_work_with_document(self):
        self.logger.info(f'конец работы с документом {self.doc}')
        return True

    def _get_task(self):
        _TIMEOUT = 10
        try:
            url = f'http://{SERVER}{GET_TASK_ROUTE}'
            headers = {'Content-type': 'application/json',  # Определение типа данных
                        'Accept': 'text/plain',
                        'Authorization': AUTH_BASIC}
            body = {"doc_num":self.doc.num, "doc_date":self.doc.return_date_1c_str(), "team_number":1}
            answer = requests.post(url=url, json=body, headers=headers, timeout=_TIMEOUT).content.decode()
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