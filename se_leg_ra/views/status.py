# -*- coding: utf-8 -*-

from flask import Blueprint, current_app, jsonify

__author__ = 'lundberg'


status_views = Blueprint('status', __name__, url_prefix='/status')


def _check_mongo():
    db = current_app.user_db
    try:
        return db.is_healthy()
    except Exception as exc:
        current_app.logger.warning('Mongodb health check failed: {}'.format(exc))
        return False


@status_views.route('/healthy', methods=['GET'])
def health_check():
    res = {'status': 'STATUS_FAIL'}
    if not _check_mongo():
        res['reason'] = 'mongodb check failed'
        current_app.logger.warning('mongodb check failed')
    else:
        res['status'] = 'STATUS_OK'
        res['reason'] = 'Databases tested OK'
    return jsonify(res)
