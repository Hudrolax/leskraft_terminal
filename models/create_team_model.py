from utility.logger_super import LoggerSuper
import logging
import requests
from env import SERVER, BASE_NAME, ADD_TEAM_ROUTE, AUTH_BASIC, API_KEY
from config import CONNECTION_TIMEOUT


class CreateTeam_model(LoggerSuper):
    logger = logging.getLogger('CreateTeam_model')
    maximum_teammates = 3

    def __init__(self, window, db):
        self.window = window
        self.db = db
        self.window_state = 1

        self.team_leader = None
        self.teammates = []

    def del_employee(self, employee):
        self.teammates.remove(employee)

    def send_team_to_1c(self):
        answer = ''
        result = False
        registered = False
        self.logger.info("Создаем бригаду на стороне 1С")
        try:
            url = f'http://{SERVER}/{BASE_NAME}{ADD_TEAM_ROUTE}'
            headers = {'Content-type': 'application/json',  # Определение типа данных
                       'Accept': 'text/plain',
                       'Authorization': AUTH_BASIC}
            teammates_cards = []
            for employee in self.teammates:
                teammates_cards.append(employee.card_number)
            body = {"API_key": API_KEY, "team_leader": self.team_leader.card_number, "teammates": teammates_cards}
            answer = requests.post(url=url, json=body, headers=headers, timeout=CONNECTION_TIMEOUT).content.decode('utf-8')
            if answer == 'ok':
                self.logger.info('Бригада зарегистрирована!')
                answer = 'Бригада зарегистрирована!'
                registered = True
            else:
                self.logger.error(answer)
            result = True
        except (
                requests.exceptions.ConnectionError or requests.exceptions.ConnectTimeout or requests.exceptions.BaseHTTPError) as e:
            self.logger.critical(e)
        except Exception as e:
            self.logger.critical(e)
        return (result, registered, answer)

    def rfid_code_got(self, card_id):
        employee = self.db.get_employee(card_id)

        # Не нашли человека, покажем ошибку
        if employee == None:
            return (False, False, f'Карта {card_id} не зарегистрирована. Обратитесь в отдел кадров.')

        # Кладовщик набрал команду и отметился второй раз, значит формируем бригаду в 1С
        if self.team_leader == employee:
            return self.send_team_to_1c()

        # слишком много участников? не порядок
        if len(self.teammates) >= self.maximum_teammates:
            return (False, False, f'Количество участников бригады не может быть больше {self.maximum_teammates+1}')

        if self.window_state == 1:
            # Отсканироваля кладовщик?
            if employee.role == "Кладовщик":
                self.team_leader = employee
                self.window_state = 2
            else:
                return (False, False, f'Сотрудник с картой {card_id} не является кладовщиком!.')
        elif self.window_state == 2:
            if employee in self.teammates:
                return (False, False, f'Сотрудник с картой {card_id} уже является участником бригады!.')
            else:
                self.teammates.append(employee)
        return (False, False, '')