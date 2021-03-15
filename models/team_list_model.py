from utility.logger_super import LoggerSuper
import logging


class TeamList_model(LoggerSuper):
    logger = logging.getLogger('team_list_model')

    def __init__(self, controller, db):
        self.controller = controller
        self.db = db