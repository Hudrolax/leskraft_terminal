from datetime import datetime
from utility.util import value_filled

class DocumentTableString:
    def __init__(self, doc_link, num, nomenclature_code, amount, status, cancelled, reason_for_cancellation):
        """
        Класс описывает строку документа
        :param doc_link: тип строка. Ссылка на документ.
        :param num: тип число целое. Номер строки.
        :param nomenclature_code: тип строка. Код номенклатуры.
        :param amount: тип число float. Количество.
        :param status: тип строка. Статус строки (НаИсполнение, ВРаботе, Выполнено)
        :param cancelled: тип булево. Признак отмены строки.
        :param reason_for_cancellation: тип строка. Причина отмены.
        """
        if not isinstance(doc_link, str):
            raise TypeError(f'DocumentTableString init: doc_link must be str type!')
        self.doc_link = doc_link
        self.num = num
        self.nomenclature_code = nomenclature_code
        self.amount = amount
        self.status = status
        self.cancelled = cancelled
        self.reason_for_cancellation = reason_for_cancellation


class Document:
    DATE_FORMAT = '%d.%m.%Y %H:%M:%S'
    DATE_FORMAT_SQL = '%Y-%m-%d %H:%M:%S'

    def __init__(self, link, num, date, date_sending, type, storage, status, execute_to, team_leader, team_number, start_time, end_time, destination, autos_number, table):
        """
        :param link: тип строка. Цифровое представление ссылки на документ (как в QR коде)
        :param num: тип строка. Номер документа.
        :param date: тип дата. Дата документа.
        :param date_sending: тип дата. Дата отправки на терминал.
        :param type: тип строка. Тип (вид) документа (Отгрузка, Сборка, Приемка, ВнутреннееПеремещение)
        :param storage: тип Строка. Склад.
        :param status: тип строка. Статус документа (НаИсполнение, ВРаботе, Выполнено)
        :param execute_to: тип дата. Дата, до которой задание должно быть выполнено.
        :param team_leader: тип строка. ФИО кладовщика, чья команда взяла задание.
        :param team_number: тип строка. Номер документа ЛК_ФормированиеСкладскойБригады
        :param start_time: тип дата. Дата начала исполнения задания.
        :param end_time: тип дата. Дата окончания исполнения задания.
        :param destination: тип строка. Куда грузить (Клиент, Склад, Место хранения)
        :param autos_number: тип строка. Номер машины, куда грузить.
        :param table: тип DocumentTableString. табличная часть документа.
        """
        self._link = link
        self.num = num
        self._date = self._date_setter(date)
        self._date_sending = self._date_setter(date_sending)
        self.type = type
        self.storage = storage
        self.status = status
        self._execute_to = self._date_setter(execute_to)
        self.team_leader = team_leader
        self.team_number = team_number
        self._start_time = self._date_setter(start_time)
        self._end_time = self._date_setter(end_time)
        self.destination = destination
        self.autos_number = autos_number
        self.table = None

    def get_num_str(self):
        try:
            return str(int(self.num))
        except:
            return self.num

    def _date_setter(self, date):
        if isinstance(date, datetime):
            return date
        else:
            try:
                return datetime.strptime(date, self.DATE_FORMAT)
            except ValueError:
                try:
                    return datetime.strptime(date, self.DATE_FORMAT_SQL)
                except:
                    raise ValueError(f'Document: неверный формат даты. Получена дата формата {date}, тогда как ожидается {self.DATE_FORMAT}')

    def return_date_str(self, date):
        if value_filled(date):
            return datetime.strftime(date, self.DATE_FORMAT)
        else:
            return ""

    @property
    def end_time(self):
        return self._end_time

    @end_time.setter
    def end_time(self, val):
        self._end_time = self._date_setter(val)

    def get_end_time_str(self):
        return self.return_date_str(self._end_time)

    @property
    def start_time(self):
        return self._start_time

    @start_time.setter
    def start_time(self, val):
        self._start_time = self._date_setter(val)

    def get_start_time_str(self):
        return self.return_date_str(self._start_time)

    @property
    def execute_to(self):
        return self._execute_to

    @execute_to.setter
    def execute_to(self, val):
        self._execute_to = self._date_setter(val)

    def get_execute_to_str(self):
        return self.return_date_str(self._execute_to)

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, val):
        self._date = self._date_setter(val)

    @property
    def date_sending(self):
        return self._date_sending

    @date_sending.setter
    def date_sending(self, val):
        self._date_sending = self._date_setter(val)

    def get_date_str(self):
        return self.return_date_str(self._date)

    def get_date_sending_str(self):
        return self.return_date_str(self._date_sending)

    @property
    def link(self):
        return self._link

    def __str__(self):
        return f'Задание {self.num} от {self._date.strftime(self.DATE_FORMAT)}'