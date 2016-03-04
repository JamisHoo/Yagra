#!/usr/bin/env python

from __future__ import print_function

from common import populate_html

import os
import hashlib
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

    # TODO: move MySQL info to config file
    db_connection = MySQLdb.connect(host="localhost", user="root",
                                    passwd="1234", db="yagra")
    db_cursor = db_connection.cursor()

    UserInformation = namedtuple(
        "UserInformation", 
        "email, salt, password_hash, random_password_hash")

    # Fetch user information from database
    db_cursor.execute("""SELECT email, salt, passwd_hash, random_passwd_hash
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

    # Note that both salt and hash are in binary form
    # Note that salt is in binary form 
    # while password is in ascii or hexadecimal text
    input_password_hash = hashlib.sha256(user_info.salt + password).digest()

    # Wrong password
    if (input_password_hash != user_info.password_hash and 
            input_password_hash != user_info.random_password_hash):
        print("Content-type: text/html")
        print(cookie)
        print()
        print(populate_html("signin.html", dict(email=email)))
        return

    # Else login successful

    # If signin by password
    if input_password_hash == user_info.password_hash:
        # Generate a new random password as cookie and invalidate the old one
        # TODO: random password expires some time later
        # TODO: move constants to config file
        random_password = os.urandom(32).encode("hex").upper()

        random_password_hash = (
            hashlib.sha256(user_info.salt + random_password).digest())

        db_cursor.execute("""UPDATE users 
                             SET random_passwd_hash = %s
                             WHERE email = %s""", 
                          (random_password_hash, email))
        db_connection.commit()

        cookie["password"] = random_password
        cookie["password"]["expires"] = 60

    print("Location: home.py")
    print(cookie)
    print()


try:
    process_input()
except:
    cgi.print_exception()
