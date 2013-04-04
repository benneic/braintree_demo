# -*- coding: utf-8 -*-
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import app

import unittest

import braintree


class SubscriptionsTestCases(unittest.TestCase):

    def setUp(self):
        super(SubscriptionsTestCases, self).setUp()

        self.app = app.app.test_client()

    def test_webhook_post(self):

        signature, payload = braintree.WebhookTesting.sample_notification(
            braintree.WebhookNotification.Kind.SubscriptionWentPastDue,
            "123123123"
        )

        response = self.app.post('/webhook',
                                 data={
                                     'bt_signature': signature,
                                     'bt_payload': payload
                                 }
        )
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
