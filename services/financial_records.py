from services import set_up_directories
from services.transactions import Transaction
from services.reporting_queue import ReportingQueue
from collections import namedtuple
import editdistance
import pandas as pd
import os
import json


Action = namedtuple("Action", ['function', 'description'])


CURRENT_BALANCES_CSV_PATH = './balances/current_balances.csv'
INITIAL_BALANCES_CSV_PATH = './balances/initial_balances.csv'
TRANSACTIONS_CSV_PATH = './transactions/transactions.csv'


class FinancialRecords:
    def __init__(self):
        set_up_directories.set_up_directories()
        self._set_balances(self._read_balances())
        self._ACCOUNTS = self._get_accounts()
        self._ACTIONS = self._set_up_actions()
        self._TRANSACTIONS = self._read_transactions()

    @staticmethod
    def _get_accounts():
        df = pd.read_csv(INITIAL_BALANCES_CSV_PATH)
        return list(set(df['Account'].tolist()))

    @staticmethod
    def _read_transactions():
        if os.path.exists(TRANSACTIONS_CSV_PATH):
            return pd.read_csv(TRANSACTIONS_CSV_PATH)
        return pd.DataFrame()

    def _set_balances(self, balances_csv):
        balances_csv.to_csv(CURRENT_BALANCES_CSV_PATH, index=False)
        balances_dict = dict()
        for index, row in balances_csv.iterrows():
            balances_dict[row['Account']] = float(row['Starting Balance'])
        self._BALANCES = balances_dict

    @staticmethod
    def _set_blank_balances_csv():
        balances_csv = pd.DataFrame()
        balances_csv['Account'] = []
        balances_csv['Starting Balance'] = []
        balances_csv.to_csv(INITIAL_BALANCES_CSV_PATH, index=False)

    def _read_balances(self):
        if os.path.exists(CURRENT_BALANCES_CSV_PATH):
            return pd.read_csv(CURRENT_BALANCES_CSV_PATH)
        if os.path.exists(INITIAL_BALANCES_CSV_PATH):
            return pd.read_csv(INITIAL_BALANCES_CSV_PATH)
        self._set_blank_balances_csv()
        return self._read_balances()

    def interact_with_user(self):
        action = 'initial'
        prompt = self._create_prompt()

        while action != 'quit':
            if action in self._ACTIONS.keys():
                self._ACTIONS[action].function()
            action = input(prompt).lower()

    def _set_up_actions(self):
        # Must be function to use _add_new_transaction as object
        actions = {
            'add': Action(function=self._add_new_transaction,
                          description='Record a new transaction'),
            'balance': Action(function=self._calculate_balances,
                              description='Calculate current balances'),
            'quit': Action(function='', description='Quit script'),
            'report': Action(function=self._run_report,
                             description='Run expense report'),
            'edit': Action(function=self._search_for_transaction,
                           description='Edit transaction'),
            'recalculate': Action(function=self._recalculate_transactions,
                                  description='Recalculate current balances'),
            'account': Action(function=self._add_account,
                              description="Add a new account")
        }
        return actions

    def _create_prompt(self):
        prompt = 'Available actions are: \n'
        for action in self._ACTIONS.keys():
            prompt += '"{action}": {description}\n'.format(
                action=action, description=self._ACTIONS[action].description)
        return prompt

    def _add_new_transaction(self):
        return Transaction(self._ACCOUNTS).create_new_transaction()

    def _update_list_of_transactions(self):
        new_transactions = self._get_new_transactions()
        self._TRANSACTIONS = pd.concat([self._TRANSACTIONS, new_transactions], sort=False)
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
        df.sort_values(['Date', 'From', 'To', 'Amount'], ascending=False, inplace=True)
        self._TRANSACTIONS = df

    @staticmethod
    def _get_list_of_categories(columns):
        categories = [col.lower() for col in columns if 'ategory' in col]
        categories = [int(col.lstrip('category')) for col in categories]
        categories.sort()
        categories = ['Category%s' % str(cat) for cat in categories]
        return categories

    def _recalculate_transactions(self):
        self._set_balances(pd.read_csv(INITIAL_BALANCES_CSV_PATH))
        self._calculate_balances(full=True)

    def _calculate_balances(self, full=False, quiet=False):
        self._update_list_of_transactions()
        if not full:
            new_transactions = self._get_new_transactions()
        else:
            new_transactions = self._TRANSACTIONS.copy()
        self._clear_unreconciled_transactions()
        for index, trans in new_transactions.iterrows():
            if trans['From'] in self._BALANCES.keys():
                self._BALANCES[trans['From']] -= float(trans['Amount'])
            if trans['To'] in self._BALANCES.keys():
                self._BALANCES[trans['To']] += float(trans['Amount'])
        balances = list()
        for key in self._ACCOUNTS:
            balances.append(round(float(self._BALANCES[key]), 2))
        balances = pd.DataFrame([self._ACCOUNTS, balances]).transpose()
        balances.columns = ['Account', 'Starting Balance']
        self._set_balances(balances)
        if not quiet:
            print(balances)
            print("Net worth: ", balances['Starting Balance'].sum())

    def _run_report(self):
        self._TRANSACTIONS['Amount'] = self._TRANSACTIONS['Amount'].apply(float)
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

    def _search_for_transaction(self):
        self._calculate_balances(quiet=True)
        columns = list(self._TRANSACTIONS.columns)
        column_dict = dict()
        for col in columns:
            column_dict[col.lower()] = col

        message = 'On what parameter should the search be?: %s ' % columns
        search_col = 'notacolumnname'

        while search_col not in columns:
            search_col = column_dict.get(input(message).lower(), 'notacolumnname')

        message = 'Enter search key: '
        search_val = input(message)

        df = self._TRANSACTIONS.copy().fillna('')
        df['Key'] = range(len(df))
        for col in column_dict.values():
            df[col] = df[col].apply(str)

        df['editdistance'] = len(search_val)
        if search_col != 'amount':
            df['editdistance'] = df[search_col].apply(
                lambda x: editdistance.eval(x, search_val))
        df_list = df[df['editdistance'] < max(len(search_val) - 2.0, len(search_val) / 2)].copy()
        del df['editdistance']

        if len(df_list) == 0:
            print("Search key not found")

        df_list.sort_values(by=['editdistance'], ascending=[True], inplace=True)

        for index, row in df_list.iterrows():
            response = 'notyn'
            while response not in ['y', 'n']:
                response = input('Is this the transaction you are looking to edit?: \n %s ' % row).lower()

            if response == 'y':
                df = df[df['Key'] != row['Key']]
                del df['Key']
                successful = self._add_new_transaction()
                if successful:
                    self._TRANSACTIONS = df.copy()
                    self._calculate_balances(quiet=True)
                else:
                    print("Something went wrong.  Not saving changes")
                break

    def _add_account(self):
        yn_response = 'notaresponse'
        account = None
        initial_balance = None
        while yn_response not in ['y', 'n']:
            account = input("Enter name of account to add: ")
            initial_balance = input("Enter initial balance of account: ")
            yn_response = input("Confirm: %s account has initial balance of %s: " %
                                (account, initial_balance)).lower()

        row = list()
        row.append({'Account': account, 'Starting Balance': initial_balance})

        for balance_type_path in [INITIAL_BALANCES_CSV_PATH, CURRENT_BALANCES_CSV_PATH]:
            if balance_type_path in os.listdir('./balances'):
                df = pd.read_csv(balance_type_path)
            else:
                df = pd.DataFrame()
            df = pd.concat([df, pd.DataFrame(row)])
            df.to_csv(balance_type_path, index=False)

        self._set_balances(self._read_balances())
        self._ACCOUNTS = self._get_accounts()
