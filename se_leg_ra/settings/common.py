# -*- coding: utf-8 -*-

from __future__ import absolute_import


__author__ = 'lundberg'

"""
For more built in configuration options see,
http://flask.pocoo.org/docs/0.10/config/#builtin-configuration-values
"""

DEBUG = False

# Database URIs
DB_URI = ''
REDIS_HOST = ''
REDIS_PORT = 6379
REDIS_DB = 0

# Secret key
SECRET_KEY = None

# Logging
LOG_LEVEL = 'INFO'

# App settings
LOGIN_URL = '/login/'
LOGIN_ALTERNATIVES = [
    {'name': 'a_name', 'url': 'an_url'}
]
LOGOUT_URL = ''

AL2_ASSURANCES = []
AL2_IDP_EXCEPTIONS = []

MFA_AUTHN_CONTEXT_CLASSES = []
MFA_IDP_EXCEPTIONS = []

# Authentication info for OP
RA_APP_ID = ''
RA_APP_SECRET = ''
