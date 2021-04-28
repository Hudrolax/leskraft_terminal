from sys import platform
import subprocess
if platform == "linux" or platform == "linux2":
    import cups
else:
    from PDFNetPython3.PDFNetPython import *
import os
if __name__ != '__main__':
    from env import *
import logging
import requests
from time import sleep


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
    file_path = f'./temp/{link}.pdf'
    content = _get_http_data_static(GET_PRINT_FORM_ROUTE, f'&document_id={link}')
    try:
        with open(file_path, 'wb') as f:
            f.write(content)
        print_file(file_path)
    except:
        logging.critical(f'Ошибка записи файла {file_path}')

def print_file(path):
    if os.path.exists(path):
        if platform == "linux" or platform == "linux2" or platform == "darwin":
            # conn = cups.Connection()
            # conn.printFile(PRINTER_NAME, path, "", {})
            result = subprocess.run(["lp", "-d", PRINTER_NAME, path])
        else:
            win32_print(path)
        sleep(3)
        # os.remove(path)
        logging.info(f'Файл {path} отправлен на печать и удален.')
    else:
        logging.error(f'Не найден файл для печати {path}')

def find_printer_by_name(name):
    try:
        if platform == "linux" or platform == "linux2":
            conn = cups.Connection()
            printers = conn.getPrinters()
            for printer in printers:
                if str(printer).find(name) > -1:
                    return True
    except Exception as ex:
        logging.error(ex)
        return False
    return False

def win32_print(path):
    PDFNet.Initialize()

    doc = PDFDoc(path)
    doc.InitSecurityHandler()

    # Set our PrinterMode options
    printerMode = PrinterMode()
    printerMode.SetCollation(True)
    printerMode.SetCopyCount(1)
    printerMode.SetDPI(100)  # regardless of ordering, an explicit DPI setting overrides the OutputQuality setting
    printerMode.SetDuplexing(PrinterMode.e_Duplex_Auto)

    # If the XPS print path is being used, then the printer spooler file will
    # ignore the grayscale option and be in full color
    printerMode.SetOutputColor(PrinterMode.e_OutputColor_Grayscale)
    printerMode.SetOutputQuality(PrinterMode.e_OutputQuality_Medium)
    # printerMode.SetNUp(2,1)
    # printerMode.SetScaleType(PrinterMode.e_ScaleType_FitToOutPage)

    # Print the PDF document to the default printer, using "tiger.pdf" as the document
    # name, send the file to the printer not to an output file, print all pages, set the printerMode
    # and don't provide a cancel flag.
    Print.StartPrintJob(doc, "", doc.GetFileName(), "", None, printerMode, None)

if __name__ == '__main__':
    if platform == "linux" or platform == "linux2":
        conn = cups.Connection()
        printers = conn.getPrinters()
        print('Доступные принтеры:')
        for printer in printers:
            print(printer)
    else:
        print('Модуль pycups не доступен на данной OS')
