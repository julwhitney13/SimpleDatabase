#!/usr/bin/env python
import argparse
import sys
import copy

# A database full of transactions that manipulate Data objects
# default transaction does not need a commit
class Database(object):

    def __init__(self, vals={}):
        self.transactions = [Transaction(vals)]
        self.current_transaction = self.transactions[-1]
        self.data = self.current_transaction.data

    def set_new_current_transaction(self):
        if len(self.transactions) <= 0:
            print "NO TRANSACTION"
        self.current_transaction = self.transactions[-1]

    def begin_new_transaction(self):
        self.current_transaction = Transaction(copy.deepcopy(self.data.values))
        self.transactions.append(self.current_transaction)
        return self.current_transaction

    def rollback(self):
        if len(self.transactions) == 1:
            print "NO TRANSACTION"
        elif len(self.transactions) < 1:
            raise Exception("Code Error: lost transactions")
        else:
            self.transactions.pop()
            self.set_new_current_transaction()

    def commit(self):
        if len(self.transactions) == 1:
            print "NO TRANSACTION"
        for i in range(1, len(self.transactions)):
            self.data.update(self.transactions[i].commit())
        self.transactions = [self.transactions[0]]
        self.set_new_current_transaction()

class Transaction(object):

    def __init__ (self, values):
        self.data = Data(values)

    def commit(self):
        return self.data

class Data(object):

    def __init__(self, values):
        self.values = values

    def set(self, key, val):
        self.values[key] = val

    def get(self, key):
        val = self.values.get(key)
        if not val:
            print "NULL"
        else:
            print val

    def unset(self, key):
        del self.values[key]

    def num_equal_to(self, value):
        counter = 0
        for k, v in self.values.iteritems():
            if v == value:
                counter +=1
        print counter

    def update(self, data2):
        self.values.update(data2.values)


def execute_commands(db):
    new_command = next_command()
    while(new_command):
        db = parse_command(new_command, db)
        new_command = next_command()

def parse_command(command, db):
    if command == None:
        raise Exception("Invalid command")
    command = command.strip().split(" ")
    return run_command(command[0], command, db)


def next_command():
    return sys.stdin.readline()

def run_command(command, full, db):

    if command == "SET":
        db.current_transaction.data.set(full[1], full[2])
    elif command == "GET":
        db.current_transaction.data.get(full[1])
    elif command == "UNSET":
        db.current_transaction.data.unset(full[1])
    elif command == "NUMEQUALTO":
        db.current_transaction.data.num_equal_to(full[1])
    elif command == "END":
        exit()
    elif command == "BEGIN":
        db.begin_new_transaction()
    elif command == "ROLLBACK":
        db.rollback()
    elif command == "COMMIT":
        db.commit()
    else:
        print "Invalid command"
    return db

def main():
    db = Database()
    execute_commands(db)
    return

if __name__ == '__main__':
    main()

