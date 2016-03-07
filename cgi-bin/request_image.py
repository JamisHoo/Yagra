#!/usr/bin/env python

from __future__ import print_function

from common import config
from common.response import text_response, populate_html, redirect, not_found

import os
import sys
import string
import imghdr
import hashlib
import urlparse
import cgi
import MySQLdb


def process_input():
    url_parse_result = urlparse.urlparse(os.environ.get("REQUEST_URI"))

    request_path = url_parse_result.path

    query_parse_result = urlparse.parse_qs(os.environ.get("QUERY_STRING"))

    default = config.default_image
    if "default" in query_parse_result:
        default = query_parse_result["default"][0]
    elif "d" in query_parse_result:
        default = query_parse_result["d"][0]

    force_default = False
    force_default = force_default or "force_default" in query_parse_result
    force_default = force_default or "f" in query_parse_result

    rating = "g"
    ratings = ["g", "pg", "r", "x"]
    if "rating" in query_parse_result:
        rating = query_parse_reuslt["rating"][0]
    elif "r" in query_parse_result:
        rating = query_parse_result["r"][0]
    if rating not in ratings:
        rating = "g"

    email_hash = os.path.basename(request_path)

    generate_output(email_hash, default, force_default, rating)


def generate_output(email_hash, default, force_default, rating):
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
                      (email_hash.decode("hex"), ))
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
