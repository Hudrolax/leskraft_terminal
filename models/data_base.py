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
        self.online = False
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
        self._nomenclature.append(Nomenclature(code, name))

    def add_document(self, link, num, date, date_sending, type, storage, status, execute_to, team_leader, team_number, team_date, start_time, end_time, destination, autos_number):
        self._documents.append(Document(link, num, date, date_sending, type, storage, status, execute_to, team_leader, team_number, team_date, start_time, end_time, destination, autos_number))

    def add_doc_table_string(self, doc_link, num, nomenclature_code, amount, status, adress_shelf, adress_floor, cancelled, reason_for_cancellation):
        _nomenclature = self.get_nomenclature(nomenclature_code)
        self._doc_strings.append(DocumentTableString(doc_link, num, _nomenclature, amount, status, adress_shelf, adress_floor, cancelled, reason_for_cancellation))

    def add_employee(self, name, card_number, role):
        self._employees.append(Employee(name, card_number, role))

    def add_team(self, num, date, team_leader, terminal_api):
        tl = self.get_employee(team_leader)
        if tl is None:
            self.logger.error(f'Team leader "{team_leader}" is not exists in Employees. Team {num}.')
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
        self._employee_connections.append(Employee_connection(employee, team))

# Вспомогательные функции
    def get_team_by_emloyee_code(self, code):
        _teams = []
        for team in self.teams:
            if team.team_leader.card_number == code and team not in _teams:
                _teams.append(team)

        for conn in self._employee_connections:
            if conn.employee.card_number == code and conn.team not in _teams:
                _teams.append(conn.team)
        return _teams

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

    def get_team_employees(self, team):
        _employees = []
        for connection in self._employee_connections:
            if connection.team.num == team.num and connection.team.date == team.date:
                if connection.employee not in _employees:
                    _employees.append(connection.employee)
        return _employees

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

