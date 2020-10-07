import sqlite3 as sql
import threading
from time import sleep
from utility.logger_super import LoggerSuper
from models.document import Document, DocumentTableString
from models.nomenclature import Nomenclature
from utility.threaded_class import Threaded_class


class DB(Threaded_class):
    """
    Класс описывает объект базы данных
    Класс реализует запись и чтение БД в собственном потоке
    """
    DATE_FORMAT = '%d.%m.%Y %H:%M:%S'
    def __init__(self):
        self._init = False
        self.connection = None

        self._nomenclature = []
        self._documents = []
        self._doc_tables = []

        self._bool_commit_nomenclature = False
        self._bool_commit_documents = False
        self._bool_commit_doc_tables = False
        self._bool_clear_db = False

        self._sql_thread = threading.Thread(target=self._threaded_sql_func, args=(), daemon=False)
        self._sql_thread.start()
        while not self._init:
            sleep(0.1)

    @property
    def documents(self):
        return self._documents

    def get_doc(self, link):
        for doc in self._documents:
            if doc.link == link:
                return doc

    def get_doc_string(self, link, num):
        for doc_str in self._doc_tables:
            if doc_str.link == link and doc_str.num == num:
                return doc_str

    def get_doc_strings(self, doc_link):
        doc_strings = []
        for doc_str in self._doc_tables:
            if doc_str.doc_link == doc_link:
                doc_strings.append(doc_str)
        return doc_strings

    def get_nomenclature(self, code):
        for nom in self._nomenclature:
            if nom.code == code:
                return nom

    def _commit_nomenclature(self):
        self._bool_commit_nomenclature = True

    def _commit_documents(self):
        self._bool_commit_documents = True

    def _commit_doc_tables(self):
        self._bool_commit_doc_tables = True

    def create_tables(self, _connection):
        with _connection:
            cur = _connection.cursor()
            cur.execute('''CREATE TABLE IF NOT EXISTS nommenclature (code text, name text)''')
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
            cur.execute('''CREATE TABLE IF NOT EXISTS document_tables (
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
            if self._bool_commit_doc_tables:
                self._update_doc_tables()
                self._bool_commit_doc_tables = False
            if self._bool_clear_db:
                self._clear_db()
                self._bool_clear_db = False
            sleep(0.1)

    def _load_nomenclature_from_db(self):
        self._nomenclature = []
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM nommenclature")
        _list = cur.fetchall()
        for p in _list:
            self._nomenclature.append(Nomenclature(p[0], p[1]))

    def _load_documents_from_db(self):
        self._documents = []
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM documents")
        _list = cur.fetchall()
        for p in _list:
            self._documents.append(Document(p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7], p[8], p[9], p[10], p[11], p[12], p[13]))

    def _load_doc_tables_from_db(self):
        self._doc_tables = []
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM document_tables")
        _list = cur.fetchall()
        for p in _list:
            self._doc_tables.append(DocumentTableString(p[0], p[1], p[2], p[3], p[4], p[5], p[6]))

    def _load_data_from_db(self):
        self._load_nomenclature_from_db()
        self._load_documents_from_db()
        self._load_doc_tables_from_db()

    def _update_nomenclature_codes(self):
        cur = self.connection.cursor()
        cur.execute("DELETE FROM nommenclature")
        sql_query = "INSERT INTO nommenclature (code, name) VALUES (?, ?)"
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

    def _update_doc_tables(self):
        cur = self.connection.cursor()
        cur.execute("DELETE FROM document_tables")
        sql_query = '''INSERT INTO document_tables (doc_link, num, nomenclature_code, amount, status, cancelled, reason_for_cancellation)
                                        VALUES (?, ?, ?, ?, ?, ?, ?)'''
        values = []
        for doc_str in self._doc_tables:
            if isinstance(doc_str, DocumentTableString):
                values.append((doc_str.doc_link, doc_str.num, doc_str.nomenclature_code, doc_str.amount, doc_str.status, doc_str.cancelled,\
                               doc_str.reason_for_cancellation))
            else:
                raise TypeError(f'_update_doc_tables: {doc_str} is not DocumentTableString. It is {type(doc_str)}')
        cur.executemany(sql_query, values)
        self.connection.commit()
        cur.close()

    def _clear_db(self):
        cur = self.connection.cursor()
        cur.execute("DELETE FROM documents")
        cur.execute("DELETE FROM document_tables")
        cur.execute("DELETE FROM document_tables")
        self.connection.commit()
        cur.close()

    def clear_db(self):
        self._documents = []
        self._doc_tables = []
        self._nomenclature = []
        self._bool_clear_db = True

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
        for doc_string in self._doc_tables:
            if doc_string.doc_link == doc_link and doc_string.num == num:
                doc_string.nomenclature_code = nomenclature_code
                doc_string.amount = amount
                doc_string.status = status
                doc_string.cancelled = cancelled
                doc_string.reason_for_cancellation = reason_for_cancellation

                self._commit_doc_tables()
                return
        self._doc_tables.append(DocumentTableString(doc_link, num, nomenclature_code, amount, status, cancelled, reason_for_cancellation))
        self._commit_doc_tables()

    def get_fuul_doc_description(self, link):
        for doc in self._documents:
            if doc.link == link:
                print(f'link: {doc.link}')
                print(f'Задание {doc.num} от {doc.date.strftime(self.DATE_FORMAT)}')
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
                    print(f'      {k}: {self.get_nomenclature(_str.nomenclature_code)}, кол-во: {_str.amount}, статус: {_str.status}, cancelled: {_str.cancelled}, причина: {_str.reason_for_cancellation}')
                    k += 1
                print()


if __name__ == '__main__':
    data_base = DB()
    data_base.add_nomenclature('test_code1', 'test_name 1')
    data_base.add_nomenclature('test_code2', 'test name 2')
    sleep(2)
    Threaded_class.working = False

