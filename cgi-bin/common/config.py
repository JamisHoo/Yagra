#!/usr/bin/env python

from urlparse import urlunparse


# MySQL server configuration
mysql_host = "localhost"
mysql_user = "root"
mysql_password = "1234"
mysql_db = "yagra"


# Length in bytes of the password for cookie
random_password_length = 32
# The time in seconds password cookies expire
random_password_expires = 60
# Length in bytes of salt
salt_length = 32
# Length in bytes of activation token
activation_token_length = 32
# Length in bytes of password reset token
password_reset_token_length = 32
# The time in seconds password reset tokens expire
password_reset_token_expires = 900


# Server address
my_scheme = "http"
my_domain = "test.jamis.xyz"
my_path = "cgi-bin/"
my_entire_url = urlunparse((my_scheme, my_domain, my_path, None, None, None))
# Sender of activation emails and password reset emails
email_from = "yagra_service@%s" % my_domain
# SMTP server
smtp_host = "localhost"


# Max size in bytes of uploaded image
image_max_size = 3 * 1024 * 1024


# html templates direcoty
html_templates_dir = "html_templates/"
