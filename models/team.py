from utility.util import date_setter


class Employee:
    def __init__(self, name, card_number, role):
        self.name = name
        self.card_number = card_number
        self.role = role

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if isinstance(other, Employee):
            if self.card_number == other.card_number:
                return True
            else:
                return False
        else:
            return False


class Employee_connection:
    def __init__(self, employee, team):
        self.employee = employee
        self.team = team

    def __str__(self):
        return f'{self.employee.name} команда {self.team.num} ({self.employee.role})'


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