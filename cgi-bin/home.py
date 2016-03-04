#!/usr/bin/env python

from __future__ import print_function

from common import populate_html

import os
import cgi
import hashlib
import base64
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

    UserInformation = namedtuple(
        "UserInformation",
        """email, email_hash, salt, password_hash, random_password_hash,
           no_image""")

    # Fetch user information from database
    db_cursor.execute("""SELECT email, email_hash, salt, passwd_hash,
                                random_passwd_hash, ISNULL(image)
                         FROM users
                         WHERE email = %s""", (email,))
    record = db_cursor.fetchone()

    # Could not find this user
    if not record:
        print("Location: signin.py")
        print()
        return

    user_info = UserInformation._make(record)

    input_password_hash = hashlib.sha256(user_info.salt + password).digest()

    # Wrong password
    if (input_password_hash != user_info.password_hash and
            input_password_hash != user_info.random_password_hash):
        print("Location: signin.py")
        print()
        return

    # Valid email and password
    if user_info.no_image:
        image_url = ""
    else:
        image_url = base64.b16encode(user_info.email_hash)

    print("Content-type: text/html")
    print()
    print(populate_html("home.html", dict(email=email, image_url=image_url)))


try:
    process_input()
except:
    cgi.print_exception()
