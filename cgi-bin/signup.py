#!/usr/bin/env python

from __future__ import print_function

from common import populate_html

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

    generate_output(email, password)


def generate_output(email, password):
    # Email is not provided
    if not email:
        print("Content-type: text/html")
        print()
        print(populate_html("signup.html", {}))
        return
    
    # Password is not provided
    if not password:
        print("Content-type: text/html")
        print()
        print(populate_html("signup.html", {}))
        return

    # Insert new user info into database
    db_connection = MySQLdb.connect(host="localhost", user="root",
                                    passwd="1234", db="yagra")
    db_cursor = db_connection.cursor()

    email_hash = hashlib.md5(email).digest()
    salt = os.urandom(32)
    password_hash = hashlib.sha256(salt + password).digest()
    activate_token = os.urandom(32)
    
    # TODO: check activate token field when signing in and resetting password
    # TODO: Handle primary key duplicate
    try:
        db_cursor.execute(
            """INSERT INTO users 
            (email, email_hash, activate_token, salt, passwd_hash)
            VALUES (%s, %s, %s, %s, %s)""",
            (email, email_hash, activate_token, salt, password_hash))
        db_connection.commit()
    except MySQLdb.IntegrityError:
        print("Content-type: text/html")
        print()
        print("Email already used")
        return
    
    # Send an activate email
    from_addr = "jamis@test.jamis.xyz"
    activate_link = "http://121.42.28.81/cgi-bin/activate.py?token=%s" % activate_token.encode("hex").upper()
    email_content = populate_html("activate.email", dict(link = activate_link))

    smtp_server = smtplib.SMTP("localhost")
    smtp_server.sendmail(from_addr, email, email_content);
    smtp_server.quit()
    
    print("Content-type: text/html")
    print()
    print("Activate email sent")


try:
    process_input()
except:
    cgi.print_exception()
