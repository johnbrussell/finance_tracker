from services import setup_directories
from services.transactions import Transaction
from services.reporting_queue import ReportingQueue
from collections import namedtuple
import pandas as pd
import os
import json


Action = namedtuple("Action", ['function', 'description'])


class FinancialRecords:
    def __init__(self):
        setup_directories.setup_directories()
        self._ACCOUNTS = self._get_accounts()
        self._ACTIONS = self._set_up_actions()
        self._TRANSACTIONS = self._read_transactions()
        self._set_balances(self._read_balances())

    @staticmethod
    def _get_accounts():
        df = pd.read_csv('./balances/initial_balances.csv')
        return list(set(df['Account'].tolist()))

    @staticmethod
    def _read_transactions():
        if os.path.exists('./transactions/transactions.csv'):
            return pd.read_csv('./transactions/transactions.csv')
        return pd.DataFrame()

    def _set_balances(self, balances_csv):
        balances_csv.to_csv('./balances/current_balances.csv', index=False)
        balances_dict = dict()
        for index, row in balances_csv.iterrows():
            balances_dict[row['Account']] = float(row['Starting Balance'])
        self._BALANCES = balances_dict

    @staticmethod
    def _read_balances():
        if os.path.exists('./balances/current_balances.csv'):
            return pd.read_csv('./balances/current_balances.csv')
        if os.path.exists('./balances/initial_balances.csv'):
            return pd.read_csv('./balances/initial_balances.csv')
        raise IOError("initial_balances.csv file does not exist")

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
            'balance': Action(function=self._calculate_balances,
                              description='Calculate current balances'),
            'quit': Action(function='', description='Quit script'),
            'report': Action(function=self._run_report,
                             description='Run expense report')
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

    def _update_list_of_transactions(self):
        new_transactions = self._get_new_transactions()
        self._TRANSACTIONS = pd.concat([self._TRANSACTIONS, new_transactions])
        self._set_transaction_columns()
        self._TRANSACTIONS.to_csv('./transactions/transactions.csv', index=False)

    @staticmethod
    def _get_new_transactions():
        unreconciled_transactions = os.listdir('./transactions/unreconciled')
        new_transactions = list()
        for trans in unreconciled_transactions:
            with open(os.path.join('./transactions/unreconciled', trans)) as f:
                trans = json.load(f)
            new_transactions.append(trans)
        new_transactions = pd.DataFrame(new_transactions)
        return new_transactions

    @staticmethod
    def _clear_unreconciled_transactions():
        unreconciled_transactions = os.listdir('./transactions/unreconciled')
        for trans in unreconciled_transactions:
            os.remove(os.path.join('./transactions/unreconciled', trans))

    def _set_transaction_columns(self):
        df = self._TRANSACTIONS
        columns = df.columns
        categories = self._get_list_of_categories(columns)
        columns = ['Date', 'From', 'To', 'Memo', 'Amount'] + categories
        df = df[columns]
        df['Date'] = pd.to_datetime(df['Date']).dt.date
        df.sort_values(['Date', 'From', 'To', 'Amount'], inplace=True)
        self._TRANSACTIONS = df

    @staticmethod
    def _get_list_of_categories(columns):
        categories = [col.lower() for col in columns if 'ategory' in col]
        categories = [int(col.lstrip('category')) for col in categories]
        categories.sort()
        categories = ['Category%s' % str(cat) for cat in categories]
        return categories

    def _calculate_balances(self):
        self._update_list_of_transactions()
        new_transactions = self._get_new_transactions()
        self._clear_unreconciled_transactions()
        for index, trans in new_transactions.iterrows():
            if trans['From'] in self._BALANCES.keys():
                self._BALANCES[trans['From']] -= float(trans['Amount'])
            if trans['To'] in self._BALANCES.keys():
                self._BALANCES[trans['To']] += float(trans['Amount'])
        balances = list()
        for key in self._ACCOUNTS:
            balances.append(self._BALANCES[key])
        balances = pd.DataFrame([self._ACCOUNTS, balances]).transpose()
        balances.columns = ['Account', 'Starting Balance']
        self._set_balances(balances)
        print balances
        print "Net worth: ", balances['Starting Balance'].sum()

    def _run_report(self):
        self._run_income_report()
        self._run_expense_report()

    def _run_income_report(self):
        df = self._TRANSACTIONS.copy()
        df = df[df['To'].isin(self._ACCOUNTS)]
        df = df[~df['From'].isin(self._ACCOUNTS)]
        report = ReportingQueue(df, 'Income')
        report.run_report()

    def _run_expense_report(self):
        df = self._TRANSACTIONS.copy()
        df = df[df['From'].isin(self._ACCOUNTS)]
        df = df[~df['To'].isin(self._ACCOUNTS)]
        report = ReportingQueue(df, 'Expense')
        report.run_report()


