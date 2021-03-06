# -*- coding: utf-8 -*-

from flask import Blueprint, current_app, render_template, url_for, request, redirect
from se_leg_ra.forms import DriversLicenseForm, IdCardForm, PassportForm, NationalIDCardForm
from se_leg_ra.decorators import require_eppn
from se_leg_ra.db import IdCardProofing, DriversLicenseProofing, PassportProofing, NationalIdCardProofing
from se_leg_ra.utils import log_and_send_proofing

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
    view_context = get_view_context(DriversLicenseForm(), user)
    view_context['action_url'] = url_for('se_leg_ra.drivers_license')
    return render_template('drivers_license.jinja2', view_context=view_context)


@se_leg_ra_views.route('/login', methods=['GET'])
def login():
    current_app.logger.debug('GET login')
    login_dict = current_app.config['LOGIN_ALTERNATIVES']
    return render_template('login.jinja2', login_alternatives=login_dict)


@se_leg_ra_views.route('/id-card', methods=['GET', 'POST'])
@require_eppn
def id_card(user):
    form = IdCardForm()
    view_context = get_view_context(form, user)

    if form.validate_on_submit():
        current_app.logger.debug('id_card form validated')
        data = {
            'qr_code': form.qr_code.data,
            'nin': form.nin.data,
            'card_number': form.card_number.data,
            'expiry_date': form.expiry_date.data,
            'ocular_validation': form.ocular_validation.data
        }
        current_app.logger.debug('Form data: {}'.format(data))
        # Log the vetting attempt
        proofing_element = IdCardProofing(current_app.config['RA_APP_ID'], user['eppn'], data['nin'],
                                          data['card_number'], data['qr_code'], data['ocular_validation'],
                                          data['expiry_date'], '2018v1')
        view_context = log_and_send_proofing(proofing_element, identity=data['nin'], view_context=view_context)

    return render_template('id_card.jinja2', view_context=view_context)


@se_leg_ra_views.route('/drivers-license', methods=['GET', 'POST'])
@require_eppn
def drivers_license(user):
    form = DriversLicenseForm()
    view_context = get_view_context(form, user)

    if form.validate_on_submit():
        data = {
            'qr_code': form.qr_code.data,
            'nin': form.nin.data,
            'reference_number': form.reference_number.data,
            'expiry_date': form.expiry_date.data,
            'ocular_validation': form.ocular_validation.data
        }
        current_app.logger.debug('Form data: {}'.format(data))
        # Log the vetting attempt
        proofing_element = DriversLicenseProofing(current_app.config['RA_APP_ID'], user['eppn'], data['nin'],
                                                  data['reference_number'], data['qr_code'], data['ocular_validation'],
                                                  data['expiry_date'], '2018v1')
        view_context = log_and_send_proofing(proofing_element, identity=data['nin'], view_context=view_context)

    return render_template('drivers_license.jinja2', view_context=view_context)


@se_leg_ra_views.route('/passport', methods=['GET', 'POST'])
@require_eppn
def passport(user):
    form = PassportForm()
    view_context = get_view_context(form, user)

    if form.validate_on_submit():
        data = {
            'qr_code': form.qr_code.data,
            'nin': form.nin.data,
            'expiry_date': form.expiry_date.data,
            'passport_number': form.passport_number.data,
            'ocular_validation': form.ocular_validation.data
        }
        current_app.logger.debug('Form data: {}'.format(data))
        # Log the vetting attempt
        proofing_element = PassportProofing(current_app.config['RA_APP_ID'], user['eppn'], data['nin'],
                                            data['passport_number'], data['qr_code'], data['ocular_validation'],
                                            data['expiry_date'], '2018v1')
        view_context = log_and_send_proofing(proofing_element, identity=data['nin'], view_context=view_context)

    return render_template('passport.jinja2', view_context=view_context)


@se_leg_ra_views.route('/national-id-card', methods=['GET', 'POST'])
@require_eppn
def national_id_card(user):
    form = NationalIDCardForm()
    view_context = get_view_context(form, user)

    if form.validate_on_submit():
        data = {
            'qr_code': form.qr_code.data,
            'nin': form.nin.data,
            'expiry_date': form.expiry_date.data,
            'card_number': form.card_number.data,
            'ocular_validation': form.ocular_validation.data
        }
        current_app.logger.debug('Form data: {}'.format(data))
        # Log the vetting attempt
        proofing_element = NationalIdCardProofing(current_app.config['RA_APP_ID'], user['eppn'], data['nin'],
                                                  data['card_number'], data['qr_code'],
                                                  data['ocular_validation'], data['expiry_date'], '2018v1')
        view_context = log_and_send_proofing(proofing_element, identity=data['nin'], view_context=view_context)

    return render_template('national_id_card.jinja2', view_context=view_context)


@se_leg_ra_views.route('/logout', methods=['GET'])
@require_eppn
def logout(user):
    current_app.logger.info('User {} logged out'.format(user['eppn']))
    return redirect(current_app.config['LOGOUT_URL'])
