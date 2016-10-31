## Requirements
To run, python2.7+ must be installed.

For test, make sure to `pip install` `mock` and `pytest`

## Running
With a file:
```
python SimpleDatabase.py < <filename>
```
or inputted commands:
```python SimpleDatabase.py
SET a 1
GET a
<other commands>
END
```

## Testing
```pytest tests```

# Sample Database Solution
SimpleDatabase is an in-memory database similar to Redis. It receives commands via standard input (stdin), writes appropriate responses to standard output (stdout).

### Data Commands

SimpleDatabase accepts the following commands:
```
SET name value – Set the variable name to the value value. Neither variable names nor values will contain spaces.
GET name – Print out the value of the variable name, or NULL if that variable is not set.
UNSET name – Unset the variable name, making it just like that variable was never set.
NUMEQUALTO value – Print out the number of variables that are currently set to value. If no variables equal that value, print 0.
END – Exit the program. Your program will always receive this as its last command.
```

Commands are fed to the program one at a time, with each command on its own line. All output ends with a newline. Here are some example command sequences:
```
INPUT       OUTPUT
SET ex 10   10
GET ex
UNSET ex
GET ex      NULL
END
```

### Transaction Commands

The program also supports database transactions by also implementing these commands:
```
BEGIN – Open a new transaction block. Transaction blocks can be nested; a BEGIN can be issued inside of an existing block.
ROLLBACK – Undo all of the commands issued in the most recent transaction block, and close the block. Print nothing if successful, or print NO TRANSACTION if no transaction is in progress.
COMMIT – Close all open transaction blocks, permanently applying the changes made in them. Print nothing if successful, or print NO TRANSACTION if no transaction is in progress.
```

Any data command that is run outside of a transaction block commits immediately.
