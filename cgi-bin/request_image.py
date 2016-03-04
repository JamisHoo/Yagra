#!/usr/bin/env python

from __future__ import print_function

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
    # TODO: think about leading zero in email hash
    email_hash = os.path.basename(request_uri)

    generate_output(email_hash)


def generate_output(email_hash):
    # Invalid hash, hexadecimal MD5 hash value should be 32 bytes
    if (len(email_hash) != hashlib.md5().digest_size * 2 or
            any(c not in string.hexdigits for c in email_hash)):
        print("Status: 404 Not Found")
        print("Content-type: text/html")
        print()
        return

    db_connection = MySQLdb.connect(host="localhost", user="root",
                                    passwd="1234", db="yagra")
    db_cursor = db_connection.cursor()

    db_cursor.execute("""SELECT image
                         FROM users
                         WHERE email_hash = %s""",
                      (base64.b16decode(email_hash.upper()),))
    record = db_cursor.fetchone()

    # Could not find this user
    if not record:
        print("Status: 404 Not Found")
        print("Content-type: text/html")
        print()
        return

    image = record[0]

    # User found
    image_subtype = imghdr.what("", h=image)
    print("Content-type: image/{subtype}".format(subtype=image_subtype))
    print()
    sys.stdout.write(image)


try:
    process_input()
except:
    cgi.print_exception()
