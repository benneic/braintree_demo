# -*- coding: utf-8 -*-

import os

MERCHANT_ID = os.environ['MERCHANT_ID']
PUBLIC_KEY = os.environ['PUBLIC_KEY']
PRIVATE_KEY = os.environ['PRIVATE_KEY']
CLIENT_SIDE_ENCRYPTION_KEY = os.environ['CLIENT_SIDE_ENCRYPTION_KEY']

PLANS = {
    'STORE_59_AUD'     : 'Store Package',
    'FRANCHISE_99_AUD' : 'Franchise Package',
}

