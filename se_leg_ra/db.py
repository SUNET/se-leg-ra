# -*- coding: utf-8 -*-

from eduid_userdb.db import BaseDB
from eduid_userdb.logs.element import LogElement

__author__ = 'lundberg'


class BaseSeLegDB(BaseDB):

    def __repr__(self):
        return '<se-leg {!s}: {!s} {!r}>'.format(self.__class__.__name__,
                                                 self._db.sanitized_uri,
                                                 self._coll_name)


class UserDB(BaseSeLegDB):

    def __init__(self, db_uri, db_name='se_leg_ra', collection='users'):
        super(UserDB, self).__init__(db_uri, db_name, collection=collection)

    def is_whitelisted(self, eppn):
        """
        :param eppn: User eppn
        :type eppn: six.string_type
        :return: True or False
        :rtype: bool
        """
        if self._get_documents_by_attr('eppn', eppn, raise_on_missing=False):
            return True
        return False

    def update_user(self, user):
        """
        :param user: user data
        :type user: dict
        :return: None
        :rtype: None
        """
        eppn = user.get('eppn')
        if eppn:
            result = self._coll.replace_one({'eppn': eppn}, user, upsert=False)


class ProofingLog(BaseSeLegDB):

    def __init__(self, db_uri, db_name='se_leg_ra', collection='proofing_log'):
        # Make sure writes reach a majority of replicas
        super(ProofingLog, self).__init__(db_uri, db_name, collection, safe_writes=True)

    def _insert(self, doc):
        self._coll.insert_one(doc)

    def save(self, log_element):
        """
        @param log_element:
        @type log_element: eduid_userdb.logs.element.LogElement
        @return: Boolean
        @rtype: bool
        """
        if log_element.validate():
            self._insert(log_element.to_dict())
            return True
        return False


class ProofingLogElement(LogElement):

    def __init__(self, created_by, verified_by, opaque, ocular_validation, expiry_date, credibility_score,
                 proofing_method, proofing_version):
        """
        :param created_by: Application creating the log element
        :param verified_by: RA users eppn
        :param opaque: The json blob in string format the QR code contains
        :param ocular_validation: Did everything look ok to the RA user
        :param expiry_date: Identity document expiry date
        :param credibility_score: Overall score of the proofing
        :param proofing_method: Proofing method name
        :param proofing_version: Proofing method version number

        :type created_by: six.string_types
        :type verified_by: six.string_types
        :type opaque: six.string_types
        :type ocular_validation: bool
        :type expiry_date: datetime.datetime.date
        :type credibility_score: int
        :type proofing_method: six.string_types
        :type proofing_version: six.string_types

        :return: ProofingLogElement object
        :rtype: ProofingLogElement
        """
        super(ProofingLogElement, self).__init__(created_by)
        self._required_keys.extend(['verified_by', 'opaque', 'ocular_validation', 'expiry_date', 'credibility_score',
                                    'proofing_method', 'proofing_version'])
        self._data['verified_by'] = verified_by
        self._data['opaque'] = opaque
        self._data['ocular_validation'] = ocular_validation
        self._data['expiry_date'] = expiry_date
        self._data['credibility_score'] = credibility_score
        self._data['proofing_method'] = proofing_method
        self._data['proofing_version'] = proofing_version

    def __repr__(self):
        return '<se-leg {!s}: {!r}>'.format(self.__class__.__name__, self._data)

    @property
    def opaque(self):
        return self._data['opaque']

    @property
    def credibility_score(self):
        return self._data['credibility_score']

    @property
    def proofing_method(self):
        return self._data['proofing_method']

    @property
    def proofing_version(self):
        return self._data['proofing_version']


class NinIdentityProofingElement(ProofingLogElement):

    @property
    def identity(self):
        return self._data['nin']


class DriversLicenseProofing(NinIdentityProofingElement):
    """
    {
        'created_ts': datetime.utcnow()
        'created_by': 'RA app id',
        'verified_by': 'RA eppn',
        'nin': national_identity_number,
        'reference_number': 'drivers license reference number',
        'opaque': nonce_and_token_from_qr_code,
        'ocular_validation': True/False,
        'expiry_date': datetime.datetime(),
        'credibility_score': 0-100,
        'proofing_method': 'drivers_license',
        'proofing_version': '2018v1',
    }
    """

    def __init__(self, created_by, verified_by, nin, reference_number, opaque, ocular_validation, expiry_date,
                 credibility_score, proofing_version):
        """
        :param created_by: Application creating the log element
        :param verified_by: RA users eppn
        :param nin: National identity number
        :param reference_number: Drivers license reference number
        :param opaque: The json blob in string format the QR code contains
        :param ocular_validation: Did everything look ok to the RA user
        :param expiry_date: Identity document expiry date
        :param credibility_score: Overall score of the proofing
        :param proofing_version: Proofing method version number

        :type created_by: six.string_types
        :type verified_by: six.string_types
        :type nin: six.string_types
        :type reference_number: six.string_types
        :type opaque: six.string_types
        :type ocular_validation: bool
        :type expiry_date: datetime.datetime.date
        :type credibility_score: int
        :type proofing_version: six.string_types

        :return: DriversLicenseProofing object
        :rtype: DriversLicenseProofing
        """
        super(DriversLicenseProofing, self).__init__(created_by, verified_by=verified_by, opaque=opaque,
                                                     ocular_validation=ocular_validation, expiry_date=expiry_date,
                                                     credibility_score=credibility_score,
                                                     proofing_method='drivers_license',
                                                     proofing_version=proofing_version)
        self._required_keys.extend(['nin', 'reference_number'])
        self._data['nin'] = nin
        self._data['reference_number'] = reference_number


class PassportProofing(NinIdentityProofingElement):
    """
    {
        'created_ts': datetime.utcnow()
        'created_by': 'RA app id',
        'verified_by': 'RA eppn',
        'nin': national_identity_number,
        'opaque': nonce_and_token_from_qr_code,
        'ocular_validation': True/False,
        'expiry_date': datetime.datetime(),
        'credibility_score': 0-100,
        'passport_number': passport_number,
        'proofing_method': 'passport',
        'proofing_version': '2018v1',
    }
    """

    def __init__(self, created_by, verified_by, nin, passport_number, opaque, ocular_validation, expiry_date,
                 credibility_score, proofing_version):
        """
        :param created_by: Application creating the log element
        :param verified_by: RA users eppn
        :param nin: National identity number
        :param passport_number: Passport number
        :param opaque: The json blob in string format the QR code contains
        :param ocular_validation: Did everything look ok to the RA user
        :param expiry_date: Identity document expiry date
        :param credibility_score: Overall score of the proofing
        :param proofing_version: Proofing method version number

        :type created_by: six.string_types
        :type verified_by: six.string_types
        :type nin: six.string_types
        :type passport_number: six.string_types
        :type opaque: six.string_types
        :type ocular_validation: bool
        :type expiry_date: datetime.datetime.date
        :type credibility_score: int
        :type proofing_version: six.string_types

        :return: PassportProofing object
        :rtype: PassportProofing
        """
        super(PassportProofing, self).__init__(created_by, verified_by=verified_by, opaque=opaque,
                                               ocular_validation=ocular_validation, expiry_date=expiry_date,
                                               credibility_score=credibility_score, proofing_method='passport',
                                               proofing_version=proofing_version)
        self._required_keys.extend(['nin', 'passport_number'])
        self._data['nin'] = nin
        self._data['passport_number'] = passport_number


class IdCardProofing(NinIdentityProofingElement):
    """
    {
        'created_ts': datetime.utcnow()
        'created_by': 'RA app id',
        'verified_by': 'RA eppn',
        'nin': national_identity_number,
        'opaque': nonce_and_token_from_qr_code,
        'ocular_validation': True/False,
        'expiry_date': datetime.datetime(),
        'credibility_score': 0-100,
        'card_number': card_number,
        'proofing_method': 'id_card',
        'proofing_version': '2018v1',
    }
    """

    def __init__(self, created_by, verified_by, nin, card_number, opaque, ocular_validation, expiry_date,
                 credibility_score, proofing_version):
        """
        :param created_by: Application creating the log element
        :param verified_by: RA users eppn
        :param nin: National identity number
        :param card_number: Id card number
        :param opaque: The json blob in string format the QR code contains
        :param ocular_validation: Did everything look ok to the RA user
        :param expiry_date: Identity document expiry date
        :param credibility_score: Overall score of the proofing
        :param proofing_version: Proofing method version number

        :type created_by: six.string_types
        :type verified_by: six.string_types
        :type nin: six.string_types
        :type card_number: six.string_types
        :type opaque: six.string_types
        :type ocular_validation: bool
        :type expiry_date: datetime.datetime.date
        :type credibility_score: int
        :type proofing_version: six.string_types

        :return: PassportProofing object
        :rtype: PassportProofing
        """
        super(IdCardProofing, self).__init__(created_by, verified_by=verified_by, opaque=opaque,
                                             ocular_validation=ocular_validation, expiry_date=expiry_date,
                                             credibility_score=credibility_score, proofing_method='id_card',
                                             proofing_version=proofing_version)
        self._required_keys.extend(['nin', 'card_number'])
        self._data['nin'] = nin
        self._data['card_number'] = card_number


class NationalIdCardProofing(IdCardProofing):
    """
    {
        'created_ts': datetime.utcnow()
        'created_by': 'RA app id',
        'verified_by': 'RA eppn',
        'nin': national_identity_number,
        'opaque': nonce_and_token_from_qr_code,
        'ocular_validation': True/False,
        'expiry_date': datetime.datetime(),
        'credibility_score': 0-100,
        'card_number': card_number,
        'proofing_method': 'passport',
        'proofing_version': '2018v1',
    }
    """

    def __init__(self, created_by, verified_by, nin, card_number, opaque, ocular_validation, expiry_date,
                 credibility_score, proofing_version):
        """
        :param created_by: Application creating the log element
        :param verified_by: RA users eppn
        :param nin: National identity number
        :param card_number: Id card number
        :param opaque: The json blob in string format the QR code contains
        :param ocular_validation: Did everything look ok to the RA user
        :param expiry_date: Identity document expiry date
        :param credibility_score: Overall score of the proofing
        :param proofing_version: Proofing method version number

        :type created_by: six.string_types
        :type verified_by: six.string_types
        :type nin: six.string_types
        :type card_number: six.string_types
        :type opaque: six.string_types
        :type ocular_validation: bool
        :type expiry_date: datetime.datetime.date
        :type credibility_score: int
        :type proofing_version: six.string_types

        :return: NationalIdCardProofing object
        :rtype: NationalIdCardProofing
        """
        super(NationalIdCardProofing, self).__init__(created_by, verified_by, nin, card_number, opaque,
                                                     ocular_validation, expiry_date, credibility_score,
                                                     proofing_version)
        self._data['proofing_method'] = 'national_id_card'
