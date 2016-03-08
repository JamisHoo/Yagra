#!/usr/bin/env python

from __future__ import print_function

from common import config
from common.response import text_response, populate_html, redirect

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
    if (not token or len(token) != config.activation_token_length * 2 or
            any(c not in string.hexdigits for c in token)):
        print(text_response("text/plain", "Invalid token"))
        return

    db_connection = MySQLdb.connect(
        host=config.mysql_host, user=config.mysql_user,
        passwd=config.mysql_password, db=config.mysql_db)
    db_cursor = db_connection.cursor()

    # Find this token in db
    db_cursor.execute("""SELECT email
                         FROM users
                         WHERE activate_token = %s""", (token.decode("hex"),))
    record = db_cursor.fetchone()

    # Token not found
    if not record:
        print(text_response("text/plain", "Invalid token"))
        return

    email = record[0]

    # activate_token == NULL means activated
    db_cursor.execute("""UPDATE users
                         SET activate_token = NULL
                         WHERE email = %s""", (email,))
    db_connection.commit()

    print(text_response("text/plain", "Account activation successful"))


try:
    process_input()
except:
    cgi.print_exception()
