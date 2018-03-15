# -*- coding: utf-8 -*-

from __future__ import absolute_import

from unittest import TestCase
from se_leg_ra.app import init_se_leg_ra_app

__author__ = 'lundberg'


class SeLegRATests(TestCase):
    """Base TestCase for those tests that need a full environment setup"""

    def setUp(self):
        config = {
            'SERVER_NAME': 'localhost',
            'SECRET_KEY': 'testing',
            'TESTING': True
        }
        self.app = init_se_leg_ra_app('testing', config)
        self.client = self.app.test_client()
        super(SeLegRATests, self).setUp()

    def tearDown(self):
        super(SeLegRATests, self).tearDown()
        #with self.app.app_context():
        #    self.app.central_userdb._drop_whole_collection()

    def test_index(self):
        rv = self.client.get('/')
        self.assertEqual(rv.status_code, 200)

