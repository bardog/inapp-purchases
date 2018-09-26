# coding: utf-8
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession
from inapp_purchases.inapp_service import InAppService
from inapp_purchases.subscription_status import SubscriptionStatus

class GooglePlayService(InAppService):
    scopes = ['https://www.googleapis.com/auth/androidpublisher']
    base_uri = 'https://www.googleapis.com/androidpublisher/v3/applications'
    products_uri = '/%packageName%/inappproducts'
    product_purchase_uri = '/%packageName%/purchases/products/%productId%/tokens/%token%'
    subscription_purchase_uri = '/%packageName%/purchases/subscriptions/%subscriptionId%/'+\
                                'tokens/%token%'

    service_account_info = None
    service_account_file = None
    credentials = None
    authed_session = None
    package_name = None

    def __init__(self, service_account_info=None, service_account_file=None,
                 package_name=None, scopes=None, base_uri=None, products_uri=None,
                 product_purchase_uri=None, subscription_purchase_uri=None):
        if scopes is not None:
            self.scopes = scopes
        if base_uri is not None:
            self.base_uri = base_uri
        if products_uri is not None:
            self.products_uri = products_uri
        if product_purchase_uri is not None:
            self.product_purchase_uri = product_purchase_uri
        if subscription_purchase_uri is not None:
            self.subscription_purchase_uri = subscription_purchase_uri
        if service_account_info is not None:
            self.service_account_info = service_account_info
        if service_account_file is not None:
            self.service_account_file = service_account_file
        if package_name is not None:
            self.package_name = package_name
        if self.service_account_info is not None or self.service_account_file is not None:
            self.authed_session = self.create_session()

    def set_service_account_info(self, service_account_info):
        self.service_account_info = service_account_info
        return self

    def set_service_account_file(self, service_account_file):
        self.service_account_file = service_account_file
        return self

    def generate_credentials(self):
        if self.service_account_info is not None:
            self.credentials = service_account.Credentials.from_service_account_info(
                self.service_account_info,
                scopes=self.scopes
            )
        elif self.service_account_file is not None:
            self.credentials = service_account.Credentials.from_service_account_file(
                self.service_account_file,
                scopes=self.scopes
            )
        return self.credentials

    def create_session(self):
        if self.credentials is None:
            self.credentials = self.generate_credentials()
        if self.credentials is not None:
            self.authed_session = AuthorizedSession(self.credentials)
            return self.authed_session
        if not self.authed_session:
            self.authed_session = None
        return self.authed_session

    def refresh_session(self):
        self.authed_session = self.create_session()

    def close_session(self):
        return self.authed_session.close()

    def get_products(self, package_name=None):
        package_name = package_name if package_name is not None else self.package_name
        response = self.request(
            self.base_uri+self.products_uri.replace('%packageName%', package_name)
        )
        return self.get_products_response(response)

    def get_product_purchase(self, product_id, token, package_name=None):
        package_name = package_name if package_name is not None else self.package_name
        response = self.request(
            self.base_uri+
            self.product_purchase_uri
            .replace('%packageName%', package_name)
            .replace('%productId%', product_id)
            .replace('%token%', token)
        )
        return self.get_product_response(response)

    def get_subscription_purchase(self, subscription_id, token, package_name=None):
        package_name = package_name if package_name is not None else self.package_name
        response = self.request(
            self.base_uri+
            self.subscription_purchase_uri
            .replace('%packageName%', package_name)
            .replace('%subscriptionId%', subscription_id)
            .replace('%token%', token)
        )
        return self.get_subscription_response(
            response, additional_data={
                'package_name': package_name,
                'subscription_id': subscription_id
            }
        )

    def request(self, query):
        if self.authed_session is not None:
            response = self.authed_session.get(query)
            return response
        else:
            raise BaseException("authed_session is not defined")

    def get_products_response(self, response, additional_data=None):
        data = None
        if response.ok:
            data = response.json()['inappproduct']
        return super(GooglePlayService, self).get_products_response(response, data)

    def get_product_response(self, response, additional_data=None):
        data = None
        if response.ok:
            data = response.json()
        return super(GooglePlayService, self).get_product_response(response, data)

    def get_subscription_response(self, response, additional_data=None):
        data = None
        try:
            if response.ok:
                response_data = response.json()
                cancellation_date_ms = (int(response_data['userCancellationTimeMillis'])
                                        if 'userCancellationTimeMillis' in response_data
                                        else None)
                cancellation_date = (int(cancellation_date_ms/1000)
                                    if cancellation_date_ms is not None
                                    else None)
                expires_date_ms = (int(response_data['expiryTimeMillis'])
                                if 'expiryTimeMillis' in response_data
                                else None)
                expires_date = (int(expires_date_ms/1000)
                                if expires_date_ms is not None
                                else None)
                cancellation_reason = (response_data['cancelReason']
                                    if 'cancelReason' in response_data
                                    else None)
                payment_state = (response_data['paymentState']
                                if 'paymentState' in response_data
                                else None)
                payment_state = (response_data['paymentState']
                                if 'paymentState' in response_data
                                else None)
                if cancellation_reason is None:
                    status = SubscriptionStatus.ACTIVE
                elif cancellation_reason is not None:
                    status = SubscriptionStatus.CANCELLED
                is_active = status == SubscriptionStatus.ACTIVE
                data = {
                    'purchase_id': response_data['orderId'],
                    'original_purchase_id': response_data['orderId'],
                    'purchase_date_ms': int(response_data['startTimeMillis']),
                    'purchase_date': int(int(response_data['startTimeMillis'])/1000),
                    'original_purchase_date_ms': int(response_data['startTimeMillis']),
                    'original_purchase_date': int(int(response_data['startTimeMillis'])/1000),
                    'auto_renewing': response_data['autoRenewing'],
                    'expires_date_ms': expires_date_ms,
                    'expires_date': expires_date,
                    'country_code': response_data['countryCode'],
                    'price_currency_code': response_data['priceCurrencyCode'],
                    'price_amount': float(int(int(response_data['priceAmountMicros'])/1000)/100),
                    'cancellation_date_ms': cancellation_date_ms,
                    'cancellation_date': cancellation_date,
                    'cancellation_reason': cancellation_reason,
                    'payment_state': payment_state,
                    'status': status,
                    'is_active': is_active,
                    'is_trial_period': None,
                    'expiration_intent': None
                }
                if additional_data is not None:
                    if 'package_name' in additional_data:
                        data.update({
                            'bundle_id': additional_data['package_name']
                        })
                    if 'subscription_id' in additional_data:
                        data.update({
                            'subscription_id': additional_data['subscription_id']
                        })
            return super(GooglePlayService, self).get_subscription_response(response, data)
        except Exception:
            return super(GooglePlayService, self).get_subscription_response(response)
