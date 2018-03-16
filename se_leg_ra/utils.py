# -*- coding: utf-8 -*-

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
    if not credibility_data.get('ocular_validation', False):
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
    if current_app.proofing_log.save(proofing_element):
        current_app.logger.info('Saved proofing element.')
        current_app.logger.debug('{}'.format(proofing_element))
        # TODO: Post data to op
        return True
    return False
