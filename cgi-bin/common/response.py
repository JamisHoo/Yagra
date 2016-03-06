#!/usr/bin/env python

import os
import config

from collections import defaultdict


def text_response(content_type, message_body, cookie=None):
    response = ""
    response += "Content-type: {}".format(content_type) + "\n"
    if cookie:
        response += str(cookie) + "\n"
    response += "\n"
    response += message_body

    return response


def redirect(location, cookie=None):
    response = ""
    response += "Location: {}".format(location) + "\n"
    if cookie:
        response += str(cookie) + "\n"
    response += "\n"

    return response


def not_found():
    response = "Status: 404 Not Found"
    return response


def populate_html(template_file, variables={}):
    """ Return a string containing the contents of the named file and replace
    variables in the file.
    """
    variables_dict = defaultdict(str, variables)

    file_path = os.path.join(config.html_templates_dir, template_file)

    with open(file_path) as file_handler:
        return file_handler.read().format(variables_dict)
