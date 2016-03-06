#!/usr/bin/env python

from __future__ import print_function

from common import config
from common.response import text_response, populate_html, redirect

import os
import hashlib
import cgi
import MySQLdb
import smtplib


def process_input():
    # Load email and password
    form = cgi.FieldStorage()

    email = form.getfirst("email")
    password = form.getfirst("password")

    request_method = os.environ.get("REQUEST_METHOD")

    generate_output(email, password, request_method)


def generate_output(email, password, request_method):
    # Email is not provided
    if not email:
        if request_method == "POST":
            print(text_response("text/plain", "Empty email"))
        else:
            print(text_response("text/html", populate_html("signup.html")))
        return

    # Password is not provided
    if not password:
        if request_method == "POST":
            print(text_response("text/plain", "Empty password"))
        else:
            print(text_response("text/html", populate_html("signup.html")))
        return

    # Insert new user info into database
    db_connection = MySQLdb.connect(
        host=config.mysql_host, user=config.mysql_user,
        passwd=config.mysql_password, db=config.mysql_db)
    db_cursor = db_connection.cursor()

    email_hash = hashlib.md5(email).digest()
    salt = os.urandom(config.salt_length)
    password_hash = hashlib.sha256(salt + password).digest()
    activate_token = os.urandom(config.activation_token_length)

    try:
        db_cursor.execute(
            """INSERT INTO users
            (email, email_hash, activate_token, salt, passwd_hash)
            VALUES (%s, %s, %s, %s, %s)""",
            (email, email_hash, activate_token, salt, password_hash))
        db_connection.commit()
    except MySQLdb.IntegrityError:
        print(text_response("text/plain", "Email already used"))
        return

    # Send an activate email
    activate_link = "{}activate.py?token={}".format(
        config.my_entire_url, activate_token.encode("hex").upper())

    email_content = populate_html("activate.email", dict(link=activate_link))

    smtp_server = smtplib.SMTP(config.smtp_host)
    smtp_server.sendmail(config.email_from, email, email_content)
    smtp_server.quit()

    print(text_response("text/plain", "Activation email sent"))


try:
    process_input()
except:
    cgi.print_exception()
