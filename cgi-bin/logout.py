#!/usr/bin/env python

from __future__ import print_function

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

    print("Location: signin.py")
    print(cookie)
    print()


try:
    process_input()
except:
    cgi.print_exception()
