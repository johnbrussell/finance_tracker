from datetime import datetime


class Transaction:
    KEYWORDS = [
        'back',
        'cancel'
    ]

    def __init__(self):
        self.INFORMATION = dict()
        self.__create_process()
        self.__run_process()

    def __create_process(self):
        self.__PROCESS = [
            self.__get_date
            # self.__get_from,
            # self.__get_to,
            # self.__get_memo,
            # self.__get_amount,
            # self.__get_categories,
            # self.__confirm,
            # self.__save
        ]

    def __run_process(self):
        print("Enter 'back' to return to the prior step; 'cancel' to cancel the new transaction.")
        self.__PROCESS[0](prev=list(), nxt=self.__PROCESS[1:])

    def __interpret_result(self, previous_steps, current_step, next_steps, validation, info, key):
        if info.lower() not in self.KEYWORDS:
            validation = validation(info)
            if validation:
                self.INFORMATION[key] = info
                self.__proceed_to_next_step(prev=previous_steps, current=current_step, nxt=next_steps)
            else:
                current_step(prev=previous_steps, nxt=next_steps)
        if info == 'back':
            self.__proceed_to_prev_step(prev=previous_steps, current=current_step, nxt=next_steps)

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
        date = input("Enter the date of the transaction (MM/DD/YYYY): ")
        self.__interpret_result(previous_steps=prev, current_step=self.__get_date, next_steps=nxt,
                                validation=self.validate_date, info=date, key='Date')

    @staticmethod
    def validate_date(date):
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
        return True

    def __get_to(self, prev=list(), nxt=list()):
        return True

    def __get_memo(self, prev=list(), nxt=list()):
        return True

    def __get_amount(self, prev=list(), nxt=list()):
        return True

    def __get_categories(self, prev=list(), nxt=list()):
        return True

    def __save(self, prev=list(), nxt=list()):
        return True
