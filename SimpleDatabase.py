#!/usr/bin/env python
import argparse
import sys
import copy


class Database(object):
    """
    A database of transactions that manipulate
    data objects within a greater database.
    Data not within a Begin block are auto-committed.
    """

    def __init__(self, vals={}):
        self.transactions = [Transaction(vals)]
        self.current_transaction = self.transactions[-1]
        self.data = self.current_transaction.data

    # Reset the current transaction to be last in the stack.
    def set_new_current_transaction(self):
        if len(self.transactions) <= 0:
            print "NO TRANSACTION"
        else:
            self.current_transaction = self.transactions[-1]

    # Begin a new transaction and append to list.
    def begin_new_transaction(self):
        self.current_transaction = Transaction(copy.deepcopy(self.data.values))
        self.transactions.append(self.current_transaction)

    # Undo all the changes made in the current transaction block.
    def rollback(self):
        # cannot roll back current/main transaction.
        if len(self.transactions) == 1:
            print "NO TRANSACTION"
        else:
            self.transactions.pop()
            self.set_new_current_transaction()

    # Commit all current open transactions.
    def commit(self):
        if len(self.transactions) == 1:
            print "NO TRANSACTION"
        for i in range(1, len(self.transactions)):
            self.data.update(self.transactions[i].commit())
        self.transactions = [self.transactions[0]]
        self.set_new_current_transaction()

class Transaction(object):
    """
    Transaction object containing own set of database values.
    """
    def __init__ (self, values):
        self.data = Data(values)

    # Commiting the transaction returns its updated values.
    def commit(self):
        return self.data


class Data(object):
    """
    Data class to hold a dictionary of database values and
    data commands.
    """
    def __init__(self, values):
        self.values = values

    # Set a value to a key.
    def set(self, key, val):
        self.values[key] = val

    # Get a value of a key.
    def get(self, key):
        val = self.values.get(key)
        if not val:
            print "NULL"
        else:
            print val

    # Remove a key/value.
    def unset(self, key):
        if key not in self.values.keys():
            print "%s not in database." % (key)
        else:
            del self.values[key]

    # Return number of keys that have specified value.
    def num_equal_to(self, value):
        counter = 0
        for k, v in self.values.iteritems():
            if v == value:
                counter +=1
        print counter

    # Update a data object with values of another.
    def update(self, data2):
        self.values.update(data2.values)

# Execute commands while there are new commands / not exited.
def execute_commands(db):
    new_command = next_command()
    while(new_command):
        parse_command(new_command, db)
        new_command = next_command()

# Parse the command for key word
def parse_command(command, db):
    if command == None:
        raise Exception("Invalid command.")
    command = command.strip().split(" ")
    run_command(command[0], command, db)


# Grab the next command from stdin.
def next_command():
    return sys.stdin.readline()

# Essential switch statement for mapping commands to functions.
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
        print "Invalid command."

# Create database then run commands within it.
def main():
    db = Database()
    execute_commands(db)
    return

if __name__ == '__main__':
    main()

