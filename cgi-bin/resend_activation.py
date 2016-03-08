#!/usr/bin/env python

from __future__ import print_function
from collections import namedtuple

from common import config
from common.response import text_response, populate_html

import os
import cgi
import MySQLdb
import smtplib


def process_input():
    # Load email
    form = cgi.FieldStorage()

    email = form.getfirst("email")

    request_method = os.environ.get("REQUEST_METHOD")

    generate_output(email, request_method)


def generate_output(email, request_method):
    # Email not provided
    if not email:
        if request_method == "POST":
            print(text_response("text/plain", "Empty email"))
        else:
            print(text_response("text/html",
                                populate_html("resend_activation.html")))
        return

    db_connection = MySQLdb.connect(
        host=config.mysql_host, user=config.mysql_user,
        passwd=config.mysql_password, db=config.mysql_db)
    db_cursor = db_connection.cursor()

    UserInformation = namedtuple("UserInformation", "email, activate_token")

    # Fetch user information from db
    db_cursor.execute("""SELECT email, activate_token
                         FROM users
                         WHERE email = %s""", (email,))
    record = db_cursor.fetchone()

    # Couldn't find this user
    if not record:
        print(text_response("text/plain", "Account not found"))
        return

    user_info = UserInformation._make(record)

    # User already activated
    if not user_info.activate_token:
        print(text_response("text/plain", "Account already activated"))
        return

    # Else, resend the activate email
    activate_link = "{}activate.py?token={}".format(
        config.my_entire_url, user_info.activate_token.encode("hex").upper())

    email_content = populate_html("activate.email", dict(link=activate_link))

    smtp_server = smtplib.SMTP(config.smtp_host)
    smtp_server.sendmail(config.email_from, email, email_content)
    smtp_server.quit()

    print(text_response("text/plain", "Activation email sent"))


try:
    process_input()
except:
    cgi.print_exception()
