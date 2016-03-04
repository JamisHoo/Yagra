#!/usr/bin/env python

from __future__ import print_function

import os
import hashlib
import cgi
import MySQLdb
import Cookie

from collections import namedtuple


def process_input():
    # Load email and password from cookie
    cookie = Cookie.SimpleCookie(os.environ.get("HTTP_COOKIE"))

    email = cookie["email"].value if "email" in cookie else None
    password = cookie["password"].value if "password" in cookie else None

    # Load image uploaded from form
    form = cgi.FieldStorage()
    image_file = form["userfile"].file if "userfile" in form else None

    # Check whether is an empty file
    if image_file:
        image_file.seek(0, 2)  # To end of file
        if image_file.tell() == 0:
            image_file = None
        else:
            image_file.seek(0)  # To beginning of file

    # TODO: image too large?

    generate_output(email, password, image_file)


def generate_output(email, password, image_file):
    if not email or not password:
        print("Location: signin.py")
        print()
        return

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
    if image_file:
        db_cursor.execute("""UPDATE users
                             SET image = %s
                             WHERE email = %s""", (image_file.read(), email))
        db_connection.commit()

    print("Location: home.py")
    print()


try:
    process_input()
except:
    cgi.print_exception()
