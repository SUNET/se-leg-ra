# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField
from wtforms.validators import InputRequired

__author__ = 'lundberg'


class BaseForm(FlaskForm):
    qr_code = TextAreaField('QR-kod', description='Klicka här och läs in QR-koden', validators=[InputRequired()])
    identity = StringField('Personnummer', description='ÅÅÅÅMMDDNNNN', validators=[InputRequired()])
    ocular_validation = BooleanField('Ok', description='Ovanstående uppgifter är rätta och riktiga')


class PassportForm(BaseForm):
    passport_number = StringField('Passnummer', description='NNNNNNNN', validators=[InputRequired()])
