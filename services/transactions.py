from datetime import datetime
import editdistance
import os
import json
import pandas as pd


class Transaction:
    KEYWORDS = [
        'back',
        'repeat',
        'cancel',
        'quit'
    ]

    INFO_KEYS = {
        'Date': 'Date',
        'From': 'From',
        'To': 'To',
        'Memo': 'Memo',
        'Amount': 'Amount',
        'Category': 'Category'
    }

    def __init__(self, accounts):
        self.INFORMATION = dict()
        self.ACCOUNTS = self._check_accounts(accounts)
        self.OTHER_TRANSACTIONS = pd.read_csv('./transactions/transactions.csv') if os.path.exists(
            './transactions/transactions.csv') else pd.DataFrame()

    def _check_accounts(self, accounts):
        for account in accounts:
            if account in self.KEYWORDS:
                raise ValueError("Account name %s must be changed; overlaps with reserved word" % account)
        return accounts

    def _create_process(self):
        self._PROCESS = [
            self._get_date,
            self._get_from,
            self._get_to,
            self._get_memo,
            self._get_amount,
            self._get_categories,
            self._confirm,
            self._save
        ]

    def create_new_transaction(self):
        self._create_process()
        self._run_process()

    def _run_process(self):
        print "Enter 'back' to return to the prior step; 'cancel' to cancel the new transaction."
        self._PROCESS[0](prev=list(), nxt=self._PROCESS[1:])

    def _interpret_result(self, previous_steps, current_step, next_steps, validation, info, key, **kwargs):
        # Info is the information collected in the function being interpreted.
        if info.lower() not in self.KEYWORDS:
            validation = validation(info, kwargs) if kwargs else validation(info)
            if validation:
                if key:
                    self.INFORMATION[key] = info
                self._proceed_to_next_step(prev=previous_steps, current=current_step, nxt=next_steps)
            else:
                current_step(prev=previous_steps, nxt=next_steps)
        if info == 'back':
            self._proceed_to_prev_step(prev=previous_steps, current=current_step, nxt=next_steps)
        if info == 'repeat':
            current_step(prev=previous_steps, nxt=next_steps)

    @staticmethod
    def _proceed_to_next_step(prev, current, nxt):
        if nxt:
            prev.append(current)
            next_step = nxt[0]
            nxt = nxt[1:]
            next_step(prev=prev, nxt=nxt)

    @staticmethod
    def _proceed_to_prev_step(prev, current, nxt):
        if prev:
            current = [current]
            nxt = current + nxt
            prev_step = prev[len(prev) - 1]
            prev = prev[:-1]
            prev_step(prev=prev, nxt=nxt)

    def _get_date(self, prev=list(), nxt=list()):
        date = raw_input("Enter the date of the transaction (MM/DD/YYYY): ")
        self._interpret_result(previous_steps=prev, current_step=self._get_date, next_steps=nxt,
                               validation=self._validate_date, info=date, key=self.INFO_KEYS['Date'])

    @staticmethod
    def _validate_date(date):
        date = date.replace('-', '/').replace('_', '/')
        try:
            datetime.strptime(date, '%m/%d/%y')
            return True
        except ValueError as e:
            if "does not match format" in str(e):
                pass
        try:
            datetime.strptime(date, '%m/%d/%Y')
            return True
        except ValueError as e:
            if 'does not match format' in str(e):
                return False

    def _get_from(self, prev=list(), nxt=list()):
        frm = raw_input("What account funded the transaction?: ")
        frm = self._detect_account(frm)
        frm = self._detect_income(frm)
        self._interpret_result(previous_steps=prev, current_step=self._get_from, next_steps=nxt,
                               validation=self._validate_from, info=frm, key=self.INFO_KEYS['From'])

    def _detect_income(self, frm):
        if frm in self.ACCOUNTS or frm in self.KEYWORDS:
            return frm

        yn = self._get_yn_response("Is this transaction income?")
        if yn in self.KEYWORDS:
            return self._back_to_repeat(yn)
        if yn == 'n':
            return 'repeat'
        return frm

    def _detect_account(self, frm):
        if frm in self.ACCOUNTS or frm in self.KEYWORDS:
            return frm

        distances = [editdistance.eval(frm, account) for account in self.ACCOUNTS]
        for account, distance in zip(self.ACCOUNTS, distances):
            if self._similar_to_an_account(frm, account, distance):
                yn = self._get_yn_response("Did you mean: %s?" % account)
                if yn in self.KEYWORDS:
                    return self._back_to_repeat(yn)
                if yn == 'y':
                    return account
        return frm

    @staticmethod
    def _similar_to_an_account(frm, account, distance):
        if distance <= max(abs(len(frm) - len(account)) - 1, min(len(frm), len(account)) / 2):
            return True
        if account in frm or frm in account:  # Eschewing return "a in b or b in a" format for clarity.
            return True
        return False

    @staticmethod
    def _validate_from(frm):
        if frm:
            return True
        return False

    def _get_to(self, prev=list(), nxt=list()):
        to = raw_input("What account received the transaction?: ")
        to = self._detect_account(to)
        self._interpret_result(previous_steps=prev, current_step=self._get_to, next_steps=nxt,
                               validation=self._validate_to, info=to, key=self.INFO_KEYS['To'])

    def _validate_to(self, to):
        frm = self.INFORMATION['From']
        if to == frm:
            return False
        if to not in self.ACCOUNTS and frm not in self.ACCOUNTS:
            return False
        return True

    def _get_memo(self, prev=list(), nxt=list()):
        memo = raw_input("Enter memo for transaction: ")
        self._interpret_result(previous_steps=prev, current_step=self._get_memo, next_steps=nxt,
                               validation=self._validate_memo, info=memo, key=self.INFO_KEYS['Memo'])

    @staticmethod
    def _validate_memo(memo):
        if memo:
            return True
        return False

    def _get_amount(self, prev=list(), nxt=list()):
        amount = raw_input("Enter amount of transaction: ")
        self._interpret_result(previous_steps=prev, current_step=self._get_amount, next_steps=nxt,
                               validation=self._validate_amount, info=amount, key=self.INFO_KEYS['Amount'])

    @staticmethod
    def _validate_amount(amount):
        try:
            amount = float(amount)
        except Exception as e:
            if "could not convert" in str(e) or "invalid literal" in str(e):
                return False
        if amount > 0:
            return True
        return False

    def _get_categories(self, prev=list(), nxt=list()):
        if self.INFORMATION['From'] in self.ACCOUNTS and self.INFORMATION['To'] in self.ACCOUNTS:
            cat = 'Transfer'
        else:
            cat = raw_input("Enter category, or 'done' to stop categorizing: ").strip(' ')
        level, prev = self._check_back_categories(cat, prev, return_level=True)
        if level > 1 and \
                self.INFORMATION['From'] in self.ACCOUNTS and self.INFORMATION['To'] in self.ACCOUNTS:
            cat = 'done'
        cat = self._infer_category(cat, level)
        nxt = self._determine_categorization_finish(cat, nxt)
        key = self._determine_categorization_key(cat, level)
        self._interpret_result(previous_steps=prev, current_step=self._get_categories, next_steps=nxt,
                               validation=self._validate_categories, info=cat, key=key)

    def _check_back_categories(self, cat, prev, return_level=False):
        # This function counts the number of times the `get_categories` function was used.
        # If cat is "back", then it will remove all but one of these instances from the list of
        #  previously visited functions.
        # If return_level is true, it will return one more than the number of times the `get_categories`
        #  function was used.
        # It will always return the list of previously visited functions. 
        level = 1
        for key in self.INFORMATION.keys():
            if 'Category' in key:
                if cat == 'back':
                    del self.INFORMATION[key]
                else:
                    level += 1
        if cat == 'back':
            prev = [fun for fun in prev if fun != self._get_categories]
        if return_level:
            return level, prev
        return prev

    def _determine_categorization_finish(self, cat, nxt):
        if cat in ['done', 'back']:
            return nxt
        return [self._get_categories] + nxt

    def _determine_categorization_key(self, cat, level):
        if cat == 'done':
            return ''
        return '%s%s' % (self.INFO_KEYS['Category'], str(level))

    @staticmethod
    def _validate_categories(cat):
        return True

    def _confirm(self, prev=list(), nxt=list()):
        max_category, prev = self._check_back_categories('', prev, return_level=True)
        print 'Date:', self.INFORMATION['Date']
        print 'From:', self.INFORMATION['From']
        print 'To:', self.INFORMATION['To']
        print 'Memo:', self.INFORMATION['Memo']
        print 'Amount:', self.INFORMATION['Amount']
        for number in range(1, max_category):
            print 'Category%s:' % number, self.INFORMATION['Category%s' % number]
        yn = self._get_yn_response('Is this correct?')
        if yn == 'n':
            yn = 'back'
            re_append = prev[len(prev) - 1] == self._get_categories
            prev = self._check_back_categories(yn, prev)
            if re_append:
                prev.append(self._get_categories)
        self._interpret_result(previous_steps=prev, current_step=self._confirm, next_steps=nxt,
                               validation=self._validate_confirmation, info=yn, key='')

    @staticmethod
    def _validate_confirmation(conf):
        if conf == 'y':
            return True
        return False

    def _save(self, prev=list(), nxt=list()):
        name_decorator = 1
        name = self.INFORMATION[self.INFO_KEYS['Date']].replace('/', '-') + \
            self.INFORMATION[self.INFO_KEYS['From']] + '_' + \
            self.INFORMATION[self.INFO_KEYS['To']] + str(name_decorator)
        while name + str(name_decorator) + '.json' in os.listdir('./transactions/unreconciled/'):
            name_decorator += 1
        name = name.replace('/', '_') + str(name_decorator) + '.json'
        with open(os.path.join('./transactions/unreconciled/', name), 'w') as f:
            json.dump(self.INFORMATION, f)
        self._interpret_result(previous_steps=prev, current_step=self._save, next_steps=nxt,
                               validation=self._validate_save, info='', key='')

    @staticmethod
    def _validate_save(info):
        return True

    @staticmethod
    def _back_to_repeat(keyword):
        if keyword == 'back':
            return 'repeat'
        return keyword

    def _get_yn_response(self, message):
        yn = 'z'
        while yn not in ['y', 'n'] and yn not in self.KEYWORDS:
            yn = raw_input(message + ' (y/n): ').lower()
        return yn

    def _infer_category(self, cat, level):
        if self.OTHER_TRANSACTIONS.empty:
            return cat
        if cat.capitalize() in list(self.OTHER_TRANSACTIONS['Category{}'.format(str(level))]) and \
                cat != cat.capitalize():
            yn = self._get_yn_response("Did you mean {}? ".format(cat.capitalize()))
            if yn == 'y':
                return cat.capitalize()
            if yn in self.KEYWORDS:
                return yn
        return cat
