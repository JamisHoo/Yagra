#!/usr/bin/env python

from common import config
from common.response import text_response, populate_html


def generate_output():
    message_body = populate_html("api.html",
                                 dict(my_entire_url=config.my_entire_url))
    print(text_response("text/html", message_body))
    return

generate_output()
