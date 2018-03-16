# -*- coding: utf-8 -*-

import re
import json
from flask import current_app
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField
from wtforms.validators import InputRequired, Regexp, ValidationError, Length

__author__ = 'lundberg'


class OpaqueDataRequired(object):
    """
    Validates that the scanned QR code resulted in readable data.
    """
    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):
        if self.message is None:
            message = field.gettext('Could not validate QR data format')
        else:
            message = self.message

        opaque_data = field.raw_data[0]
        opaque_data_version = opaque_data[0]
        if opaque_data_version != '1':
            current_app.logger.info('Invalid opaque data version')
            field.errors[:] = []
            raise ValidationError(message)

        try:
            opaque_data_deserialized = json.loads(opaque_data[1:])
        except ValueError as e:
            current_app.logger.info('Invalid formatted opaque data: {}'.format(e))
            field.errors[:] = []
            raise ValidationError(message)

        if not all(key in opaque_data_deserialized for key in ('nonce', 'token')):
            current_app.logger.info('Invalid opaque data: nonce or token is missing')
            field.errors[:] = []
            raise ValidationError(message)


input_validator = InputRequired(message="Det här fältet är obligatoriskt")

qr_validator = OpaqueDataRequired(message="Inläsning av QR-koden misslyckades")

nin_re = re.compile(r'^(18|19|20)\d{2}(0[1-9]|1[0-2])\d{2}\d{4}$')
nin_validator = Regexp(nin_re, message="Ange ett giltigt personnummer i formatet YYMMDDNNNN")

passport_number_re = re.compile('\d{8}')
passport_number_validator = Regexp(passport_number_re, message="Ange ett giltigt passnummer i formatet NNNNNNNN")

class BaseForm(FlaskForm):
    qr_code = TextAreaField('QR-kod', description='Klicka här och läs in QR-koden',
                            validators=[input_validator, qr_validator])
    nin = StringField('Personnummer', description='ÅÅÅÅMMDDNNNN', validators=[input_validator, nin_validator])
    ocular_validation = BooleanField(description='Ovanstående uppgifter är rätta och riktiga')


class PassportForm(BaseForm):
    passport_number = StringField('Passnummer', description='NNNNNNNN', validators=[passport_number_validator])
