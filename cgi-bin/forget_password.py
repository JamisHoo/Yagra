#!/usr/bin/env python

from __future__ import print_function

from common import config
from common.response import text_response, populate_html, redirect

import os
import time
import cgi
import MySQLdb
import smtplib


def process_input():
    # Load email address
    form = cgi.FieldStorage()

    email = form.getfirst("email")

    generate_output(email)


def generate_output(email):
    # Email is not provided
    if not email:
        message_body = populate_html("forget_password.html")
        print(text_response("text/html", message_body))
        return

    db_connection = MySQLdb.connect(
        host=config.mysql_host, user=config.mysql_user,
        passwd=config.mysql_password, db=config.mysql_db)
    db_cursor = db_connection.cursor()

    db_cursor.execute("""SELECT email FROM users WHERE email=%s""", (email,))
    record = db_cursor.fetchone()

    # Could not find this user
    if not record:
        print(text_response("text/plain", "Account not found"))
        return

    # Else generate a random token for resetting password
    # This token expires after a period of time or after it's used
    # This token also expires after the user logs in or requests another token
    token = os.urandom(config.password_reset_token_length)
    token_expires = int(time.time()) + config.password_reset_token_expires

    db_cursor.execute("""UPDATE users
                         SET reset_passwd_token = %s,
                             reset_passwd_token_expires = %s
                         WHERE email = %s""",
                      (token, token_expires, email))
    db_connection.commit()

    # Send an email to the user
    reset_password_link = "{}reset_password.py?token={}".format(
        config.my_entire_url, token.encode("hex").upper())

    email_content = populate_html("reset_password.email",
                                  dict(link=reset_password_link))

    smtp_server = smtplib.SMTP(config.smtp_host)
    smtp_server.sendmail(config.email_from, email, email_content)
    smtp_server.quit()

    print(text_response("text/plain", "Password reset email sent"))


try:
    process_input()
except:
    cgi.print_exception()
