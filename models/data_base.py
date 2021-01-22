from time import sleep
from models.document import Document, DocumentTableString
from models.nomenclature import Nomenclature
from models.team import Team, Employee, Employee_connection
from utility.logger_super import LoggerSuper
import logging
from utility.util import DATE_FORMAT
from utility.util import date_setter


class DB(LoggerSuper):
    """
    Класс описывает объект базы данных
    """
    logger = logging.getLogger('DB')
    def __init__(self):
        self.clear_db()

# Функции очистки базы
    def clear_db(self):
        self._documents = []
        self._doc_strings = []
        self._nomenclature = []
        self._teams = []
        self._employees = []
        self._employee_connections = []  # связь работников с командами

    def clear_docs(self):
        self._documents = []
        self._doc_strings = []
        self._nomenclature = []

    def clear_employees(self):
        self._employees = []

    def clear_teams(self):
        self._teams = []

    def clear_employee_connections(self):
        self._employee_connections = []

# Функции добавления в списки
    def add_nomenclature(self, code, name):
        for nom in self._nomenclature:
            if nom.code == code:
                nom.name = name
                return
        self._nomenclature.append(Nomenclature(code, name))

    def add_document(self, link, num, date, date_sending, type, storage, status, execute_to, team_leader, team_number, start_time, end_time, destination, autos_number):
        for doc in self._documents:
            if doc.link == link:
                doc.num = num
                doc.date = date
                doc.date_sending = date_sending
                doc.type = type
                doc.storage = storage
                doc.status = status
                doc.execute_to = execute_to
                doc.team_leader = team_leader
                doc.team_number = team_number
                doc.start_time = start_time
                doc.end_time = end_time
                doc.destination = destination
                doc.autos_number = autos_number
                return
        self._documents.append(Document(link, num, date, date_sending, type, storage, status, execute_to, team_leader, team_number, start_time, end_time, destination, autos_number))

    def add_doc_table_string(self, doc_link, num, nomenclature_code, amount, status, adress_shelf, adress_floor, cancelled, reason_for_cancellation):
        _nomenclature = self.get_nomenclature(nomenclature_code)
        for doc_string in self._doc_strings:
            if doc_string.doc_link == doc_link and doc_string.num == num:
                doc_string.nomenclature = _nomenclature
                doc_string.amount = amount
                doc_string.status = status
                doc_string.adress_shelf = adress_shelf
                doc_string.adress_floor = adress_floor
                doc_string.cancelled = cancelled
                doc_string.reason_for_cancellation = reason_for_cancellation
                return
        self._doc_strings.append(DocumentTableString(doc_link, num, _nomenclature, amount, status, adress_shelf, adress_floor, cancelled, reason_for_cancellation))

    def add_employee(self, name, card_number, role):
        for employee in self._employees:
            if employee.card_number == card_number:
                employee.name = name
                employee.role = role
                return
        self._employees.append(Employee(name, card_number, role))

    def add_team(self, num, date, team_leader, terminal_api):
        tl = self.get_employee(team_leader)
        if tl is None:
            self.logger.error(f'Team leader "{team_leader}" is not exists in Employees. Team {num}.')
            return
        for team in self._teams:
            if team.num == num and team.date == date:
                team.team_leader = tl
                team.terminal_api = terminal_api
                return
        self._teams.append(Team(num, date, tl, terminal_api))

    def add_employee_connection(self, card_number, team_num, team_date):
        team = self.get_team(team_num, team_date)
        employee = self.get_employee(card_number)
        if team is None:
            self.logger.error(f'team "{team_num} at {team_date}" is not exists in _teams.')
            return
        if employee is None:
            self.logger.error(f'employee with card number "{card_number} is not exists in _employees.')
            return

        for ec in self._employee_connections:
            if ec.employee == employee and ec.team == team:
                return
        self._employee_connections.append(Employee_connection(employee, team))

# Вспомогательные функции
    def get_team(self, num, date):
        date = date_setter(date)
        for team in self._teams:
            if team.num == num and team.date == date:
                return team
        return None

    def get_employee(self, param):
        for employee in self._employees:
            param = str(param)
            if employee.card_number == param or employee.name == param:
                return employee
        return None

    def get_fuul_doc_description(self, link):
        for doc in self._documents:
            if doc.link == link:
                print(f'link: {doc.link}')
                print(f'Задание {doc.num} от {doc.date.strftime(DATE_FORMAT)}')
                print(f'   date_sending: {doc.date_sending}')
                print(f'   Тип: {doc.type}')
                print(f'   Склад: {doc.storage}')
                print(f'   Статус: {doc.status}')
                print(f'   Выполнить до: {doc.execute_to}')
                print(f'   Кладовщик: {doc.team_leader}')
                print(f'   Номер бригады: {doc.team_number}')
                print(f'   Начало исполнения: {doc.start_time}')
                print(f'   Конец исполнения: {doc.end_time}')
                print(f'   Назначение: {doc.destination}')
                print(f'    Товары: {doc.type}')
                k = 1
                for _str in self.get_doc_strings(doc.link):
                    print(f'      {k}: {self.get_nomenclature(_str.nomenclature.code)}, кол-во: {_str.amount}, статус: {_str.status}, cancelled: {_str.cancelled}, причина: {_str.reason_for_cancellation}')
                    k += 1
                print()

    @property
    def employees(self):
        return self._employees

    @property
    def documents(self):
        return self._documents

    @property
    def teams(self):
        return self._teams

    def get_doc(self, link):
        for doc in self._documents:
            if doc.link == link:
                return doc

    def get_doc_string(self, link, num):
        for doc_str in self._doc_strings:
            if doc_str.link == link and doc_str.num == num:
                return doc_str

    def get_doc_strings(self, doc_link):
        doc_strings = []
        for doc_str in self._doc_strings:
            if doc_str.doc_link == doc_link:
                doc_strings.append(doc_str)
        return doc_strings

    def get_nomenclature(self, code):
        for nom in self._nomenclature:
            if nom.code == code:
                return nom

if __name__ == '__main__':
    data_base = DB()
    data_base.add_employee('Вася', '123456')
    data_base.add_employee('Петя', '987456')
    from datetime import datetime
    data_base.add_team(1, '25.08.2020 17:12:15', '987456', 'plate1')
    # data_base.add_employee_connection('987456', 1, '25.08.2020 17:12:15', 'грузчик')
    sleep(2)
    print(data_base.employees)

