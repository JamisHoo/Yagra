#!/usr/bin/env python

import os
from collections import defaultdict

# TODO: move to config file
html_templates_dir = "html_templates"


def populate_html(template_file, variables):
    """ Return a string containing the contents of the named file and replace
    variables in the file.
    """
    variables_dict = defaultdict(str, variables)

    with open(os.path.join(html_templates_dir, template_file)) as file_handler:
        return file_handler.read().format(variables_dict)
