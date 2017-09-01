from services import setup_directories
from services.transactions import Transaction
from collections import namedtuple
import pandas as pd


Action = namedtuple("Action", ['function', 'description'])


class FinancialRecords:
    def __init__(self):
        setup_directories.setup_directories()
        self._ACCOUNTS = self._get_accounts()
        self._ACTIONS = self._set_up_actions()

    @staticmethod
    def _get_accounts():
        df = pd.read_csv('./balances/initial_balances.csv')
        return list(set(df['Account'].tolist()))

    def interact_with_user(self):
        action = 'initial'
        prompt = self._create_prompt()

        while action != 'quit':
            if action in self._ACTIONS.keys():
                self._ACTIONS[action].function()
            action = raw_input(prompt).lower()

    def _set_up_actions(self):
        # Must be function to use _add_new_transaction as object
        actions = {
            'add': Action(function=self._add_new_transaction,
                          description='Record a new transaction'),
            'quit': Action(function='', description='Quit script')
        }
        return actions

    def _create_prompt(self):
        prompt = 'Available actions are: \n'
        for action in self._ACTIONS.keys():
            prompt += '"{action}": {description}\n'.format(
                action=action, description=self._ACTIONS[action].description)
        return prompt

    def _add_new_transaction(self):
        Transaction(self._ACCOUNTS).create_new_transaction()
