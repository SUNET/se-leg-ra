# -*- coding: utf-8 -*-

import re
import json
from flask import current_app
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, DateTimeField
from wtforms.validators import InputRequired, Regexp, ValidationError

__author__ = 'lundberg'


class OpaqueDataField(TextAreaField):
    """
    Extension of TextAreaField that removes whitespace from input data.
    """
    def process_formdata(self, valuelist):
        super().process_formdata(valuelist)
        if valuelist:
            self.data = ''.join(valuelist[0].split())


class SEDateTimeField(DateTimeField):
    """
    Extension of DateField to provide error message in swedish.
    """
    def process_formdata(self, valuelist):
        try:
            super().process_formdata(valuelist)
        except ValueError:
            raise ValueError('Ange ett giltigt datum i formatet ÅÅÅÅ-MM-DD')


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

        opaque_data = ''.join(field.raw_data[0].split())
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
nin_validator = Regexp(nin_re, message="Ange ett giltigt personnummer i formatet ÅÅMMDDNNNN")

passport_number_re = re.compile('\d{8}')
passport_number_validator = Regexp(passport_number_re,
                                              message="Ange ett giltigt nummer i formatet NNNNNNNN (åtta siffror)")


class BaseForm(FlaskForm):
    qr_code = OpaqueDataField('QR-kod', description='Klicka här och läs in QR-koden',
                            validators=[input_validator, qr_validator])
    nin = StringField('Personnummer', description='ÅÅÅÅMMDDNNNN', validators=[input_validator, nin_validator])
    expiry_date = SEDateTimeField('Utgångsdatum', description="YYYY-MM-DD", format='%Y-%m-%d',
                                  validators=[input_validator])
    ocular_validation = BooleanField(description='Ovanstående uppgifter är rätta och riktiga')


class PassportForm(BaseForm):
    passport_number = StringField('Passnummer', description='NNNNNNNN',
                                  validators=[passport_number_validator])


class NationalIDCard(BaseForm):
    card_number = StringField('Kortnummer', description='NNNNNNNN', validators=[passport_number_validator])
