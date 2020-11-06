from utility.logger_super import LoggerSuper
import logging

class Login_model(LoggerSuper):
    logger = logging.getLogger('login_model')
    def __init__(self, controller, db):
        self.controller = controller
        self.db = db

    def check(self):
        pass