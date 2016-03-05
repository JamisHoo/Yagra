#!/usr/bin/env python

from __future__ import print_function

from common import populate_html

import os
import time
import string
import hashlib
import cgi
import MySQLdb

from collections import namedtuple


def process_input():
    # Load token
    form = cgi.FieldStorage()

    token = form.getfirst("token")
    password = form.getfirst("password")

    generate_output(token, password)


def generate_output(token, password):
    if (not token or len(token) != 64 or
            any(c not in string.hexdigits for c in token)):
        print("Content-type: text/html")
        print()
        print("Invalid token")
        return

    if not password:
        print("Content-type: text/html")
        print()
        print(populate_html("reset_password.html", dict(token=token)))
        return

    db_connection = MySQLdb.connect(host="localhost", user="root",
                                    passwd="1234", db="yagra")
    db_cursor = db_connection.cursor()

    TokenInformation = namedtuple("TokenInformation",
                                  "email, salt, token, token_expires")

    # Fetch token from database
    db_cursor.execute("""SELECT email, salt, reset_passwd_token,
                                reset_passwd_token_expires
                         FROM users
                         WHERE reset_passwd_token = %s""",
                      (token.decode("hex"),))
    record = db_cursor.fetchone()

    # Could not find this token
    if not record:
        print("Content-type: text/html")
        print()
        print("Invalid token")
        return

    token_info = TokenInformation._make(record)

    if token_info.token_expires < int(time.time()):
        print("Content-type: text/html")
        print()
        print("Token expired")
        return

    # Else reset salt and password
    new_salt = os.urandom(32)
    password_hash = hashlib.sha256(new_salt + password).digest()

    db_cursor.execute("""UPDATE users
                         SET salt = %s, passwd_hash = %s,
                             random_passwd_hash = NULL,
                             reset_passwd_token = NULL,
                             reset_passwd_token_expires = NULL
                         WHERE email = %s""",
                      (new_salt, password_hash, token_info.email))
    db_connection.commit()

    print("Content-type: text/html")
    print()
    print("Reset successful")


try:
    process_input()
except:
    cgi.print_exception()
