import sqlite3 as sql
import threading
from time import sleep
from models.document import Document, DocumentTableString
from models.nomenclature import Nomenclature
from models.team import Team, Employee, Employee_connection
from utility.threaded_class import Threaded_class
from utility.logger_super import LoggerSuper
import logging
from utility.util import DATE_FORMAT
from utility.util import date_setter


class DB(Threaded_class, LoggerSuper):
    """
    Класс описывает объект базы данных
    Класс реализует запись и чтение БД в собственном потоке
    """
    logger = logging.getLogger('DB')

    def __init__(self):
        self._init = False
        self.connection = None

        self._nomenclature = []
        self._documents = []
        self._doc_strings = []
        self._teams = []
        self._employees = []
        self._employee_connections = [] # связь работников с командами

        self._bool_commit_nomenclature = False
        self._bool_commit_documents = False
        self._bool_commit_doc_strings = False
        self._bool_commit_teams = False
        self._bool_commit_employees = False
        self._bool_commit_employee_connections = False

        self._sql_thread = threading.Thread(target=self._threaded_sql_func, args=(), daemon=False)
        self._sql_thread.start()
        while not self._init:
            sleep(0.1)

# Функции флагов коммитов
    def _commit_nomenclature(self):
        self._bool_commit_nomenclature = True

    def _commit_documents(self):
        self._bool_commit_documents = True

    def _commit_doc_strings(self):
        self._bool_commit_doc_strings = True

    def _commit_teams(self):
        self._bool_commit_teams = True

    def _commit_employees(self):
        self._bool_commit_employees = True

    def _commit_employee_connections (self):
        self._bool_commit_employee_connections = True

### Функции работы с БД
    @staticmethod
    #Создание таблиц
    def create_tables(_connection):
        with _connection:
            cur = _connection.cursor()
            cur.execute('''CREATE TABLE IF NOT EXISTS employees (name text, card_number text)''')
            cur.execute('''CREATE TABLE IF NOT EXISTS teams (num integer, date datetime, team_leader text, terminal_api text)''')
            cur.execute('''CREATE TABLE IF NOT EXISTS employee_connections (card_number text, team_num integer, team_date datetime,
                                        position text)''')
            cur.execute('''CREATE TABLE IF NOT EXISTS nomenclature (code text, name text)''')
            cur.execute('''CREATE TABLE IF NOT EXISTS documents (
                                        link text,
                                        num text,
                                        date datetime,
                                        date_sending datetime,
                                        type text,
                                        storage text,
                                        status text,
                                        execute_to datetime,
                                        team_leader text,
                                        team_number integer,
                                        start_time datetime,
                                        end_time datetime,
                                        destination text,
                                        autos_number text
                                        )''')
            cur.execute('''CREATE TABLE IF NOT EXISTS document_strings (
                                        doc_link text,
                                        num integer,
                                        nomenclature_code text,
                                        amount real,
                                        status text,
                                        cancelled boolean,
                                        reason_for_cancellation text
                                        )''')
            _connection.commit()
            cur.close()
    # Поток работы с БД
    def _threaded_sql_func(self):
        self.connection = sql.connect('base.sqlite')
        self.create_tables(self.connection)
        self._load_data_from_db()
        self._init = True
        while self.working:
            if self._bool_commit_nomenclature:
                self._update_nomenclature_codes()
                self._bool_commit_nomenclature = False
            if self._bool_commit_documents:
                self._update_documents()
                self._bool_commit_documents = False
            if self._bool_commit_doc_strings:
                self._update_doc_strings()
                self._bool_commit_doc_strings = False
            if self._bool_commit_employees:
                self._update_employees()
                self._bool_commit_employees = False
            if self._bool_commit_teams:
                self._update_teams()
                self._bool_commit_teams = False
            if self._bool_commit_employee_connections:
                self._update_employee_connections()
                self._bool_commit_employee_connections = False
            sleep(0.1)

    # Функции загрузки из БД
    def _load_nomenclature_from_db(self):
        self._nomenclature = []
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM nomenclature")
        _list = cur.fetchall()
        for p in _list:
            self._nomenclature.append(Nomenclature(*p))

    def _load_documents_from_db(self):
        self._documents = []
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM documents")
        _list = cur.fetchall()
        for p in _list:
            self._documents.append(Document(*p))

    def _load_doc_strings_from_db(self):
        self._doc_strings = []
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM document_strings")
        _list = cur.fetchall()
        for p in _list:
            nomenclature = self.get_nomenclature(p[2])
            self._doc_strings.append(DocumentTableString(p[0], p[1], nomenclature, p[3], p[4], p[5], p[6]))

    def _load_employees_from_db(self):
        self._employees = []
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM employees")
        _list = cur.fetchall()
        for p in _list:
            self._employees.append(Employee(*p))

    def _load_teams_from_db(self):
        self._teams = []
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM teams")
        _list = cur.fetchall()
        for p in _list:
            self._teams.append(Team(*p))

    def _load_ec_from_db(self):
        self._teams = []
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM employee_connections")
        _list = cur.fetchall()
        for p in _list:
            team = self.get_team(p[1], p[2])
            employee = self.get_employee(p[0])
            self._employee_connections.append(Employee_connection(employee, team, p[3]))

    def _load_data_from_db(self):
        self._load_nomenclature_from_db()
        self._load_documents_from_db()
        self._load_doc_strings_from_db()
        self._load_employees_from_db()
        self._load_teams_from_db()

    # Обновление БД
    def _update_nomenclature_codes(self):
        cur = self.connection.cursor()
        cur.execute("DELETE FROM nomenclature")
        sql_query = "INSERT INTO nomenclature (code, name) VALUES (?, ?)"
        values = []
        for nom in self._nomenclature:
            if isinstance(nom, Nomenclature):
                values.append((nom.code, nom.name))
            else:
                raise TypeError(f'_update_nomenclature_codes: {nom} is not Nomenclature. It is {type(nom)}')
        cur.executemany(sql_query, values)
        self.connection.commit()
        cur.close()

    def _update_documents(self):
        cur = self.connection.cursor()
        cur.execute("DELETE FROM documents")
        sql_query = '''INSERT INTO documents (link, num, date, date_sending, type, storage, status, execute_to,
                            team_leader, team_number, start_time, end_time, destination, autos_number) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
        values = []
        for doc in self._documents:
            if isinstance(doc, Document):
                values.append((doc.link, doc.num, doc.date, doc.date_sending, doc.type, doc.storage, doc.status,\
                doc.execute_to, doc.team_leader, doc.team_number, doc.start_time, doc.end_time, doc.destination, doc.autos_number))
            else:
                raise TypeError(f'_update_documents: {doc} is not Document. It is {type(doc)}')
        cur.executemany(sql_query, values)
        self.connection.commit()
        cur.close()

    def _update_doc_strings(self):
        cur = self.connection.cursor()
        cur.execute("DELETE FROM document_strings")
        sql_query = '''INSERT INTO document_strings (doc_link, num, nomenclature_code, amount, status, cancelled, reason_for_cancellation)
                                        VALUES (?, ?, ?, ?, ?, ?, ?)'''
        values = []
        for doc_str in self._doc_strings:
            if isinstance(doc_str, DocumentTableString):
                values.append((doc_str.doc_link, doc_str.num, doc_str.nomenclature.code, doc_str.amount, doc_str.status, doc_str.cancelled,\
                               doc_str.reason_for_cancellation))
            else:
                raise TypeError(f'_update_doc_strings: {doc_str} is not DocumentTableString. It is {type(doc_str)}')
        cur.executemany(sql_query, values)
        self.connection.commit()
        cur.close()

    def _update_teams(self):
        cur = self.connection.cursor()
        cur.execute("DELETE FROM teams")
        sql_query = '''INSERT INTO teams (num, date, team_leader, terminal_api)
                                        VALUES (?, ?, ?, ?)'''
        values = []
        for team in self._teams:
            if isinstance(team, Team):
                values.append((team.num, team.date, team.team_leader.card_number, team.terminal_api))
            else:
                raise TypeError(f'_update_team: {team} is not Team. It is {type(team)}')
        cur.executemany(sql_query, values)
        self.connection.commit()
        cur.close()

    def _update_employees(self):
        cur = self.connection.cursor()
        cur.execute("DELETE FROM employees")
        sql_query = '''INSERT INTO employees (name, card_number)
                                        VALUES (?, ?)'''
        values = []
        for employee in self._employees:
            if isinstance(employee, Employee):
                values.append((employee.name, employee.card_number))
            else:
                raise TypeError(f'_update_employees: {employee} is not Employees. It is {type(employee)}')
        cur.executemany(sql_query, values)
        self.connection.commit()
        cur.close()

    def _update_employee_connections(self):
        cur = self.connection.cursor()
        cur.execute("DELETE FROM employee_connections")
        sql_query = '''INSERT INTO employee_connections (card_number, team_num, team_date, position)
                                        VALUES (?, ?, ?, ?)'''
        values = []
        for ec in self._employee_connections:
            if isinstance(ec, Employee_connection):
                values.append((ec.employee.card_number, ec.team.num, ec.team.date, ec.position))
            else:
                raise TypeError(f'_update_employee_connections: {ec} is not Employee_connection. It is {type(ec)}')
        cur.executemany(sql_query, values)
        self.connection.commit()
        cur.close()

# Функции очистки базы
    def clear_db(self):
        self._documents = []
        self._doc_strings = []
        self._nomenclature = []
        self._teams = []
        self._employees = []

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

### Конец функции работы с БД>>

# Функции добавления в списки
    def add_nomenclature(self, code, name):
        for nom in self._nomenclature:
            if nom.code == code:
                nom.name = name
                self._commit_nomenclature()
                return
        self._nomenclature.append(Nomenclature(code, name))
        self._commit_nomenclature()

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
                self._commit_documents()
                return
        self._documents.append(Document(link, num, date, date_sending, type, storage, status, execute_to, team_leader, team_number, start_time, end_time, destination, autos_number))
        self._commit_documents()

    def add_doc_table_string(self, doc_link, num, nomenclature_code, amount, status, cancelled, reason_for_cancellation):
        _nomenclature = self.get_nomenclature(nomenclature_code)
        for doc_string in self._doc_strings:
            if doc_string.doc_link == doc_link and doc_string.num == num:
                doc_string.nomenclature = _nomenclature
                doc_string.amount = amount
                doc_string.status = status
                doc_string.cancelled = cancelled
                doc_string.reason_for_cancellation = reason_for_cancellation

                self._commit_doc_strings()
                return
        self._doc_strings.append(DocumentTableString(doc_link, num, _nomenclature, amount, status, cancelled, reason_for_cancellation))
        self._commit_doc_strings()

    def add_employee(self, name, card_number):
        for employee in self._employees:
            if employee.card_number == card_number:
                employee.name = name
                self._commit_employees()
                return
        self._employees.append(Employee(name, card_number))
        self._commit_employees()

    def add_team(self, num, date, team_leader, terminal_api):
        tl = self.get_employee(team_leader)
        if tl is None:
            self.logger.error(f'Team leader "{team_leader}" is not exists in Employees. Team {num}.')
            return
        for team in self._teams:
            if team.num == num and team.date == date:
                team.team_leader = tl
                team.terminal_api = terminal_api

                self._commit_teams()
                return
        self._teams.append(Team(num, date, tl, terminal_api))
        self._commit_teams()

    def add_employee_connection(self, card_number, team_num, team_date, position):
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
                ec.position = position
                self._commit_employee_connections()
                return
        self._employee_connections.append(Employee_connection(employee, team, position))
        self._commit_employee_connections()

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
    Threaded_class.working = False
    print(data_base.employees)

