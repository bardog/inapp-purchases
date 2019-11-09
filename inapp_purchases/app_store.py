# coding: utf-8

import json
import logging
import requests
import string
from inapp_purchases.inapp_service import InAppService
from inapp_purchases.subscription_status import SubscriptionStatus

class AppStoreService(InAppService):
    base_sandbox_uri = 'https://sandbox.itunes.apple.com/verifyReceipt'
    base_production_uri = 'https://buy.itunes.apple.com/verifyReceipt'

    sandbox = None
    password = None
    exclude_old_transactions = None

    def __init__(self, sandbox=False, password=None, exclude_old_transactions=None,
                 base_sandbox_uri=None, base_production_uri=None):
        self.sandbox = sandbox
        self.password = password
        self.exclude_old_transactions = exclude_old_transactions
        if base_sandbox_uri is not None:
            self.base_sandbox_uri = base_sandbox_uri
        if base_production_uri is not None:
            self.base_production_uri = base_production_uri

    def get_products(self):
        raise NotImplementedError('get_products method is not implemented.')

    def get_product_purchase(self, receipt_data, password=None, exclude_old_transactions=None,
                             sandbox=None):
        password = password if password is not None else self.password
        exclude_old_transactions = (exclude_old_transactions
                                    if exclude_old_transactions is not None
                                    else self.exclude_old_transactions)
        query = {
            'receipt-data': receipt_data,
        }
        if password is not None:
            query.update({
                'password': password
            })
        if exclude_old_transactions is not None:
            query.update({
                'exclude-old-transactions': exclude_old_transactions
            })
        response = self.request(query=query, sandbox=sandbox)
        return self.get_product_response(response)

    def get_subscription_purchase(self, receipt_data, password=None, exclude_old_transactions=None,
                                  sandbox=None):
        logging.info(('receipt_data', receipt_data))
        password = password if password is not None else self.password
        sandbox = sandbox if sandbox is not None else self.sandbox
        exclude_old_transactions = (exclude_old_transactions
                                    if exclude_old_transactions is not None
                                    else self.exclude_old_transactions)
        query = {
            'receipt-data': string.strip(receipt_data)
        }
        if password is not None:
            query.update({
                'password': password
            })
        if exclude_old_transactions is not None:
            query.update({
                'exclude-old-transactions': exclude_old_transactions
            })
        response = self.request(query=query, sandbox=sandbox)
        return self.get_subscription_response(response)

    def request(self, query, sandbox):
        sandbox = sandbox if sandbox is not None else self.sandbox
        if sandbox:
            request_url = self.base_sandbox_uri
        else:
            request_url = self.base_production_uri
        return requests.post(request_url, data=json.dumps(query))

    def get_products_response(self, response, additional_data=None):
        data = None
        if response.ok:
            data = response.json()
        return super(AppStoreService, self).get_products_response(response, data)

    def get_product_response(self, response, additional_data=None):
        data = None
        if response.ok:
            data = response.json()
        return super(AppStoreService, self).get_product_response(response, data)

    def get_subscription_response(self, response, additional_data=None):
        data = None
        try:
            if response.ok:
                raw_data = response.json()
                logging.info(('raw_data', raw_data))

                if 'latest_receipt_info' not in raw_data:
                    raise Exception(response)

                response_data = raw_data['latest_receipt_info'][0]
                response_status = int(raw_data['status'])
                purchase_id = response_data['transaction_id']
                original_purchase_id = response_data['original_transaction_id']
                purchase_date_ms = int(response_data['purchase_date_ms'])
                purchase_date = int(purchase_date_ms/1000)
                original_purchase_date_ms = int(response_data['original_purchase_date_ms'])
                original_purchase_date = int(original_purchase_date_ms/1000)
                auto_renewing = int(raw_data['pending_renewal_info'][0]['auto_renew_status'] == 1) if 'pending_renewal_info' in raw_data else 0
                cancellation_date_ms = (response_data['cancellation_date']
                                        if 'cancellation_date' in response_data
                                        else None)
                cancellation_reason = (response_data['cancellation_reason']
                                    if 'cancellation_reason' in response_data
                                    else None)
                expiration_intent = (response_data['expiration_intent']
                                    if 'expiration_intent' in response_data
                                    else None)
                expires_date_ms = (int(response_data['expires_date_ms'])
                                if 'expires_date' in response_data
                                else None)
                expires_date = (int(expires_date_ms/1000)
                                if expires_date_ms is not None
                                else None)
                
                if expiration_intent is None and response_status == 0:
                    status = SubscriptionStatus.ACTIVE
                elif expiration_intent is not None:
                    if expiration_intent == 1:
                        status = SubscriptionStatus.CANCELLED
                    elif expiration_intent >= 2 and expiration_intent <= 4:
                        status = SubscriptionStatus.CUSTOM
                    elif response_status == 21006:
                        status = SubscriptionStatus.EXPIRED
                    else:
                        status = SubscriptionStatus.UNKNOWN
                elif response_status == 21006:
                    status = SubscriptionStatus.EXPIRED
                elif response_status == 21005:
                    status = SubscriptionStatus.ACTIVE
                else:
                    status = SubscriptionStatus.UNKNOWN
                is_active = status == SubscriptionStatus.ACTIVE
                bundle_id = raw_data['receipt']['bundle_id']
                subscription_id = response_data['product_id']
                is_trial_period = response_data['is_trial_period']
                
                data = {
                    'purchase_id': purchase_id,
                    'original_purchase_id': original_purchase_id,
                    'purchase_date_ms': purchase_date_ms,
                    'purchase_date': purchase_date,
                    'original_purchase_date_ms': original_purchase_date_ms,
                    'original_purchase_date': original_purchase_date,
                    'auto_renewing': auto_renewing,
                    'expires_date_ms': expires_date_ms,
                    'expires_date': expires_date,
                    'country_code': None,
                    'price_currency_code': None,
                    'price_amount': None,
                    'cancellation_date_ms': cancellation_date_ms,
                    'cancellation_reason': cancellation_reason,
                    'payment_state': None,
                    'status': status,
                    'is_active': is_active,
                    'bundle_id': bundle_id,
                    'subscription_id': subscription_id,
                    'is_trial_period': is_trial_period,
                    'expiration_intent': expiration_intent
                }
            return super(AppStoreService, self).get_subscription_response(response, data)
        except Exception:
            logging.exception(Exception)
            return super(AppStoreService, self).get_subscription_response(response)
