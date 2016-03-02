#!/usr/bin/env python

from __future__ import print_function

import os
import cgi
import MySQLdb
import Cookie

from collections import namedtuple


def process_input():
    # Load email and password from cookie
    cookie = Cookie.SimpleCookie(os.environ.get("HTTP_COOKIE"))

    email = cookie["email"].value if "email" in cookie else None
    password = cookie["password"].value if "password" in cookie else None

    generate_output(email, password)


def generate_output(email, password):
    if not email or not password:
        print("Location: signin.py")
        print()
        return

    db_connection = MySQLdb.connect(host="localhost", user="root",
                                    passwd="1234", db="yagra")
    db_cursor = db_connection.cursor()

    UserInformation = namedtuple("UserInformation", "email, password")

    # Fetch user information from database
    db_cursor.execute("""SELECT email, password
                         FROM users
                         WHERE email = %s""", (email, ))
    record = db_cursor.fetchone()

    # Could not find this user
    if not record:
        print("Location: signin.py")
        print()
        return

    user_info = UserInformation._make(record)

    # Wrong password
    if password != user_info.password:
        print("Location: signin.py")
        print()
        return

    # Valid email and password
    db_cursor.execute("""UPDATE users
                         SET image = NULL
                         WHERE email = %s""", (email, ))
    db_connection.commit()

    print("Location: home.py")
    print()


try:
    process_input()
except:
    cgi.print_exception()
