import unittest
from services.transactions import Transaction


class TestTransactions(unittest.TestCase):
    ACCOUNTS = ['TestAccount', 'AnotherTestAccount']
    TRANSACTION = Transaction(accounts=ACCOUNTS)

    def test_account_check(self):
        checked_accounts = self.TRANSACTION._check_accounts(self.ACCOUNTS)
        self.assertEqual('TestAccount', checked_accounts[0])
        self.assertRaises(ValueError, self.TRANSACTION._check_accounts, ['back'])

    def test_validate_date(self):
        dates = ['8/1/2017', '8/1/17', '08/01/2017', '08/1/17', '8_1/2017', '8-1_17']
        notdates = ['08012017', 'August 1, 2017', 'string']  # Note: raw_input() always returns a string.
        for date in dates:
            self.assertTrue(self.TRANSACTION._validate_date(date))
        for date in notdates:
            self.assertFalse(self.TRANSACTION._validate_date(date))

    def test_validate_from(self):
        self.assertFalse(self.TRANSACTION._validate_from(''))
        self.assertTrue(self.TRANSACTION._validate_from('any_input'))

    def test_validate_to(self):
        self.TRANSACTION.INFORMATION = {"From": 'TestAccount'}
        self.assertFalse(self.TRANSACTION._validate_to('TestAccount'))
        self.assertTrue(self.TRANSACTION._validate_to('NotAnAccount'))
        self.assertTrue(self.TRANSACTION._validate_to('AnotherTestAccount'))

        self.TRANSACTION.INFORMATION = {"From": 'NotAnAccount'}
        self.assertFalse(self.TRANSACTION._validate_to('AlsoNotAnAccount'))
        self.assertTrue(self.TRANSACTION._validate_to('TestAccount'))

    def test_validate_memo(self):
        self.assertFalse(self.TRANSACTION._validate_memo(''))
        self.assertTrue(self.TRANSACTION._validate_memo('any_input'))

    def test_validate_amount(self):
        self.assertFalse(self.TRANSACTION._validate_amount(-1))
        self.assertFalse(self.TRANSACTION._validate_amount(0))
        self.assertFalse(self.TRANSACTION._validate_amount("One Hundred"))


if __name__ == "__main__":
    unittest.main()
