#!/usr/bin/env python

from __future__ import print_function

from common import config
from common.response import text_response, populate_html, redirect

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

    request_method = os.environ.get("REQUEST_METHOD")

    generate_output(token, password, request_method)


def generate_output(token, password, request_method):
    if (not token or len(token) != config.password_reset_token_length * 2 or
            any(c not in string.hexdigits for c in token)):
        print(text_response("text/plain", "Empty token"))
        return

    if not password:
        if request_method == "POST":
            print(text_response("text/plain", "Empty password"))
        else:
            message_body = populate_html("reset_password.html",
                                         dict(token=token))
            print(text_response("text/html", message_body))
        return

    db_connection = MySQLdb.connect(
        host=config.mysql_host, user=config.mysql_user,
        passwd=config.mysql_password, db=config.mysql_db)

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
        print(text_response("text/plain", "Invalid token"))
        return

    token_info = TokenInformation._make(record)

    if token_info.token_expires < int(time.time()):
        print(text_response("text/plain", "Token expired"))
        return

    # Else reset salt and password
    new_salt = os.urandom(config.salt_length)
    password_hash = hashlib.sha256(new_salt + password).digest()

    db_cursor.execute("""UPDATE users
                         SET salt = %s, passwd_hash = %s,
                             random_passwd_hash = NULL,
                             reset_passwd_token = NULL,
                             reset_passwd_token_expires = NULL
                         WHERE email = %s""",
                      (new_salt, password_hash, token_info.email))
    db_connection.commit()

    print(text_response("text/plain", "Reset successful"))


try:
    process_input()
except:
    cgi.print_exception()
