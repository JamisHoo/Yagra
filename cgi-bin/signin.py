#!/usr/bin/env python

from __future__ import print_function
from collections import namedtuple

from common import config
from common.response import text_response, populate_html, redirect

import os
import hashlib
import cgi
import MySQLdb
import Cookie


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

    request_method = os.environ.get("REQUEST_METHOD")

    generate_output(email, password, request_method)


def generate_output(email, password, request_method):
    # Email is not provided
    if not email:
        if request_method == "POST":
            print(text_response("text/plain", "Empty email"))
        else:
            print(text_response("text/html", populate_html("signin.html")))
        return

    cookie = Cookie.SimpleCookie()
    cookie["email"] = email

    # Password is not provided
    if not password:
        if request_method == "POST":
            print(text_response("text/plain", "Empty password", cookie))
        else:
            message_body = populate_html("signin.html", dict(email=email))
            print(text_response("text/html", message_body, cookie))
        return

    db_connection = MySQLdb.connect(
        host=config.mysql_host, user=config.mysql_user,
        passwd=config.mysql_password, db=config.mysql_db)
    db_cursor = db_connection.cursor()

    UserInformation = namedtuple(
        "UserInformation",
        """email, salt, password_hash, random_password_hash, activated,
           resetting_password""")

    # Fetch user information from database
    db_cursor.execute("""SELECT email, salt, passwd_hash, random_passwd_hash,
                                ISNULL(activate_token),
                                NOT ISNULL(reset_passwd_token)
                         FROM users
                         WHERE email = %s""", (email,))
    record = db_cursor.fetchone()

    # Couldn't find this user
    if not record:
        print(text_response("text/plain", "Account not found", cookie))
        return

    user_info = UserInformation._make(record)

    # User signed up but not yet activted
    if not user_info.activated:
        print(text_response("text/plain", "Account not activated yet", cookie))
        return

    # Note that salt is in binary form
    # while password is in ascii or hexadecimal text
    input_password_hash = hashlib.sha256(user_info.salt + password).digest()

    # Wrong password
    if (input_password_hash != user_info.password_hash and
            input_password_hash != user_info.random_password_hash):
        if request_method == "POST":
            print(text_response("text/plain", "Wrong password", cookie))
        else:
            message_body = populate_html("signin.html", dict(email=email))
            print(text_response("text/html", message_body, cookie))
        return

    # Else login successful

    # If signin by password
    if input_password_hash == user_info.password_hash:
        # Generate a new random password as cookie and invalidate the old one
        random_password = (
            os.urandom(config.random_password_length).encode("hex").upper())

        random_password_hash = (
            hashlib.sha256(user_info.salt + random_password).digest())

        db_cursor.execute("""UPDATE users
                             SET random_passwd_hash = %s
                             WHERE email = %s""",
                          (random_password_hash, email))
        db_connection.commit()

        cookie["password"] = random_password
        cookie["password"]["expires"] = config.random_password_expires

        # Invalidate the token if this user is resetting password
        if user_info.resetting_password:
            db_cursor.execute("""UPDATE users
                                 SET reset_passwd_token = NULL,
                                     reset_passwd_token_expires = NULL
                                 WHERE email = %s""",
                              (email,))
            db_connection.commit()

    print(redirect("home.py", cookie))


try:
    process_input()
except:
    cgi.print_exception()
