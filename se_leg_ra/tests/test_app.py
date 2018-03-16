# -*- coding: utf-8 -*-

from __future__ import absolute_import

from unittest import TestCase
from flask import request
from eduid_userdb.testing import MongoTemporaryInstance
from se_leg_ra.app import init_se_leg_ra_app
from se_leg_ra.forms import input_validator, qr_validator, nin_validator, passport_number_validator

__author__ = 'lundberg'


class SeLegRATests(TestCase):
    """Base TestCase for those tests that need a full environment setup"""

    @classmethod
    def setUpClass(cls):
        super(SeLegRATests, cls).setUpClass()
        cls.mongo_instance = MongoTemporaryInstance()

    def setUp(self):
        config = {
            'SERVER_NAME': 'localhost',
            'SECRET_KEY': 'testing',
            'TESTING': True,
            'MONGO_URI': self.mongo_instance.get_uri(),
            'RA_APP_ID': 'test_ra_app',
            'WTF_CSRF_ENABLED': False
        }

        self.test_user_eppn = 'test-user@localhost'

        self.app = init_se_leg_ra_app('testing', config)

        # Add test user to whitelist
        with self.app.app_context():
            self.app.user_db._coll.insert_one({'eppn': self.test_user_eppn})

        self.client = self.app.test_client()
        self.auth_env = {'HTTP_EPPN': self.test_user_eppn}
        super(SeLegRATests, self).setUp()

    def tearDown(self):
        super(SeLegRATests, self).tearDown()
        with self.app.app_context():
            self.app.user_db._drop_whole_collection()
            self.app.proofing_log._drop_whole_collection()

    @classmethod
    def tearDownClass(cls):
        cls.mongo_instance.shutdown()
        super(SeLegRATests, cls).tearDownClass()

    def test_index_not_logged_in(self):
        rv = self.client.get('/')
        self.assertEqual(rv.status_code, 403)

    def test_index_logged_in(self):
        rv = self.client.get('/', environ_base=self.auth_env)
        self.assertEqual(rv.status_code, 200)

    def test_id_card(self):
        end_point = '/id-card'
        rv = self.client.get(end_point, environ_base=self.auth_env)
        self.assertEqual(rv.status_code, 200)

        # Blank form
        rv = self.client.post(end_point, environ_base=self.auth_env, data={'csrf_token': 'bogus token'})
        self.assertEqual(rv.status_code, 200)
        self.assertIn(str.encode(input_validator.message), rv.data)

        # Invalid form input
        rv = self.client.post(end_point, environ_base=self.auth_env,
                              data={'qr_code': 'test', 'nin': 'test', 'csrf_token': 'bogus token'})
        self.assertEqual(rv.status_code, 200)
        self.assertIn(str.encode(qr_validator.message), rv.data)
        self.assertIn(str.encode(nin_validator.message), rv.data)

        # Valid form input
        qr_code = '1{"token": "a_token", "nonce": "a_nonce"}'
        nin = '190001021234'
        rv = self.client.post(end_point, environ_base=self.auth_env, data={'qr_code': qr_code, 'nin': nin,
                                                                           'ocular_validation': True,
                                                                           'csrf_token': 'bogus token'})

        self.assertEqual(rv.status_code, 200)
        self.assertIn(str.encode('Verifiering mottagen'), rv.data)
        self.assertEqual(self.app.proofing_log.db_count(), 1)

    def test_drivers_license(self):
        end_point = '/drivers-license'
        rv = self.client.get(end_point, environ_base=self.auth_env)
        self.assertEqual(rv.status_code, 200)

        # Blank form
        rv = self.client.post(end_point, environ_base=self.auth_env, data={'csrf_token': 'bogus token'})
        self.assertEqual(rv.status_code, 200)
        self.assertIn(str.encode(input_validator.message), rv.data)

        # Invalid form input
        rv = self.client.post(end_point, environ_base=self.auth_env,
                              data={'qr_code': 'test', 'nin': 'test', 'csrf_token': 'bogus token'})
        self.assertEqual(rv.status_code, 200)
        self.assertIn(str.encode(qr_validator.message), rv.data)
        self.assertIn(str.encode(nin_validator.message), rv.data)

        # Valid form input
        qr_code = '1{"token": "a_token", "nonce": "a_nonce"}'
        nin = '190001021234'
        rv = self.client.post(end_point, environ_base=self.auth_env, data={'qr_code': qr_code, 'nin': nin,
                                                                           'ocular_validation': True,
                                                                           'csrf_token': 'bogus token'})

        self.assertEqual(rv.status_code, 200)
        self.assertIn(str.encode('Verifiering mottagen'), rv.data)
        self.assertEqual(self.app.proofing_log.db_count(), 1)

    def test_passport(self):
        end_point = '/passport'
        rv = self.client.get(end_point, environ_base=self.auth_env)
        self.assertEqual(rv.status_code, 200)

        # Blank form
        rv = self.client.post(end_point, environ_base=self.auth_env, data={'csrf_token': 'bogus token'})
        self.assertEqual(rv.status_code, 200)
        self.assertIn(str.encode(input_validator.message), rv.data)

        # Invalid form input
        rv = self.client.post(end_point, environ_base=self.auth_env,
                              data={'qr_code': 'test', 'nin': 'test', 'passport_number': 'test',
                                    'csrf_token': 'bogus token'})
        self.assertEqual(rv.status_code, 200)
        self.assertIn(str.encode(qr_validator.message), rv.data)
        self.assertIn(str.encode(nin_validator.message), rv.data)
        self.assertIn(str.encode(passport_number_validator.message), rv.data)

        # Valid form input
        qr_code = '1{"token": "a_token", "nonce": "a_nonce"}'
        nin = '190001021234'
        rv = self.client.post(end_point, environ_base=self.auth_env, data={'qr_code': qr_code, 'nin': nin,
                                                                           'passport_number': '12345678',
                                                                           'ocular_validation': True,
                                                                           'csrf_token': 'bogus token'})

        self.assertEqual(rv.status_code, 200)
        self.assertIn(str.encode('Verifiering mottagen'), rv.data)
        self.assertEqual(self.app.proofing_log.db_count(), 1)
