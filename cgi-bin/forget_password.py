#!/usr/bin/env python

from __future__ import print_function

from common import populate_html

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
        print("Content-type: text/html")
        print()
        print(populate_html("forget_password.html", {}))
        return

    db_connection = MySQLdb.connect(host="localhost", user="root", 
                                    passwd="1234", db="yagra")
    db_cursor = db_connection.cursor()

    db_cursor.execute("""SELECT email FROM users WHERE email=%s""", (email,))
    record = db_cursor.fetchone()

    # Could not find this user
    if not record:
        print("Location: forget_password.py")
        print()
        return

    # Else generate a random token for resetting password 
    # This token expires after a period of time or after it's used 
    # This token also expires after the user logs in or requests another token
    # TODO: invalidate this token after the user logs in
    # TODO: move constants to config file
    token = os.urandom(32)
    token_expires = int(time.time()) + 900  # 15-min

    db_cursor.execute("""UPDATE users
                         SET reset_passwd_token = %s, 
                             reset_passwd_token_expires = %s
                         WHERE email = %s""",
                      (token, token_expires, email))
    db_connection.commit()

    # Send an email to the user
    from_addr = "jamis@test.jamis.xyz"
    reset_password_link = "http://121.42.28.81/cgi-bin/reset_password.py?&token=%s" % token.encode("hex").upper()
    email_content = populate_html("reset_password.email", 
                                  dict(link = reset_password_link))

    smtp_server = smtplib.SMTP("localhost")
    smtp_server.sendmail(from_addr, email, email_content)
    smtp_server.quit()
    
    print("Content-type: text/html")
    print()
    print("Email sent. ")


try:
    process_input()
except:
    cgi.print_exception()
