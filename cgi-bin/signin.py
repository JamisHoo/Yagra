#!/usr/bin/env python

from __future__ import print_function

from common import populate_html

import os
import cgi
import MySQLdb
import Cookie

from collections import namedtuple


def process_input():
    # Load email and password from form
    form = cgi.FieldStorage()

    email = form.getfirst("email")
    password = form.getfirst("password")

    # Load email and password from cookie
    cookie = Cookie.SimpleCookie(os.environ.get("HTTP_COOKIE"))

    if not email and "email" in cookie:
        email = cookie["email"].value

    if email and not password and "password" in cookie:
        password = cookie["password"].value

    generate_output(email, password)


def generate_output(email, password):
    # Email is not provided
    if not email:
        print("Content-type: text/html")
        print()
        # TODO: print prompt info
        print(populate_html("signin.html", {}))
        return

    cookie = Cookie.SimpleCookie()
    cookie["email"] = email

    # Password is not provided
    if not password:
        print("Content-type: text/html")
        print(cookie)
        print()
        # TODO: print prompt info
        print(populate_html("signin.html", dict(email=email)))
        return

    # TODO: package db-select operation to a separate function
    # TODO: move MySQL info to config file
    db_connection = MySQLdb.connect(host="localhost", user="root",
                                    passwd="1234", db="yagra")
    db_cursor = db_connection.cursor()

    UserInformation = namedtuple("UserInformation", "email, password")

    # Fetch user information from database
    db_cursor.execute("""SELECT email, password
                         FROM users
                         WHERE email = %s""", (email,))
    record = db_cursor.fetchone()

    # Couldn't find this user
    if not record:
        print("Content-type: text/html")
        print(cookie)
        print()
        print(populate_html("signin.html", dict(email=email)))
        return

    user_info = UserInformation._make(record)

    # Wrong password
    if password != user_info.password:
        print("Content-type: text/html")
        print(cookie)
        print()
        print(populate_html("signin.html", dict(email=email)))
        return

    # Login successful
    cookie["password"] = password
    # TODO: move expire time to config file
    cookie["password"]["expires"] = 60
    print("Location: home.py")
    print(cookie)
    print()


try:
    process_input()
except:
    cgi.print_exception()
