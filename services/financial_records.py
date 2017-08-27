from services import setup_directories
from services.transactions import Transaction
from collections import namedtuple
import pandas as pd


Action = namedtuple("Action", ['function', 'description'])


class FinancialRecords:
    def __init__(self):
        setup_directories.setup_directories()
        self.__ACCOUNTS = self.__get_accounts()
        self.__ACTIONS = self.__set_up_actions()

    @staticmethod
    def __get_accounts():
        df = pd.read_csv('./balances/initial_balances.csv')
        return list(set(df['Account'].tolist()))

    def interact_with_user(self):
        action = 'initial'
        prompt = self.__create_prompt()

        while action != 'quit':
            if action in self.__ACTIONS.keys():
                self.__ACTIONS[action].function()
            action = raw_input(prompt).lower()

    def __set_up_actions(self):
        actions = {
            'add': Action(function=self.__add_new_transaction,
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
        Transaction(self.__ACCOUNTS).create_new_transaction()
