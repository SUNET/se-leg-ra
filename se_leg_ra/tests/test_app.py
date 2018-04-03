# -*- coding: utf-8 -*-

from __future__ import absolute_import

from unittest import TestCase
from mock import patch
from flask import request
from datetime import datetime
from eduid_userdb.testing import MongoTemporaryInstance
from se_leg_ra.app import init_se_leg_ra_app
from se_leg_ra.forms import input_validator, qr_validator, nin_validator, eight_digits_validator, nine_digits_validator

__author__ = 'lundberg'


class MockResponse:
    def __init__(self, status_code):
        self.status_code = status_code


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
            'DB_URI': self.mongo_instance.get_uri(),
            'RA_APP_ID': 'test_ra_app',
            'VETTING_ENDPOINT': 'http://op/vetting-result',
            'WTF_CSRF_ENABLED': False
        }

        self.test_user_eppn = 'test-user@localhost'

        self.app = init_se_leg_ra_app('testing', config)

        # Add test user to whitelist
        with self.app.app_context():
            self.app.user_db._coll.insert_one({'eppn': self.test_user_eppn})

        self.client = self.app.test_client()
        self.auth_env = {'HTTP_EPPN': self.test_user_eppn}
        self.todays_date = datetime.date(datetime.now())
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

    @patch('requests.post')
    def test_id_card(self, mock_requests_post):
        mock_requests_post.return_value = MockResponse(200)

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
                                                                           'expiry_date': str(self.todays_date),
                                                                           'card_number': '12345678',
                                                                           'ocular_validation': True,
                                                                           'csrf_token': 'bogus token'})

        self.assertEqual(rv.status_code, 200)
        self.assertIn(str.encode('Verifiering mottagen'), rv.data)
        self.assertEqual(self.app.proofing_log.db_count(), 1)

    @patch('requests.post')
    def test_drivers_license(self, mock_requests_post):
        mock_requests_post.return_value = MockResponse(200)

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
        self.assertIn(str.encode(nine_digits_validator.message), rv.data)

        # Valid form input
        qr_code = '1{"token": "a_token", "nonce": "a_nonce"}'
        nin = '190001021234'
        rv = self.client.post(end_point, environ_base=self.auth_env, data={'qr_code': qr_code, 'nin': nin,
                                                                           'reference_number': '123456789',
                                                                           'expiry_date': str(self.todays_date),
                                                                           'ocular_validation': True,
                                                                           'csrf_token': 'bogus token'})

        self.assertEqual(rv.status_code, 200)
        self.assertIn(str.encode('Verifiering mottagen'), rv.data)
        self.assertEqual(self.app.proofing_log.db_count(), 1)

    @patch('requests.post')
    def test_passport(self, mock_requests_post):
        mock_requests_post.return_value = MockResponse(200)
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
        self.assertIn(str.encode(eight_digits_validator.message), rv.data)

        # Valid form input
        qr_code = '1{"token": "a_token", "nonce": "a_nonce"}'
        nin = '190001021234'
        rv = self.client.post(end_point, environ_base=self.auth_env, data={'qr_code': qr_code, 'nin': nin,
                                                                           'expiry_date': str(self.todays_date),
                                                                           'passport_number': '12345678',
                                                                           'ocular_validation': True,
                                                                           'csrf_token': 'bogus token'})

        self.assertEqual(rv.status_code, 200)
        self.assertIn(str.encode('Verifiering mottagen'), rv.data)
        self.assertEqual(self.app.proofing_log.db_count(), 1)

    @patch('requests.post')
    def test_national_id_card(self, mock_requests_post):
        mock_requests_post.return_value = MockResponse(200)

        end_point = '/national-id-card'
        rv = self.client.get(end_point, environ_base=self.auth_env)
        self.assertEqual(rv.status_code, 200)

        # Blank form
        rv = self.client.post(end_point, environ_base=self.auth_env, data={'csrf_token': 'bogus token'})
        self.assertEqual(rv.status_code, 200)
        self.assertIn(str.encode(input_validator.message), rv.data)

        # Invalid form input
        rv = self.client.post(end_point, environ_base=self.auth_env,
                              data={'qr_code': 'test', 'nin': 'test', 'card_number': 'test',
                                    'csrf_token': 'bogus token'})
        self.assertEqual(rv.status_code, 200)

        self.assertIn(str.encode(qr_validator.message), rv.data)
        self.assertIn(str.encode(nin_validator.message), rv.data)
        self.assertIn(str.encode(eight_digits_validator.message), rv.data)

        # Valid form input
        qr_code = '1{"token": "a_token", "nonce": "a_nonce"}'
        nin = '190001021234'
        rv = self.client.post(end_point, environ_base=self.auth_env, data={'qr_code': qr_code, 'nin': nin,
                                                                           'expiry_date': str(self.todays_date),
                                                                           'card_number': '12345678',
                                                                           'ocular_validation': True,
                                                                           'csrf_token': 'bogus token'})

        self.assertEqual(rv.status_code, 200)
        self.assertIn(str.encode('Verifiering mottagen'), rv.data)
        self.assertEqual(self.app.proofing_log.db_count(), 1)
