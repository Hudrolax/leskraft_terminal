from sys import platform
if platform == "linux" or platform == "linux2":
    import cups
import os
if __name__ == '__main__':
    from .env import *
else:
    from env import *
import logging
import requests


def _get_http_data_static(route, parameters=''):
    try:
        answer = requests.get(f'http://{SERVER}/{BASE_NAME}{route}?api_key={API_KEY}{parameters}',
                              auth=(USER, PASSWORD))
        if answer.status_code == 200:
            return answer.content
        else:
            MainModel.logger.error(f'http_get {route} status code {answer.status_code}:{answer.content.decode()}')
            return None
    except Exception as e:
        try:
            answer = requests.get(f'http://{SERVER2}/{BASE_NAME}{route}?api_key={API_KEY}{parameters}',
                                  auth=(USER, PASSWORD))
            if answer.status_code == 200:
                return answer.content
            else:
                MainModel.logger.error(f'http_get {route} status code {answer.status_code}:{answer.content.decode()}')
                return None
        except:
            return None

def get_pdf_and_print(link):
    if platform == "linux" or platform == "linux2" or platform == "darwin":
        file_path = '.'
    else:
        file_path = ''
    file_path = file_path + f'./temp/{link}.pdf'
    content = _get_http_data_static(GET_PRINT_FORM_ROUTE, f'&document_id={link}')
    try:
        with open(file_path, 'wb') as f:
            f.write(content)
        return print_file(file_path)
    except:
        error_msg = f'Ошибка записи файла {file_path}'
        logging.critical(error_msg)
        return error_msg

def print_file(path):
    if platform == "linux" or platform == "linux2" or platform == "darwin":
        if os.path.exists(path):
            conn = cups.Connection()
            conn.printFile(PRINTER_NAME, path, "", {})
            os.remove(path)
            return ''
        else:
            return f'Не найден файл для печати {path}'
    else:
        return 'Печать на вашей OS невозможна.'

if __name__ == '__main__':
    if platform == "linux" or platform == "linux2":
        conn = cups.Connection()
        printers = conn.getPrinters()
        print('Доступные принтеры:')
        for printer in printers:
            print(printer)
    else:
        print('Модуль pycups не доступен на данной OS')
