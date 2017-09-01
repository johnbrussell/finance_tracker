import unittest
from services.transactions import Transaction


class TestTransactions(unittest.TestCase):
    TRANSACTION = Transaction(accounts=['TestAccount'])

