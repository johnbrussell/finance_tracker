from services import setup_directories


class FinancialRecords:
    def __init__(self):
        setup_directories.setup_directories()

    def interact_with_user(self):
        action = 'initial'
        prompt = 'What function would you like to perform?'
        while action != 'quit':
            action = input(prompt).lower()
            prompt = 'Available actions are: \n' \
                '"quit": exit.\n'
