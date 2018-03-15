# -*- coding: utf-8 -*-

from __future__ import absolute_import

from flask import Blueprint, current_app, render_template, url_for, request, redirect
from se_leg_ra.forms import BaseForm, PassportForm
from se_leg_ra.decorators import require_eppn

__author__ = 'lundberg'

se_leg_ra_views = Blueprint('se_leg_ra', __name__, url_prefix='', template_folder='templates')


def get_view_context(form, user):
    view_context = {
        'form': form,
        'action_url': request.path,
        'user': user,
        'success_message': None,
        'error_message': None
    }
    return view_context


@se_leg_ra_views.route('/', methods=['GET'])
@require_eppn
def index(user):
    current_app.logger.debug('GET index')
    # Set up the default form
    view_context = get_view_context(BaseForm(), user)
    view_context['action_url'] = url_for('se_leg_ra.id_card')
    return render_template('id_card.jinja2', view_context=view_context)


@se_leg_ra_views.route('/id-card', methods=['GET', 'POST'])
@require_eppn
def id_card(user):
    form = BaseForm()
    view_context = get_view_context(form, user)

    if form.validate_on_submit():
        current_app.logger.debug('id_card form validated')
        view_context['success_message'] = 'Verifiering mha. id-kort har skickats.'

    return render_template('id_card.jinja2', view_context=view_context)


@se_leg_ra_views.route('/driverce-license', methods=['GET', 'POST'])
@require_eppn
def drivers_license(user):
    form = BaseForm()
    view_context = get_view_context(form, user)

    if form.validate_on_submit():
        view_context['success_message'] = 'Verifiering mha. körkort har skickats.'

    return render_template('drivers_license.jinja2', view_context=view_context)


@se_leg_ra_views.route('/passport', methods=['GET', 'POST'])
@require_eppn
def passport(user):
    form = PassportForm()
    view_context = get_view_context(form, user)

    if form.validate_on_submit():
        view_context['success_message'] = 'Verifiering mha. pass har skickats.'

    return render_template('passport.jinja2', view_context=view_context)


@se_leg_ra_views.route('/logout', methods=['GET'])
@require_eppn
def logout(user):
    current_app.logger.info('User {} logged out'.format(user['eppn']))
    return redirect(current_app.config['LOGOUT_URL'])
