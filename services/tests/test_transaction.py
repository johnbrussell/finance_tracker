import unittest
from services.transactions import Transaction


class TestTransactions(unittest.TestCase):
    ACCOUNTS = ['TestAccount']
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


if __name__ == "__main__":
    unittest.main()
