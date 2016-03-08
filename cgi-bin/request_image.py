#!/usr/bin/env python

from __future__ import print_function
from collections import namedtuple

from common import config
from common.response import text_response, populate_html, redirect, not_found

import os
import sys
import string
import imghdr
import hashlib
import urlparse
import urllib
import cgi
import MySQLdb


def process_input():
    url_parse_result = urlparse.urlparse(os.environ.get("REQUEST_URI"))

    request_path = url_parse_result.path

    query_parse_result = urlparse.parse_qs(os.environ.get("QUERY_STRING"))

    default = ""
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
        rating = query_parse_result["rating"][0]
    elif "r" in query_parse_result:
        rating = query_parse_result["r"][0]
    if rating not in ratings:
        rating = "g"

    email_hash = os.path.basename(request_path)

    generate_output(email_hash, default, force_default, rating)


def generate_output(email_hash, default, force_default, rating):
    # Hexadecimal MD5 hash value should be 32 bytes
    invalid_hash = (len(email_hash) != hashlib.md5().digest_size * 2 or
                    any(c not in string.hexdigits for c in email_hash))

    # Load image from db
    image = None
    if not invalid_hash and not force_default:
        db_connection = MySQLdb.connect(
            host=config.mysql_host, user=config.mysql_user,
            passwd=config.mysql_password, db=config.mysql_db)
        db_cursor = db_connection.cursor()

        ImageInformation = namedtuple("ImageInformation", "image, rating")

        db_cursor.execute("""SELECT image, rating
                             FROM users
                             WHERE email_hash = %s""",
                          (email_hash.decode("hex"), ))
        record = db_cursor.fetchone()

        if record:
            # Image found and the rating meeting requested rating level
            image_info = ImageInformation._make(record)
            image = image_info.image if image_info.rating <= rating else None
        else:
            image = None

    # Invalid hash or account not found or force to load default image
    # Return default
    if not image:
        # Default not provided, use default image
        if not default:
            image = open(config.default_image, "rb").read()
        # Default is 404
        elif default == "404":
            print(not_found())
            return
        # Default is blank
        elif default == "blank":
            image = open(config.blank_image, "rb").read()
        # Else treat it as a URL
        else:
            print(redirect(urllib.unquote(default)))
            return

    # Make HTTP response
    image_subtype = imghdr.what("", h=image)
    http_response = text_response("image/{}".format(image_subtype), image)
    sys.stdout.write(http_response)


try:
    process_input()
except:
    cgi.print_exception()
