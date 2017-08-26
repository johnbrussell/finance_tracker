from services import setup_directories
from collections import namedtuple


Action = namedtuple("Action", ['function', 'description'])


class FinancialRecords:
    def __init__(self):
        setup_directories.setup_directories()
        self.__ACTIONS = self.__set_up_actions()

    def interact_with_user(self):
        action = 'initial'
        prompt = self.__create_prompt()

        while action != 'quit':
            action = input(prompt).lower()
            if action in self.__ACTIONS.keys() and action != 'quit':
                self.__ACTIONS[action].function()
                continue

    def __set_up_actions(self):
        actions = {
            'add': Action(function=self.__add_new_transaction(),
                          description='Record a new transaction'),
            'quit': Action(function='', description='Quit script')
        }
        return actions

    def __create_prompt(self):
        prompt = 'Available actions are: \n'
        for action in self.__ACTIONS.keys():
            prompt = prompt + '"{action}": '.format(action=action) + self.__ACTIONS[action].description + '\n'
        return prompt

    def __add_new_transaction(self):
        pass
