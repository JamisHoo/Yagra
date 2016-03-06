#!/usr/bin/env python

from __future__ import print_function

import string
import cgi
import MySQLdb


def process_input():
    # Load token
    form = cgi.FieldStorage()

    activate_token = form.getfirst("token")

    generate_output(activate_token)


def generate_output(token):
    # Token is not provided or not follows the format
    if (not token or len(token) != 64 or
            any(c not in string.hexdigits for c in token)):
        print("Content-type: text/html")
        print()
        print("Where's token?")
        return

    db_connection = MySQLdb.connect(host="localhost", user="root",
                                    passwd="1234", db="yagra")
    db_cursor = db_connection.cursor()
    
    # Find this token in db
    db_cursor.execute("""SELECT email
                         FROM users
                         WHERE activate_token = %s""", (token.decode("hex"),))
    record = db_cursor.fetchone()

    # Token not found
    if not record:
        print("Content-type: text/html")
        print()
        print("Invalid token")
        return
    
    email = record[0]
    
    db_cursor.execute("""UPDATE users
                         SET activate_token = NULL 
                         WHERE email = %s""", (email,))
    db_connection.commit()

    print("Content-type: text/html")
    print()
    print("Account activation successful")


try:
    process_input()
except:
    cgi.print_exception()
