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


class LuhnValidator(object):
    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):
        if self.message is None:
            message = field.gettext('Could not validate NIN format')
        else:
            message = self.message

        n = int(field.raw_data[0][2:])
        # https://rosettacode.org/wiki/Luhn_test_of_credit_card_numbers#Python
        r = [int(ch) for ch in str(n)][::-1]
        if not (sum(r[0::2]) + sum(sum(divmod(d * 2, 10)) for d in r[1::2])) % 10 == 0:
            raise ValidationError(message)


class NDigitValidator(Regexp):
    """
    Validates that the field contains n number of digits.
    """
    def __init__(self, n_digits, message=None):
        regex = re.compile('\d{%s}' % n_digits)
        super().__init__(regex=regex, message=message)


class NinValidator(Regexp):
    """
    Validates that the field contains a correctly formatted swedish national identity number.
    """
    def __init__(self, message=None):
        regex = re.compile(r'^(18|19|20)\d{2}(0[1-9]|1[0-2])\d{2}\d{4}$')
        super().__init__(regex=regex, message=message)


input_validator = InputRequired(message="Det här fältet är obligatoriskt")
qr_validator = OpaqueDataRequired(message="Inläsning av QR-koden misslyckades")
nin_validator = NinValidator(message="Ange ett giltigt personnummer i formatet ÅÅMMDDNNNN")
luhn_validator = LuhnValidator(message='Personnummret kunde inte valideras. Saknas någon siffra?')
eight_digits_validator = NDigitValidator(8, message="Ange ett giltigt nummer i formatet NNNNNNNN (åtta siffror)")
nine_digits_validator = NDigitValidator(9, message="Ange ett giltigt nummer i formatet NNNNNNNNN (nio siffror)")


class BaseForm(FlaskForm):
    qr_code = OpaqueDataField('QR-kod', description='Klicka här och läs in QR-koden',
                              validators=[input_validator, qr_validator])
    nin = StringField('Personnummer', description='ÅÅÅÅMMDDNNNN', validators=[input_validator, nin_validator])
    expiry_date = SEDateTimeField('Utgångsdatum', description="YYYY-MM-DD", format='%Y-%m-%d',
                                  validators=[input_validator])
    ocular_validation = BooleanField(description='Ovanstående uppgifter är rätta och riktiga', default="checked")


class DriversLicenseForm(BaseForm):
    reference_number = StringField('Referensnummer', description='NNNNNNNNN',
                                   validators=[nine_digits_validator])


class IdCardForm(BaseForm):
    card_number = StringField('Kortnummer', description='Kortnummer',
                              validators=[input_validator])


class PassportForm(BaseForm):
    passport_number = StringField('Passnummer', description='NNNNNNNN',
                                  validators=[eight_digits_validator])


class NationalIDCardForm(BaseForm):
    card_number = StringField('Kortnummer', description='NNNNNNNN',
                              validators=[eight_digits_validator])
