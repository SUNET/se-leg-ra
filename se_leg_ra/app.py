# -*- coding: utf-8 -*-

from __future__ import absolute_import

import logging
from flask import Flask, current_app
from werkzeug.contrib.fixers import ProxyFix
from flask_wtf.csrf import CSRFProtect
from se_leg_ra.db import UserDB, ProofingLog
from se_leg_ra.utils import urlappend
from se_leg_ra.middleware import LocalhostMiddleware


__author__ = 'lundberg'


SE_LEG_RA_SETTINGS_ENVVAR = 'SE_LEG_RA_SETTINGS'


def init_logging(app):
    out_handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    out_handler.setFormatter(formatter)
    out_handler.setLevel(logging.DEBUG)
    app.logger.addHandler(out_handler)
    return app


def init_template_functions(app):

    @app.template_global()
    def static_url_for(f):
        static_url = current_app.config.get('STATIC_URL', '/static/')
        return urlappend(static_url, f)

    return app


def init_se_leg_ra_app(name=None, config=None):
    """
    :param name: The name of the instance, it will affect the configuration loaded.
    :param config: any additional configuration settings. Specially useful
                   in test cases

    :type name: str
    :type config: dict

    :return: the flask app
    :rtype: flask.Flask
    """

    name = name or __name__
    app = Flask(name)
    # Load project wide default settings
    app.config.from_object('se_leg_ra.settings.common')
    # Load optional app specific settings
    app.config.from_envvar(SE_LEG_RA_SETTINGS_ENVVAR, silent=True)
    if config:
        # Load optional init time settings
        app.config.update(config)

    # Init logging
    app = init_logging(app)

    # Init other
    app.wsgi_app = ProxyFix(app.wsgi_app)
    app.url_map.strict_slashes = False
    CSRFProtect(app)
    app = init_template_functions(app)
    app.wsgi_app = LocalhostMiddleware(app.wsgi_app, server_name=app.config['SERVER_NAME'])

    # Register views
    from se_leg_ra.views.ra import se_leg_ra_views
    app.register_blueprint(se_leg_ra_views)
    from se_leg_ra.views.status import status_views
    app.register_blueprint(status_views)

    # Init db
    app.user_db = UserDB(db_uri=app.config['DB_URI'])
    app.logger.info('user_db initialized')
    app.user_db.setup_indexes({'index-eppn': {'key': [('eppn', 1)], 'unique': True, 'background': True}, })
    app.logger.info('user_db indexing started')

    app.proofing_log = ProofingLog(db_uri=app.config['DB_URI'])
    app.logger.info('proofing_log initialized')

    app.logger.info('{!s} initialized'.format(name))
    return app
