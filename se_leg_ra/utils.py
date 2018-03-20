# -*- coding: utf-8 -*-

import datetime
import requests
from requests.auth import HTTPBasicAuth
from flask import current_app

__author__ = 'lundberg'


def urlappend(base, path):
    """
    :param base: Base url
    :type base: str
    :param path: Path to join to base
    :type path: str
    :return: Joined url
    :rtype: str

    Used instead of urlparse.urljoin to append path to base in an obvious way.

    >>> urlappend('https://test.com/base-path', 'my-path')
    'https://test.com/base-path/my-path'
    >>> urlappend('https://test.com/base-path/', 'my-path')
    'https://test.com/base-path/my-path'
    >>> urlappend('https://test.com/base-path/', '/my-path')
    'https://test.com/base-path/my-path'
    >>> urlappend('https://test.com/base-path', '/my-path')
    'https://test.com/base-path/my-path'
    >>> urlappend('https://test.com/base-path', '/my-path/')
    'https://test.com/base-path/my-path/'
    """
    path = path.lstrip('/')
    if not base.endswith('/'):
        base = '{!s}/'.format(base)
    return '{!s}{!s}'.format(base, path)


def compute_credibility_score(credibility_data):
    """
    :param credibility_data: Collection of credibility data
    :type credibility_data: dict

    :return: credibility score
    :rtype: int
    """
    # Ocular validation
    if not credibility_data.get('ocular_validation', False):
        return 0
    # Expiry date
    expiry_date = credibility_data.get('expiry_date')
    if expiry_date.date() < datetime.date.today():
        return 0
    return 100


def log_and_send_proofing(proofing_element, identity):
    """

    :param proofing_element: Proofing data that should be logged
    :param identity: Proofed identity

    :type: ProofingLogElement
    :type identity: six.string_types

    :return: True/False
    :rtype: bool
    """
    vetting_endpoint = current_app.config['VETTING_ENDPOINT']
    ra_app_secret = current_app.config['RA_APP_SECRET']
    if current_app.proofing_log.save(proofing_element):
        current_app.logger.info('Saved proofing element.')
        current_app.logger.debug('{}'.format(proofing_element))
        try:
            data = {
                'identity': proofing_element.identity,
                'qrcode': proofing_element.opaque,
                'meta': {
                    'score': proofing_element.credibility_score,
                    'proofing_method': proofing_element.proofing_method,
                    'proofing_version': proofing_element.proofing_version
                }
            }
            r = requests.post(vetting_endpoint, json=data,
                              auth=HTTPBasicAuth(proofing_element.created_by, ra_app_secret))
            if r.status_code != 200:
                current_app.logger.error('Bad request to vetting endpoint: {}'.format(r.content))
                return False
        except requests.RequestException as e:
            current_app.logger.error('Could not reach the vetting endpoint: {}'.format(e))
            return False
        return True
    return False
