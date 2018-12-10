# -*- coding: utf-8 -*-

from functools import wraps
from six import string_types
from flask import request, current_app, abort, redirect
__author__ = 'lundberg'


def require_eppn(f):
    @wraps(f)
    def require_eppn_decorator(*args, **kwargs):
        eppn = request.environ.pop('HTTP_EPPN', None)
        if not eppn:
            # Redirect user to login page
            current_app.logger.info('No eppn found, redirecting to log in page')
            return redirect(current_app.config['LOGIN_URL'])

        # Check if the assertion contains an AL2 assurance or if it
        # is coming from an IdP that is in the exceptions list
        if not is_al2():
            current_app.logger.warning('{} not AL2'.format(eppn))
            abort(403)

        # If the logged in user is whitelisted then we
        # pass on the request to the decorated view
        # together with a dict of user attributes.
        if eppn and current_app.user_db.is_whitelisted(eppn):
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
    entity_id = request.environ.get('HTTP_SHIB_IDENTITY_PROVIDER', None)
    if entity_id in current_app.config['AL2_IDP_EXCEPTIONS']:
        current_app.logger.warning('Not checking assurance from {}.'.format(entity_id))
        return True
    assurance = request.environ.pop('HTTP_ASSURANCE', None)
    if assurance:
        # Allow for both a single string and a list of assurances
        if isinstance(assurance, string_types):
            assurance = [assurance]
        # Check allowed assurances against supplied ones
        for item in current_app.config['AL2_ASSURANCES']:
            if item in assurance:
                current_app.logger.info('Assertion from {} asserted {} assurance'.format(entity_id, assurance))
                return True
    current_app.logger.warning('Not accepted assurance ({}) from {}'.format(assurance, entity_id))
    return False


def is_mfa():
    """
    Require MFA by default but with a list of exceptions.

    :return: True/False
    :rtype: Boolean
    """
    entity_id = request.environ.get('HTTP_SHIB_IDENTITY_PROVIDER', None)
    if entity_id in current_app.config['MFA_IDP_EXCEPTIONS']:
        current_app.logger.info('Not checking authn context class from {}'.format(entity_id))
        return True
    authn_context_class = request.environ.pop('HTTP_SHIB_AUTHNCONTEXT_CLASS', None)
    if authn_context_class in current_app.config['MFA_AUTHN_CONTEXT_CLASSES']:
        current_app.logger.info('Assertion from {} asserted {} authn context class'.format(entity_id,
                                                                                           authn_context_class))
        return True
    current_app.logger.warning('Not accepted authn context class ({}) from {}'.format(authn_context_class, entity_id))
    return False
