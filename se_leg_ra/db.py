# -*- coding: utf-8 -*-

from eduid_userdb.db import BaseDB

__author__ = 'lundberg'


class UserDB(BaseDB):

    def __init__(self, db_uri, db_name='se_leg_ra', collection='users'):
        super(UserDB, self).__init__(db_uri, db_name, collection=collection)

    def __repr__(self):
        return '<se-leg {!s}: {!s} {!r}>'.format(self.__class__.__name__,
                                                self._db.sanitized_uri,
                                                self._coll_name)

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
            result = self._coll.update({'eppn': eppn}, user, upsert=False)
