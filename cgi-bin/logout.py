#!/usr/bin/env python

from __future__ import print_function

from common.response import text_response, populate_html, redirect

import cgi
import Cookie


def process_input():
    # No input needs processing

    generate_output()


def generate_output():
    # Invalidate password cookie
    cookie = Cookie.SimpleCookie()
    cookie["password"] = ""
    cookie["password"]["expires"] = 0

    print(redirect("signin.py", cookie))


try:
    process_input()
except:
    cgi.print_exception()
