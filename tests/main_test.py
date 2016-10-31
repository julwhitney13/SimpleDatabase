#!/usr/bin/env python
import SimpleDatabase
import mock
import sys
import unittest

from cStringIO import StringIO
from contextlib import contextmanager
from mock import patch
from SimpleDatabase import *

# Helper for capturing stdout. 
@contextmanager
def capture(command, *args, **kwargs):
  out, sys.stdout = sys.stdout, StringIO()
  try:
    command(*args, **kwargs)
    sys.stdout.seek(0)
    yield sys.stdout.read()
  finally:
    sys.stdout = out

class DataTests(unittest.TestCase):
    """
    Unit tests for Data class.
    """

    def setUp(self):
        self.sample_data = Data({})

    def test_set(self):
        self.sample_data.set("A", "1")
        self.assertEqual(self.sample_data.values.get("A"), "1")

    def test_get(self):
        self.sample_data.set("A", "1")
        with capture(self.sample_data.get, "A") as out:
            self.assertEqual(out, "1\n")

    def test_get_null(self):
        with capture(self.sample_data.get, "A") as out:
            self.assertEqual(out, "NULL\n")

    def test_num_equal_to(self):
        self.sample_data.set("B", "1")
        self.sample_data.set("C", "1")

        with capture(self.sample_data.num_equal_to, "1") as out:
            self.assertEqual(out, "2\n")

    def test_num_equal_to_none(self):
        with capture(self.sample_data.num_equal_to, "8") as out:
            self.assertEqual(out, "0\n")

    def test_unset(self):
        self.sample_data.set("A", "1")
        with capture(self.sample_data.get, "A") as out:
            self.assertEqual(out, "1\n")
        self.sample_data.unset("A")
        with capture(self.sample_data.get, "A") as out:
            self.assertEqual(out, "NULL\n")

    def test_unset_error(self):
        with capture(self.sample_data.unset, "A") as out:
            self.assertEqual(out, "A not in database.\n")

    def test_update(self):
        d1 = Data({"A":"1"})
        d2 = Data({"B":"2"})
        d1.update(d2)
        self.assertEqual(d1.values, {"A":"1", "B":"2"})

class TransactionTests(unittest.TestCase):
    """
    Unit tests for Transaction object.
    """

    def setUp(self):
        self.transaction = Transaction({})

    def test_data_manip(self):
        self.transaction.data.set("A", "1")
        self.assertEqual(self.transaction.data.values, {"A":"1"})

    def test_commit_returns_values(self):
        self.transaction.data.set("A", "1")
        self.assertEqual(self.transaction.commit().values, {"A":"1"})

class DatabaseTests(unittest.TestCase):
    """
    Unit tests for database class.
    """

    def setUp(self):
        self.db = Database()

    def test_set_new_current_transaction(self):
        t2 = Transaction({"a":"1"})
        self.db.transactions = [Transaction({}), t2]
        self.db.set_new_current_transaction()
        self.assertEqual(self.db.current_transaction, t2)

    def test_set_new_current_transaction(self):
        self.db.transactions = []
        self.db.set_new_current_transaction()
        with capture(self.db.set_new_current_transaction) as out:
            self.assertEqual(out, "NO TRANSACTION\n")

    def test_begin_new_transaction(self):
        self.assertEqual(len(self.db.transactions), 1)
        current = self.db.current_transaction
        self.db.begin_new_transaction()
        self.assertEqual(len(self.db.transactions), 2)
        next = self.db.current_transaction
        self.assertNotEqual(current, next)

    def test_rollback(self):
        transactions = self.db.transactions
        self.db.begin_new_transaction()
        self.db.rollback()
        self.assertEqual(self.db.transactions, transactions)

    def test_rollback_cannot(self):
        with capture(self.db.rollback) as out:
            self.assertEqual(out, "NO TRANSACTION\n")

    def test_commit(self):
        self.db.begin_new_transaction()
        self.db.begin_new_transaction()
        self.assertEqual(len(self.db.transactions), 3)
        self.db.commit()
        self.assertEqual(len(self.db.transactions), 1)

    def test_commit_none(self):
        with capture(self.db.commit) as out:
            self.assertEqual(out, "NO TRANSACTION\n")


class TestGeneralMethods(unittest.TestCase):
    """
    Tests for public functions.
    """

    def setUp(self):
        self.db = mock.Mock()

    def test_run_command_set(self):
        run_command("SET", ["SET", "a", "1"], self.db)
        self.db.current_transaction.data.set.assert_called_once_with("a", "1")

    def test_run_command_get(self):
        run_command("GET", ["GET", "a"], self.db)
        self.db.current_transaction.data.get.assert_called_once_with("a")

    def test_run_command_unset(self):
        run_command("UNSET", ["UNSET", "a"], self.db)
        self.db.current_transaction.data.unset.assert_called_once_with("a")

    def test_run_command_num_equal_to(self):
        run_command("NUMEQUALTO", ["NUMEQUALTO", "a"], self.db)
        self.db.current_transaction.data.num_equal_to.assert_called_once_with("a")

    def test_run_command_end(self):
        self.assertRaises(SystemExit, run_command, "END", ["END"], self.db)

    def test_run_command_begin(self):
        run_command("BEGIN", ["BEGIN"], self.db)
        self.db.begin_new_transaction.assert_called_once_with()

    def test_run_command_rollback(self):
        run_command("ROLLBACK", ["ROLLBACK"], self.db)
        self.db.rollback.assert_called_once_with()

    def test_run_command_commit(self):
        run_command("COMMIT", ["COMMIT"], self.db)
        self.db.commit.assert_called_once_with()

    def test_run_command_no_command(self):
        with capture(run_command, "IDK", ["IDK"], self.db) as out:
            self.assertEqual(out, "Invalid command.\n")

    def test_next_command(self):
        sys.stdin = StringIO("ayy\n")
        self.assertEqual("ayy\n", next_command())

    def test_parse_command(self):
        parse_command("SET a 1", self.db)
        self.db.current_transaction.data.set.assert_called_once_with("a","1")

    def test_parse_command_none(self):
        self.assertRaises(Exception, parse_command, None, self.db)

    def test_execute_commands(self):
        sys.stdin = StringIO("ROLLBACK\n")
        execute_commands(self.db)
        self.db.rollback.assert_called_once_with()
