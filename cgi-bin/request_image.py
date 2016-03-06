#!/usr/bin/env python

from __future__ import print_function

from common import config
from common.response import text_response, populate_html, redirect, not_found

import os
import sys
import string
import imghdr
import hashlib
import base64
import cgi
import MySQLdb


def process_input():
    request_uri = os.environ.get("REQUEST_URI")

    email_hash = os.path.basename(request_uri)

    generate_output(email_hash)


def generate_output(email_hash):
    # Invalid hash, hexadecimal MD5 hash value should be 32 bytes
    if (len(email_hash) != hashlib.md5().digest_size * 2 or
            any(c not in string.hexdigits for c in email_hash)):
        print(not_found())
        return

    db_connection = MySQLdb.connect(
        host=config.mysql_host, user=config.mysql_user,
        passwd=config.mysql_password, db=config.mysql_db)
    db_cursor = db_connection.cursor()

    db_cursor.execute("""SELECT image
                         FROM users
                         WHERE email_hash = %s""",
                      (base64.b16decode(email_hash.upper()),))
    record = db_cursor.fetchone()

    # Could not find this user
    if not record:
        print(not_found())
        return

    image = record[0]

    # User found
    image_subtype = imghdr.what("", h=image)
    http_response = text_response("image/{}".format(image_subtype), image)
    sys.stdout.write(http_response)


try:
    process_input()
except:
    cgi.print_exception()
