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
    # Load email and password from cookie
    cookie = Cookie.SimpleCookie(os.environ.get("HTTP_COOKIE"))

    email = cookie["email"].value if "email" in cookie else None
    password = cookie["password"].value if "password" in cookie else None

    # Load image uploaded from form
    form = cgi.FieldStorage()
    image_file = form["userfile"].file if "userfile" in form else None
    rating = form.getfirst("rating")
    if rating not in ["g", "pg", "r", "x"]:
        rating = "g"

    # Check whether is an empty file
    image_file_size = 0
    if image_file:
        image_file.seek(0, 2)  # To end of file
        image_file_size = image_file.tell()
        if image_file_size == 0:
            image_file = None
        else:
            image_file.seek(0)  # To beginning of file

    generate_output(email, password, image_file, image_file_size, rating)


def generate_output(email, password, image_file, image_file_size, rating):
    if not email or not password:
        print(redirect("signin.py"))
        return

    # File too large
    if image_file_size > config.image_max_size:
        message_body = (
            "Image size too large. "
            "Maximum allowed size is {} bytes. ".format(config.image_max_size))
        print(text_response("text/plain", message_body))
        return

    db_connection = MySQLdb.connect(
        host=config.mysql_host, user=config.mysql_user,
        passwd=config.mysql_password, db=config.mysql_db)
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
        print(redirect("signin.py"))
        return

    user_info = UserInformation._make(record)

    input_password_hash = hashlib.sha256(user_info.salt + password).digest()

    # Wrong password
    if (input_password_hash != user_info.password_hash and
            input_password_hash != user_info.random_password_hash):
        print(redirect("signin.py"))
        return

    # Valid email and password
    if image_file:
        db_cursor.execute("""UPDATE users
                             SET image = %s, rating = %s
                             WHERE email = %s""",
                          (image_file.read(), rating, email))
        db_connection.commit()

    print(redirect("home.py"))


try:
    process_input()
except:
    cgi.print_exception()
