from utility.util import date_setter


class Employee:
    def __init__(self, name, card_number):
        self.name = name
        self.card_number = card_number

    def __str__(self):
        return self.name


class Employee_connection:
    def __init__(self, employee, team, position):
        self.employee = employee
        self.team = team
        self.position = position

    def __str__(self):
        return f'{self.employee.name} команда {self.team.num} ({self.position})'


class Team:
    def __init__(self, num, date, team_leader, terminal_api):
        self.num = num
        self._date = date_setter(date)
        self.team_leader = team_leader
        self.terminal_api = terminal_api

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, val):
        self._date = date_setter(val)

    def __str__(self):
        return f'Команда {self.num} ({self.team_leader})'