# -*- coding: utf-8 -*-

from functools import wraps
from flask import request, current_app, abort

__author__ = 'lundberg'


def require_eppn(f):
    @wraps(f)
    def require_eppn_decorator(*args, **kwargs):
        eppn = request.environ.pop('HTTP_EPPN', None)
        # If the logged in user is whitelisted then we
        # pass on the request to the decorated view
        # together with a dict of user attributes.
        if eppn and current_app.user_db.is_whitelisted(eppn) and is_al2():
            user = {
                'eppn': eppn,
                'given_name': request.environ.pop('HTTP_GIVENNAME', None),
                'surname': request.environ.pop('HTTP_SN', None),
                'display_name': request.environ.pop('HTTP_DISPLAYNAME', None),
            }
            kwargs['user'] = user
            current_app.user_db.update_user(user)
            return f(*args, **kwargs)
        # Anything else is considered as an unauthorized request
        current_app.logger.warning('{} not in whitelist'.format(eppn))
        abort(403)
    return require_eppn_decorator


def is_al2():
    """
    Require AL2 assurance by default but with a list of exceptions.

    :return: True/False
    :rtype: Boolean
    """
    entity_id = request.environ.pop('HTTP_SHIB_IDENTITY_PROVIDER', None)
    if entity_id in current_app.config['AL2_IDP_EXCEPTIONS']:
        return True
    assurance = request.environ.pop('HTTP_ASSURANCE', None)
    if assurance == 'http://www.swamid.se/policy/assurance/al2':
        return True
    return False
