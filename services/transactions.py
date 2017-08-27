from datetime import datetime
import editdistance


class Transaction:
    KEYWORDS = [
        'back',
        'repeat',
        'cancel',
        'quit'
    ]

    def __init__(self, accounts):
        self.INFORMATION = dict()
        self.ACCOUNTS = [account.lower() for account in accounts]

    def __create_process(self):
        self.__PROCESS = [
            self.__get_date,
            self.__get_from,
            self.__get_to,
            self.__get_memo,
            self.__get_amount,
            self.__get_categories,
            self.__confirm,
            self.__save
        ]

    def create_new_transaction(self):
        self.__create_process()
        self.__run_process()

    def __run_process(self):
        print "Enter 'back' to return to the prior step; 'cancel' to cancel the new transaction."
        self.__PROCESS[0](prev=list(), nxt=self.__PROCESS[1:])

    def __interpret_result(self, previous_steps, current_step, next_steps, validation, info, key, **kwargs):
        if info.lower() not in self.KEYWORDS:
            validation = validation(info, kwargs) if kwargs else validation(info)
            if validation:
                self.INFORMATION[key] = info
                self.__proceed_to_next_step(prev=previous_steps, current=current_step, nxt=next_steps)
            else:
                current_step(prev=previous_steps, nxt=next_steps)
        if info == 'back':
            self.__proceed_to_prev_step(prev=previous_steps, current=current_step, nxt=next_steps)
        if info == 'repeat':
            current_step(prev=previous_steps, nxt=next_steps)

    @staticmethod
    def __proceed_to_next_step(prev, current, nxt):
        if nxt:
            prev.append(current)
            next_step = nxt[0]
            nxt = nxt[1:]
            next_step(prev=prev, nxt=nxt)

    @staticmethod
    def __proceed_to_prev_step(prev, current, nxt):
        if prev:
            current = [current]
            nxt = current + nxt
            prev_step = prev[len(prev) - 1]
            prev = prev[:-1]
            prev_step(prev=prev, nxt=nxt)

    def __get_date(self, prev=list(), nxt=list()):
        date = raw_input("Enter the date of the transaction (MM/DD/YYYY): ")
        self.__interpret_result(previous_steps=prev, current_step=self.__get_date, next_steps=nxt,
                                validation=self.__validate_date, info=date, key='Date')

    @staticmethod
    def __validate_date(date):
        date = date.replace('-', '').replace('_', '')
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

    def __get_from(self, prev=list(), nxt=list()):
        frm = raw_input("Who paid the money transacted?: ").lower()
        frm = self.__detect_account(frm)
        frm = self.__detect_income(frm)
        self.__interpret_result(previous_steps=prev, current_step=self.__get_from, next_steps=nxt,
                                validation=self.__validate_from, info=frm, key='From')

    def __detect_income(self, frm):
        if frm in self.ACCOUNTS or frm in self.KEYWORDS:
            return frm

        yn = self.__get_yn_response("Is this transaction income?")
        if yn in self.KEYWORDS:
            return self.__back_to_repeat(yn)
        if yn == 'n':
            return 'repeat'
        return frm

    def __detect_account(self, frm):
        if frm in self.ACCOUNTS or frm in self.KEYWORDS:
            return frm

        distances = [editdistance.eval(frm, account) for account in self.ACCOUNTS]
        for account, distance in zip(self.ACCOUNTS, distances):
            if distance <= max(abs(len(frm) - len(account)) - 1, min(len(frm), len(account)) / 2) or \
                    account in frm or frm in account:
                yn = self.__get_yn_response("Did you mean: %s?" % account)
                if yn in self.KEYWORDS:
                    return self.__back_to_repeat(yn)
                if yn == 'y':
                    return account

        return frm

    @staticmethod
    def __validate_from(frm):
        if frm:
            return True
        return False

    def __get_to(self, prev=list(), nxt=list()):
        to = raw_input("Who received the money transacted?: ").lower()
        to = self.__detect_account(to)
        self.__interpret_result(previous_steps=prev, current_step=self.__get_to, next_steps=nxt,
                                validation=self.__validate_from, info=to, key='To')

    def __validate_to(self, to):
        frm = self.INFORMATION['From']
        if to == frm:
            return False
        if to not in self.ACCOUNTS and frm not in self.ACCOUNTS:
            return False
        return True

    def __get_memo(self, prev=list(), nxt=list()):
        memo = raw_input("Enter memo for transaction: ")
        self.__interpret_result(previous_steps=prev, current_step=self.__get_memo, next_steps=nxt,
                                validation=self.__validate_memo, info=memo, key='Memo')

    @staticmethod
    def __validate_memo(memo):
        if memo:
            return True
        return False

    def __get_amount(self, prev=list(), nxt=list()):
        amount = raw_input("Enter amount of transaction: ")
        self.__interpret_result(previous_steps=prev, current_step=self.__get_amount, next_steps=nxt,
                                validation=self.__validate_amount, info=amount, key='Amount')

    @staticmethod
    def __validate_amount(amount):
        try:
            amount = float(amount)
        except TypeError as e:
            if "could not convert" in str(e):
                return False
        if amount > 0:
            return True
        return False

    def __get_categories(self, prev=list(), nxt=list()):
        return True

    def __confirm(self, prev=list(), nxt=list()):
        return True

    def __save(self, prev=list(), nxt=list()):
        return True

    @staticmethod
    def __back_to_repeat(keyword):
        if keyword == 'back':
            return 'repeat'
        return keyword

    def __get_yn_response(self, message):
        yn = 'z'
        while yn not in ['y', 'n'] and yn not in self.KEYWORDS:
            yn = raw_input(message + ' (y/n): ').lower()
        return yn
